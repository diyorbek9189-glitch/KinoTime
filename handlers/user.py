from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

import config
import database
import keyboards
from middlewares.subscription import check_user_sub

router = Router()

WELCOME = (
    "👋 Salom! Kino botga xush kelibsiz.\n\n"
    "🎬 Kino kodini yuboring (masalan: <b>12</b>)\n"
    "🔎 Yoki kino nomini yozing — qidirib beraman.\n\n"
    "Buyruqlar:\n"
    "/random — tasodifiy kino\n"
    "/top — eng ko'p ko'rilganlar\n"
    "/help — yordam"
)


async def _need_sub(msg: Message) -> bool:
    """True = obuna yo'q, xabar yuborildi."""
    ok, _ = await check_user_sub(msg.bot, msg.from_user.id)
    if ok:
        return False
    await msg.answer(
        "📢 Davom etish uchun kanal(lar)ga obuna bo'ling:",
        reply_markup=keyboards.sub_keyboard(),
    )
    return True


async def _deliver(msg: Message, code: str) -> None:
    movie = await database.get_movie(code)
    if not movie:
        results = await database.search_movies(code, limit=10)
        if not results:
            await msg.answer("❌ Bunday kod topilmadi. Nomini yozib qidirib ko'ring.")
            return
        lines = [f"<code>{r['code']}</code> — {r['title'] or '-'} " for r in results]
        await msg.answer("🔎 O'xshashlar:\n" + "\n".join(lines) + "\n\nKodini yuboring.")
        return
    if await _need_sub(msg):
        return
    try:
        await msg.bot.copy_message(
            chat_id=msg.chat.id,
            from_chat_id=movie["chat_id"],
            message_id=movie["message_id"],
            caption=f"🎬 {movie['title'] or ''}\n🔑 Kod: {movie['code']}".strip(),
            reply_markup=keyboards.movie_keyboard(
                movie["code"], movie.get("likes", 0), movie.get("dislikes", 0)
            ),
        )
    except Exception:
        await msg.answer("⚠️ Kinoni yuborib bo'lmadi. Bot guruhda a'zo/admin ekanini tekshiring.")
        return
    await database.inc_views(code)
    await database.log_request(msg.from_user.id, code)


@router.message(CommandStart())
async def cmd_start(msg: Message):
    ref = 0
    code = None
    if msg.text:
        parts = msg.text.split(maxsplit=1)
        if len(parts) > 1:
            arg = parts[1].strip()
            if arg.startswith("ref_"):
                try:
                    ref = int(arg[4:])
                except ValueError:
                    ref = 0
            else:
                code = arg
    await database.add_user(msg.from_user.id, ref)
    await msg.answer(WELCOME)
    if code:
        await _deliver(msg, code)


@router.message(Command("help"))
async def cmd_help(msg: Message):
    await msg.answer(WELCOME)


@router.message(Command("random"))
async def cmd_random(msg: Message):
    if await _need_sub(msg):
        return
    movie = await database.get_random_movie()
    if not movie:
        await msg.answer("Hali kino qo'shilmagan.")
        return
    await _deliver(msg, movie["code"])


@router.message(Command("top"))
async def cmd_top(msg: Message):
    rows = await database.get_top(10)
    if not rows:
        await msg.answer("Hali kino qo'shilmagan.")
        return
    lines = [
        f"{i+1}. <code>{r['code']}</code> — {r['title'] or '-'} 👁 {r['views']}"
        for i, r in enumerate(rows)
    ]
    await msg.answer("🔥 Top 10:\n" + "\n".join(lines))


@router.callback_query(F.data == "check_sub")
async def cb_check_sub(call: CallbackQuery):
    ok, _ = await check_user_sub(call.bot, call.from_user.id)
    if ok:
        await call.message.delete()
        await call.message.answer("✅ Obuna tasdiqlandi! Endi kino kodini yuboring.")
    else:
        await call.answer("❌ Hali obuna bo'lmagansiz!", show_alert=True)


@router.callback_query(F.data.startswith(("like:", "dislike:")))
async def cb_vote(call: CallbackQuery):
    action, _, code = call.data.partition(":")
    field = "likes" if action == "like" else "dislikes"
    await database.vote(code, field)
    movie = await database.get_movie(code)
    if movie and call.message:
        try:
            await call.message.edit_reply_markup(
                reply_markup=keyboards.movie_keyboard(
                    code, movie.get("likes", 0), movie.get("dislikes", 0)
                )
            )
        except Exception:
            pass
    await call.answer("Rahmat! ✅")


@router.message(F.text)
async def on_text(msg: Message):
    text = (msg.text or "").strip()
    if not text or text.startswith("/"):
        return
    # Kod bo'lsa aniq topadi, bo'lmasa nom bo'yicha qidiradi
    movie = await database.get_movie(text)
    if movie:
        await _deliver(msg, text)
        return
    results = await database.search_movies(text, limit=10)
    if results:
        lines = [f"<code>{r['code']}</code> — {r['title'] or '-'}" for r in results]
        await msg.answer("🔎 Topildi:\n" + "\n".join(lines) + "\n\nKodini yuboring.")
    else:
        await msg.answer("❌ Topilmadi. Kodni to'g'ri yozing yoki /random bosing.")
