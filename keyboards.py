from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import config


def sub_keyboard() -> InlineKeyboardMarkup:
    rows = []
    for ch in config.FORCE_CHANNELS:
        url_ch = ch if ch.startswith("@") else ch
        # @username -> https://t.me/username, ID bo'lsa URL siz tugma bo'lmaydi
        if url_ch.startswith("@"):
            url = f"https://t.me/{url_ch[1:]}"
        else:
            url = f"https://t.me/{url_ch}"
        rows.append([InlineKeyboardButton(text=f"📢 {ch} — Obuna bo'lish", url=url)])
    rows.append([InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_sub")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def movie_keyboard(code: str, likes: int = 0, dislikes: int = 0) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(text=f"👍 {likes}", callback_data=f"like:{code}"),
            InlineKeyboardButton(text=f"👎 {dislikes}", callback_data=f"dislike:{code}"),
        ]
    ]
    if config.RECOMMEND_URL:
        rows.append(
            [InlineKeyboardButton(text="🔥 Yangi kinolar kanali", url=config.RECOMMEND_URL)]
        )
    elif config.RECOMMEND_CHANNEL:
        ch = config.RECOMMEND_CHANNEL
        url = f"https://t.me/{ch[1:]}" if ch.startswith("@") else f"https://t.me/{ch}"
        rows.append([InlineKeyboardButton(text="🔥 Yangi kinolar kanali", url=url)])
    return InlineKeyboardMarkup(inline_keyboard=rows)
