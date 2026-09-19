import asyncio

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

import config
import database
import keyboards
import upcoming
from middlewares.subscription import check_user_sub

router = Router()

WELCOME = (
    "👋 Salom! Kino botga xush kelibsiz.\n\n"
    "🎬 Kino kodini yuboring yoki pastdagi menyudan tanlang 👇\n\n"
    "🔎 Nom yozsangiz ham topib beraman."
)


async def _need_sub(msg: Message, user_id: int | None = None) -> bool:
    """True = obuna yo'q, xabar yuborildi."""
    uid = user_id or msg.from_user.id
    ok, _ = await check_user_sub(msg.bot, uid)
    if ok:
        return False
    await msg.answer(
        "📢 Davom etish uchun kanal(lar)ga obuna bo'ling:",
        reply_markup=keyboards.sub_keyboard(),
    )
    return True


async def _deliver(msg: Message, code: str, user_id: int | None = None) -> None:
    uid = user_id or msg.from_user.id
    movie = await database.get_movie(code)
    if not movie:
        results = await database.search_movies(code, limit=10)
        if not results:
            await msg.answer("❌ Bunday kod topilmadi. Nomini yozib qidirib ko'ring.")
            return
        lines = [f"<code>{r['code']}</code> — {r['title'] or '-'} " for r in results]
        await msg.answer("🔎 O'xshashlar:\n" + "\n".join(lines) + "\n\nKodini yuboring.")
        return
    if await _need_sub(msg, uid):
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
    await database.log_request(uid, code)


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
    await msg.answer(WELCOME, reply_markup=keyboards.main_menu())
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


@router.message(F.text == "🎬 Kino qidirish")
async def menu_search(msg: Message):
    await msg.answer("🔎 Kino nomi yoki kodini yozing:")


@router.message(F.text == "🎲 Kino tanla")
async def menu_mood(msg: Message):
    await msg.answer(
        "🧠 <b>Bugun nimani ko'ramiz?</b>\nKayfiyatni tanlang:",
        reply_markup=keyboards.mood_keyboard(),
    )


@router.message(F.text == "🔥 Trending")
async def menu_trending(msg: Message):
    rows = await database.get_top(10)
    if not rows:
        await msg.answer("Hali kino qo'shilmagan.")
        return
    lines = [
        f"{i+1}. <code>{r['code']}</code> — {r['title'] or '-'} 👁 {r['views']}"
        for i, r in enumerate(rows)
    ]
    await msg.answer("🔥 <b>Trending:</b>\n" + "\n".join(lines))


@router.message(F.text == "⭐ Top reyting")
async def menu_rated(msg: Message):
    rows = await database.get_top_rated(10)
    if not rows:
        await msg.answer("Hali kino qo'shilmagan.")
        return
    lines = [
        f"{i+1}. <code>{r['code']}</code> — {r['title'] or '-'} 👍 {r['likes']}"
        for i, r in enumerate(rows)
    ]
    await msg.answer("⭐ <b>Top reyting:</b>\n" + "\n".join(lines))


@router.message(F.text == "📅 Yangi filmlar")
async def menu_new(msg: Message):
    rows = await database.get_new_movies(10)
    if rows:
        lines = [f"<code>{r['code']}</code> — {r['title'] or '-'}" for r in rows]
        await msg.answer("🆕 <b>Botdagi yangilar:</b>\n" + "\n".join(lines))
    else:
        await msg.answer("Botda hali kino yo'q.")
    await msg.answer(
        "📅 <b>Kino kalendari</b> — premyeralar:",
        reply_markup=keyboards.cal_keyboard(),
    )


@router.message(F.text == "📚 Mening ro'yxatim")
async def menu_mylist(msg: Message):
    rows = await database.wl_list(msg.from_user.id)
    if not rows:
        await msg.answer(
            "📚 Ro'yxatingiz bo'sh.\nKino ostidagi 📌 Saqlash tugmasini bosing."
        )
        return
    await msg.answer(
        "📚 <b>Mening kinolarim:</b>",
        reply_markup=keyboards.watchlist_keyboard(rows),
    )


@router.message(F.text == "🎰 Kino Roulette")
async def menu_roulette(msg: Message):
    if await _need_sub(msg):
        return
    movie = await database.get_random_movie()
    if not movie:
        await msg.answer("Hali kino qo'shilmagan.")
        return
    m = await msg.answer("🎰 <b>RULETKA</b> aylanmoqda...")
    for t in ("3...", "2...", "1... 🎬"):
        await asyncio.sleep(0.7)
        try:
            await m.edit_text(f"🎰 <b>RULETKA</b>\n{t}")
        except Exception:
            break
    await asyncio.sleep(0.5)
    try:
        await m.delete()
    except Exception:
        pass
    await _deliver(msg, movie["code"])


@router.callback_query(F.data.startswith("mood:"))
async def cb_mood(call: CallbackQuery):
    _, _, key = call.data.partition(":")
    label = database.MOODS.get(key, key)
    rows = await database.get_movies_by_mood(key)
    if not rows:
        await call.message.answer(
            f"{label} bo'yicha hali kino qo'shilmagan."
        )
    else:
        lines = [
            f"<code>{r['code']}</code> — {r['title'] or '-'} 👁 {r['views']}"
            for r in rows
        ]
        await call.message.answer(
            f"{label} kinolar:\n" + "\n".join(lines) + "\n\nKodini yuboring."
        )
    await call.answer()


@router.callback_query(F.data.startswith("get:"))
async def cb_get(call: CallbackQuery):
    _, _, code = call.data.partition(":")
    await call.answer()
    await _deliver(call.message, code, user_id=call.from_user.id)


@router.callback_query(F.data.startswith("save:"))
async def cb_save(call: CallbackQuery):
    _, _, code = call.data.partition(":")
    await database.wl_add(call.from_user.id, code)
    await call.answer("📌 Saqlandi! 📚 Mening ro'yxatim da ko'rasiz.")


@router.callback_query(F.data.startswith("wldel:"))
async def cb_wldel(call: CallbackQuery):
    _, _, code = call.data.partition(":")
    await database.wl_remove(call.from_user.id, code)
    rows = await database.wl_list(call.from_user.id)
    try:
        if not rows:
            await call.message.edit_text("📚 Ro'yxatingiz bo'sh.")
        else:
            await call.message.edit_text(
                "📚 <b>Mening kinolarim:</b>",
                reply_markup=keyboards.watchlist_keyboard(rows),
            )
    except Exception:
        pass
    await call.answer("O'chirildi 🗑")


@router.callback_query(F.data.startswith("cal:"))
async def cb_cal(call: CallbackQuery):
    _, _, per = call.data.partition(":")
    if per == "today":
        rows, title = upcoming.get_today(), "📌 Bugun chiqadiganlar"
    elif per == "week":
        rows, title = upcoming.get_week(), "🗓 Shu hafta"
    elif per == "month":
        rows, title = upcoming.get_month(), "📆 Shu oy"
    else:
        rows, title = upcoming.get_year(2027), "🎞 2027-yil filmlari"
    body = upcoming.fmt(rows) or "— bu davrda premyera topilmadi."
    await call.message.answer(
        f"{title}:\n{body}\n\n<i>Sanalar jahon premyerasi (taxminiy).</i>"
    )
    await call.answer()


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
