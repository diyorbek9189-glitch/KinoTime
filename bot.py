import asyncio
import logging
import os
import sys

if sys.platform == "win32":
    # Windows konsolida emoji (✅⚠️) chop etishda crash bo'lmasligi uchun
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiohttp import web

import config
import database
from handlers import admin as admin_handlers
from handlers import user as user_handlers

logging.basicConfig(level=logging.INFO)


async def _health_server() -> None:
    """Render free da uyquga ketmaslik uchun: UptimeRobot shu manzilni pinglaydi."""
    async def ok(request: web.Request) -> web.Response:
        return web.Response(text="ok")

    app = web.Application()
    app.router.add_get("/", ok)
    app.router.add_get("/health", ok)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", "8080"))
    await web.TCPSite(runner, "0.0.0.0", port).start()
    print(f"🌐 Health: :{port}/health")


async def main() -> None:
    if not config.BOT_TOKEN or ":" not in config.BOT_TOKEN:
        print("❌ .env da BOT_TOKEN yo'q yoki noto'g'ri.")
        return
    await database.init_db()

    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(admin_handlers.router)
    dp.include_router(user_handlers.router)

    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Boshlash"),
            BotCommand(command="random", description="Tasodifiy kino"),
            BotCommand(command="top", description="Top kinolar"),
            BotCommand(command="help", description="Yordam"),
        ]
    )

    me = await bot.get_me()
    print(f"✅ Bot ishga tushdi: @{me.username}")
    if config.STORAGE_CHAT_ID is None:
        print("⚠️ STORAGE_CHAT_ID bo'sh. Botni guruhga admin qilib, guruhda /id yuboring.")
    if not config.ADMIN_IDS:
        print("⚠️ ADMIN_IDS bo'sh. Lichkada /myid yuborib, ID ni .env ga yozing.")
    try:
        await asyncio.gather(
            dp.start_polling(bot),
            _health_server(),
        )
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
