from aiogram import Bot

import config


async def check_user_sub(bot: Bot, user_id: int) -> tuple[bool, list[str]]:
    """Majburiy kanallarga obunani tekshiradi. (True, []) = hammasi OK."""
    if not config.FORCE_CHANNELS:
        return True, []
    missing: list[str] = []
    for ch in config.FORCE_CHANNELS:
        try:
            m = await bot.get_chat_member(chat_id=ch, user_id=user_id)
            if m.status in ("left", "kicked"):
                missing.append(ch)
        except Exception:
            # Kanal topilmasa yoki bot admin bo'lmasa — to'sib qo'ymaymiz, o'tkazamiz
            continue
    return (len(missing) == 0), missing
