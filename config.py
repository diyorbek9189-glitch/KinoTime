import os
from dotenv import load_dotenv

load_dotenv()


def _parse_ids(raw: str) -> list[int]:
    out: list[int] = []
    for part in (raw or "").split(","):
        part = part.strip().lstrip("@")
        if not part:
            continue
        try:
            out.append(int(part))
        except ValueError:
            pass  # username bo'lsa FORCE_CHANNELS da string sifatida ishlatiladi
    return out


def _parse_channels(raw: str) -> list[str]:
    out: list[str] = []
    for part in (raw or "").split(","):
        part = part.strip()
        if part:
            out.append(part)
    return out


BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
ADMIN_IDS: list[int] = _parse_ids(os.getenv("ADMIN_IDS", ""))

_storage_raw = (os.getenv("STORAGE_CHAT_ID", "") or "").strip()
try:
    STORAGE_CHAT_ID: int | None = int(_storage_raw) if _storage_raw else None
except ValueError:
    STORAGE_CHAT_ID = None

FORCE_CHANNELS: list[str] = _parse_channels(os.getenv("FORCE_CHANNELS", ""))
RECOMMEND_CHANNEL: str = (os.getenv("RECOMMEND_CHANNEL", "") or "").strip()
RECOMMEND_URL: str = (os.getenv("RECOMMEND_URL", "") or "").strip()

DB_PATH: str = os.path.join(os.path.dirname(__file__), "kino.db")


def is_admin(user_id: int) -> bool:
    # ADMIN_IDS bo'sh bo'lsa: birinchi sozlash oson bo'lishi uchun hech kim admin emas.
    # /myid orqali ID ni olib .env ga yozing.
    return user_id in ADMIN_IDS
