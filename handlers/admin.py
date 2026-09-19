from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

import config
import database

router = Router()


class AddMovie(StatesGroup):
    waiting_media = State()


def _parse_add_args(text: str) -> tuple[str, str]:
    """'/add 12 Titanic' -> ('12', 'Titanic'). '|' ham qo'llanadi."""
    parts = text.split(maxsplit=2)
    # parts[0] = /add, parts[1] = kod, parts[2] = nom (ixtiyoriy)
    if len(parts) < 2:
        return "", ""
    code = parts[1].replace("|", "").strip()
    title = parts[2].replace("|", " ").strip() if len(parts) > 2 else ""
    return code, title


@router.message(Command("id"))
async def cmd_id(msg: Message):
    # Guruhda ham, lichkada ham chat ID ni ko'rsatadi.
    await msg.reply(f"chat_id: <code>{msg.chat.id}</code>\nuser_id: <code>{msg.from_user.id}</code>")


@router.message(Command("myid"))
async def cmd_myid(msg: Message):
    await msg.reply(f"Sizning ID: <code>{msg.from_user.id}</code>")


@router.message(Command("add"))
async def cmd_add(msg: Message, state: FSMContext):
    if not config.is_admin(msg.from_user.id):
        await msg.reply("⛔ Siz admin emassiz. /myid ni adminlarga yuboring.")
        return
    code, title = _parse_add_args(msg.text or "")
    replied = msg.reply_to_message

    # 1-usul: guruhdagi kinoga reply qilib /add 12 Nom
    if replied and (replied.video or replied.document):
        if not code:
            await msg.reply("Kod yozing: kino xabariga reply qilib\n<code>/add 12 Kino nomi</code>")
            return
        await database.add_movie(code, replied.chat.id, replied.message_id, title)
        await msg.reply(f"✅ Saqlandi!\nKod: <b>{code}</b>\nNom: {title or '-'}")
        return

    # 2-usul: lichkada /add 12 Nom -> keyin video yuborish (FSM)
    if not code:
        await msg.reply(
            "Foydalanish:\n"
            "1) Guruhga kino yuboring, o'sha xabarga reply qilib:\n"
            "<code>/add 12 Titanic 1998</code>\n\n"
            "2) Yoki lichkada: <code>/add 12 Titanic</code> deb yozing, keyin kinoni shu yerga yuboring."
        )
        return
    await state.update_data(code=code, title=title)
    await state.set_state(AddMovie.waiting_media)
    await msg.reply(
        f"Kod: <b>{code}</b> qabul qilindi.\nEndi kino videosini (video/document) shu chatga yuboring."
    )


@router.message(AddMovie.waiting_media, F.video | F.document)
async def add_media_received(msg: Message, state: FSMContext):
    if not config.is_admin(msg.from_user.id):
        await state.clear()
        return
    data = await state.get_data()
    code = data.get("code", "")
    title = data.get("title", "")
    # Lichkada yuborilgan bo'lsa ham o'sha chat/message dan copy qilamiz.
    # Tavsiya: guruh ID ishlatish uchun kinoni guruhga yuboring.
    await database.add_movie(code, msg.chat.id, msg.message_id, title)
    await state.clear()
    await msg.reply(f"✅ Saqlandi!\nKod: <b>{code}</b>\nNom: {title or '-'}")


@router.message(Command("del"))
async def cmd_del(msg: Message):
    if not config.is_admin(msg.from_user.id):
        return
    parts = (msg.text or "").split(maxsplit=1)
    if len(parts) < 2:
        await msg.reply("Foydalanish: <code>/del 12</code>")
        return
    ok = await database.delete_movie(parts[1].strip())
    await msg.reply("🗑 O'chirildi." if ok else "❌ Bunday kod topilmadi.")


@router.message(Command("list"))
async def cmd_list(msg: Message):
    if not config.is_admin(msg.from_user.id):
        return
    rows = await database.list_movies(50)
    if not rows:
        await msg.reply("Hali kino qo'shilmagan.")
        return
    lines = [f"<code>{r['code']}</code> — {r['title'] or '-'} ({r['views']} ko'rish)" for r in rows]
    await msg.reply("🎬 So'nggi 50 ta:\n" + "\n".join(lines))


@router.message(Command("stat"))
async def cmd_stat(msg: Message):
    if not config.is_admin(msg.from_user.id):
        return
    s = await database.get_stats()
    top = "\n".join(f"{c}: {n} marta" for c, n in s["top_req"]) or "-"
    await msg.reply(
        f"📊 Statistika\n\n"
        f"👥 Userlar: {s['users']}\n"
        f"🎬 Kinolar: {s['movies']}\n"
        f"📩 So'rovlar: {s['requests']}\n\n"
        f"🔥 Top so'rovlar:\n{top}"
    )
