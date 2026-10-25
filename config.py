"""
Konfigurasi bot TTS (Teka-Teki Silang).
Isi lewat file .env atau environment variable.
"""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Multi owner: pisah dengan spasi/koma. Contoh: OWNER_ID=123456 789012
OWNER_IDS = set(
    int(x) for x in os.getenv("OWNER_ID", "0").replace(",", " ").split()
    if x.strip().isdigit()
)
OWNER_ID = next(iter(OWNER_IDS), 0)

# Berapa detik game otomatis berakhir bila tidak ada yang menjawab (tebak sisa)
GAME_TIMEOUT = int(os.getenv("GAME_TIMEOUT", "600"))

# Grup/channel "database" untuk backup file statistik (id -100...). 0 = nonaktif.
LOG_GROUP = int(os.getenv("LOG_GROUP", "0"))
