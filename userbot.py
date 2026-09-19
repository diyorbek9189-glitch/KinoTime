"""Test akkaunt userboti (Telethon).

Telegram Desktop YOPIIQ bo'lsa ham ishlaydi — API orqali ulanadi.
Sessiya `test_session.session` faylida saqlanadi, qayta kod so'ralmaydi.

Birinchi ishga tushirish (o'zing terminalda bajarasan, menga kod yuborma):
  1. .env ga API_ID, API_HASH, PHONE ni yoz
  2. python userbot.py
  3. Telefoningga kelgan kodni + 2FA parolni (bo'lsa) terminalga yoz

Keyin fonda ishlatish:
  pythonw userbot.py
Log: userbot.log

Buyruqlar (istalgan chatda o'zing yozasan, nuqta bilan):
  .ping              — userbot tirikligini tekshirish
  .id                — shu chat ID si
  .test 1            — botga "1" kodini yuborib javobni ko'rsatish
  .yubor @user matn  — ko'rsatilgan chatga xabar yuborish
"""
import asyncio
import logging
import os

from dotenv import load_dotenv
from telethon import TelegramClient, events

load_dotenv()

logging.basicConfig(
    filename="userbot.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

API_ID = int(os.getenv("API_ID", "0") or 0)
API_HASH = (os.getenv("API_HASH", "") or "").strip()
PHONE = (os.getenv("PHONE", "") or "").strip()
BOT_USERNAME = "kino_vaqti_kino_time_bot"

client = TelegramClient("test_session", API_ID, API_HASH)


@client.on(events.NewMessage(pattern=r"^\.ping$", outgoing=True))
async def ping_handler(event):
    await event.edit("pong ✅ userbot ishlayapti (Desktop shart emas)")


@client.on(events.NewMessage(pattern=r"^\.id$", outgoing=True))
async def id_handler(event):
    await event.edit(f"chat_id: `{event.chat_id}`")


@client.on(events.NewMessage(pattern=r"^\.test", outgoing=True))
async def test_handler(event):
    parts = event.text.split(maxsplit=1)
    kod = parts[1].strip() if len(parts) > 1 else "1"
    await event.edit(f"⏳ Botga `{kod}` yuborilmoqda...")
    try:
        async with client.conversation(BOT_USERNAME, timeout=30) as conv:
            await conv.send_message(kod)
            resp = await conv.get_response()
            matn = resp.text or resp.caption or "(media javob)"
            await event.edit(f"🤖 Bot javobi (`{kod}`):\n{matn[:500]}")
    except Exception as e:
        logging.exception("test xatosi")
        await event.edit(f"❌ Xato: {e}")


@client.on(events.NewMessage(pattern=r"^\.yubor", outgoing=True))
async def send_handler(event):
    parts = event.text.split(maxsplit=2)
    if len(parts) < 3:
        await event.edit("Foydalanish: `.yubor @user xabar matni`")
        return
    try:
        await client.send_message(parts[1], parts[2])
        await event.edit(f"✅ Yuborildi → {parts[1]}")
    except Exception as e:
        logging.exception("yuborish xatosi")
        await event.edit(f"❌ Xato: {e}")


async def main():
    if not API_ID or not API_HASH:
        print("❌ .env da API_ID / API_HASH yo'q.")
        print("   my.telegram.org → API development tools → Create app")
        return
    await client.start(phone=PHONE or None)
    me = await client.get_me()
    print(f"✅ Userbot ulandi: {me.first_name} (id={me.id})")
    print("Buyruqlar: .ping .id .test <kod> .yubor <chat> <matn>")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
