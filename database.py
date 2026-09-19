import aiosqlite
import time

import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS movies(
  code TEXT PRIMARY KEY,
  chat_id INTEGER NOT NULL,
  message_id INTEGER NOT NULL,
  title TEXT DEFAULT '',
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
"""


async def init_db() -> None:
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.executescript(SCHEMA)
        await db.commit()


async def add_movie(code: str, chat_id: int, message_id: int, title: str = "") -> None:
    code = code.strip()
    async with aiosqlite.connect(config.DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO movies(code, chat_id, message_id, title, created_at) "
            "VALUES(?, ?, ?, ?, ?)",
            (code, chat_id, message_id, title.strip(), int(time.time())),
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
