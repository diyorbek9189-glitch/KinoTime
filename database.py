import aiosqlite
import time

import config

# Kayfiyat -> kalit. /add da mood shu kalitlardan biri bilan beriladi.
MOODS = {
    "drama": "😢 Yig'latadigan",
    "komediya": "😂 Kuldiradigan",
    "horror": "😱 Qo'rqinchli",
    "romantik": "❤️ Romantik",
    "aqlli": "🧠 Miyani portlatadigan",
    "action": "🔥 Action",
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS movies(
  code TEXT PRIMARY KEY,
  chat_id INTEGER NOT NULL,
  message_id INTEGER NOT NULL,
  title TEXT DEFAULT '',
  mood TEXT DEFAULT '',
  year INTEGER DEFAULT 0,
  views INTEGER DEFAULT 0,
  likes INTEGER DEFAULT 0,
  dislikes INTEGER DEFAULT 0,
  created_at INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS users(
  user_id INTEGER PRIMARY KEY,
  joined_at INTEGER DEFAULT 0,
  ref_from INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS requests(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  code TEXT,
  created_at INTEGER
);
CREATE TABLE IF NOT EXISTS watchlist(
  user_id INTEGER NOT NULL,
  code TEXT NOT NULL,
  added_at INTEGER DEFAULT 0,
  PRIMARY KEY(user_id, code)
);
"""

_MIGRATIONS = [
    "ALTER TABLE movies ADD COLUMN mood TEXT DEFAULT ''",
    "ALTER TABLE movies ADD COLUMN year INTEGER DEFAULT 0",
]


async def init_db() -> None:
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.executescript(SCHEMA)
        for sql in _MIGRATIONS:
            try:
                await db.execute(sql)
            except Exception:
                pass  # ustun allaqachon bor
        await db.commit()


async def add_movie(
    code: str,
    chat_id: int,
    message_id: int,
    title: str = "",
    mood: str = "",
    year: int = 0,
) -> None:
    code = code.strip()
    mood = (mood or "").strip().lower()
    if mood not in MOODS:
        mood = ""
    try:
        year = int(year or 0)
    except (TypeError, ValueError):
        year = 0
    async with aiosqlite.connect(config.DB_PATH) as db:
        # Qayta qo'shishda statistika va berilmagan maydonlarni saqlaymiz
        views = likes = dislikes = 0
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT mood, year, views, likes, dislikes FROM movies WHERE code=?", (code,)
        ) as cur:
            old = await cur.fetchone()
        if old:
            views, likes, dislikes = old["views"], old["likes"], old["dislikes"]
            if not mood:
                mood = old["mood"] or ""
            if not year:
                year = old["year"] or 0
        await db.execute(
            "INSERT OR REPLACE INTO movies(code, chat_id, message_id, title, mood, year, views, likes, dislikes, created_at) "
            "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (code, chat_id, message_id, title.strip(), mood, year,
             views, likes, dislikes, int(time.time())),
        )
        await db.commit()


async def get_movie(code: str):
    code = code.strip()
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM movies WHERE code=?", (code,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def delete_movie(code: str) -> bool:
    async with aiosqlite.connect(config.DB_PATH) as db:
        cur = await db.execute("DELETE FROM movies WHERE code=?", (code.strip(),))
        await db.commit()
        return cur.rowcount > 0


async def list_movies(limit: int = 50):
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT code, title, views FROM movies ORDER BY rowid DESC LIMIT ?", (limit,)
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def search_movies(query: str, limit: int = 10):
    q = f"%{query.strip()}%"
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT code, title, views FROM movies "
            "WHERE code LIKE ? OR title LIKE ? ORDER BY views DESC LIMIT ?",
            (q, q, limit),
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def get_random_movie():
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM movies ORDER BY RANDOM() LIMIT 1"
        ) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def get_top(limit: int = 10):
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT code, title, views FROM movies ORDER BY views DESC LIMIT ?", (limit,)
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def get_movies_by_mood(mood: str, limit: int = 10):
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT code, title, views, likes FROM movies WHERE mood=? "
            "ORDER BY views DESC LIMIT ?",
            (mood.strip().lower(), limit),
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def get_new_movies(limit: int = 10):
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT code, title, views FROM movies ORDER BY rowid DESC LIMIT ?", (limit,)
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def get_top_rated(limit: int = 10):
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT code, title, likes, views FROM movies ORDER BY likes DESC, views DESC LIMIT ?",
            (limit,),
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def wl_add(user_id: int, code: str) -> None:
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO watchlist(user_id, code, added_at) VALUES(?, ?, ?)",
            (user_id, code.strip(), int(time.time())),
        )
        await db.commit()


async def wl_remove(user_id: int, code: str) -> None:
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute(
            "DELETE FROM watchlist WHERE user_id=? AND code=?", (user_id, code.strip())
        )
        await db.commit()


async def wl_has(user_id: int, code: str) -> bool:
    async with aiosqlite.connect(config.DB_PATH) as db:
        async with db.execute(
            "SELECT 1 FROM watchlist WHERE user_id=? AND code=?", (user_id, code.strip())
        ) as cur:
            return (await cur.fetchone()) is not None


async def wl_list(user_id: int):
    async with aiosqlite.connect(config.DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT m.code, m.title, m.views FROM watchlist w "
            "JOIN movies m ON m.code = w.code "
            "WHERE w.user_id=? ORDER BY w.added_at DESC",
            (user_id,),
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def inc_views(code: str) -> None:
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute("UPDATE movies SET views = views + 1 WHERE code=?", (code.strip(),))
        await db.commit()


async def vote(code: str, field: str) -> None:
    if field not in ("likes", "dislikes"):
        return
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute(f"UPDATE movies SET {field} = {field} + 1 WHERE code=?", (code.strip(),))
        await db.commit()


async def add_user(user_id: int, ref_from: int = 0) -> None:
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users(user_id, joined_at, ref_from) VALUES(?, ?, ?)",
            (user_id, int(time.time()), ref_from),
        )
        await db.commit()


async def log_request(user_id: int, code: str) -> None:
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute(
            "INSERT INTO requests(user_id, code, created_at) VALUES(?, ?, ?)",
            (user_id, code.strip(), int(time.time())),
        )
        await db.commit()


async def get_stats():
    async with aiosqlite.connect(config.DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cur:
            users = (await cur.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM movies") as cur:
            movies = (await cur.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM requests") as cur:
            reqs = (await cur.fetchone())[0]
        async with db.execute(
            "SELECT code, COUNT(*) c FROM requests GROUP BY code ORDER BY c DESC LIMIT 5"
        ) as cur:
            top_req = await cur.fetchall()
        return {"users": users, "movies": movies, "requests": reqs, "top_req": top_req}
