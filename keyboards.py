from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

import config
import database


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
        ],
        [InlineKeyboardButton(text="📌 Saqlash", callback_data=f"save:{code}")],
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


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎬 Kino qidirish"), KeyboardButton(text="🎲 Kino tanla")],
            [KeyboardButton(text="🔥 Trending"), KeyboardButton(text="⭐ Top reyting")],
            [KeyboardButton(text="📅 Yangi filmlar"), KeyboardButton(text="📚 Mening ro'yxatim")],
            [KeyboardButton(text="🎰 Kino Roulette")],
        ],
        resize_keyboard=True,
    )


def mood_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=label, callback_data=f"mood:{key}")]
        for key, label in database.MOODS.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def cal_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📌 Bugun chiqadiganlar", callback_data="cal:today")],
            [InlineKeyboardButton(text="🗓 Shu hafta", callback_data="cal:week")],
            [InlineKeyboardButton(text="📆 Shu oy", callback_data="cal:month")],
            [InlineKeyboardButton(text="🎞 2027-yil filmlari", callback_data="cal:2027")],
        ]
    )


def watchlist_keyboard(rows) -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text=f"🎬 {r['title'] or r['code']}", callback_data=f"get:{r['code']}")]
        for r in rows
    ]
    kb += [
        [InlineKeyboardButton(text=f"❌ {r['code']} ni o'chirish", callback_data=f"wldel:{r['code']}")]
        for r in rows
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)
