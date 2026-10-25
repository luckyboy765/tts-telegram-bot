"""
Bot Teka-Teki Silang (TTS) — entry point.

Fitur:
- 3 mode: Mudah / Normal / Sulit (jumlah & kesulitan kata berbeda).
- Papan crossword dirakit acak tiap game dari bank soal → variasi tak terbatas.
- Jawab dengan ketik "<nomor> <jawaban>" (spasi/titik opsional): 3. gula / 3gula.
- Skor & poin ala Family 100; peringkat global & mingguan.
- Gambar papan otomatis berubah & terisi tiap ada jawaban benar
  (pola render mengikuti bot Ular Tangga / Dam-daman).
"""
import asyncio
import io
import os
import pickle
import logging

logging.basicConfig(level=logging.INFO)

from pyrogram import Client, filters
from pyrogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
)

from config import API_ID, API_HASH, BOT_TOKEN, OWNER_IDS, GAME_TIMEOUT, LOG_GROUP
import stats
import game as G
from words import count_by_tier
from renderer import render
from generator import ACROSS

app = Client("tts_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Registry sesi aktif per chat
SESSIONS = {}

# Persistensi sesi agar game tidak hilang saat bot restart/di-deploy
_SESS_FILE = os.path.join(os.path.dirname(__file__), "sessions.pkl")


def _save_sessions():
    try:
        with open(_SESS_FILE, "wb") as f:
            pickle.dump(SESSIONS, f)
    except Exception as e:
        logging.warning("Gagal simpan sesi: %s", e)


def _load_sessions() -> dict:
    if not os.path.exists(_SESS_FILE):
        return {}
    try:
        with open(_SESS_FILE, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        logging.warning("Gagal muat sesi: %s", e)
        return {}


# ─────────────────────────── util ───────────────────────────

def _photo(data: bytes):
    bio = io.BytesIO(data)
    bio.name = "tts.png"
    return bio


async def _del(client, chat_id, msg_id):
    """Hapus pesan bila ada, abaikan error."""
    if not msg_id:
        return
    try:
        await client.delete_messages(chat_id, msg_id)
    except Exception:
        pass


def _progress_bar(done: int, total: int, slots: int = 10) -> str:
    if total <= 0:
        return "▱" * slots
    filled = round(slots * done / total)
    return "▰" * filled + "▱" * (slots - filled)


HAIR = "━━━━━━━━━━━━━━━"

MODE_INFO = {
    "easy":      ("🟢", "Mudah", "6 kata", "kosakata sehari-hari"),
    "normal":    ("🟡", "Normal", "9 kata", "pengetahuan umum"),
    "hard":      ("🔴", "Sulit", "13 kata", "istilah, sains & teknologi"),
    "nightmare": ("💀", "Nightmare", "18 kata", "sangat sulit — istilah langka"),
}

PICK_TEXT = (
    "🧩 <b>TEKA-TEKI SILANG</b> 🧩\n"
    f"<code>{HAIR}</code>\n"
    "Susun kata bersilangan, tebak jawaban, kumpulkan poin, "
    "dan naik peringkat! 🏆\n\n"
    "🎚 <b>Pilih tingkat kesulitan:</b>\n\n"
    "🟢 <b>Mudah</b> — 6 kata · kata sehari-hari\n"
    "🟡 <b>Normal</b> — 9 kata · pengetahuan umum\n"
    "🔴 <b>Sulit</b> — 13 kata · istilah & sains\n"
    "💀 <b>Nightmare</b> — 18 kata · sangat sulit!\n\n"
    "💡 Cara jawab: ketik <b>nomor + jawaban</b>, contoh <code>3 gula</code>."
)

HELP_TEXT = (
    "📖 <b>CARA MAIN — Teka-Teki Silang</b>\n"
    f"<code>{HAIR}</code>\n"
    "🧩 Papan berisi kotak-kotak bernomor yang saling bersilangan. "
    "Tiap nomor punya petunjuk di daftar <b>MENDATAR ➡️</b> dan <b>MENURUN ⬇️</b>.\n\n"
    "1️⃣ Ketik /new lalu pilih mode.\n"
    "2️⃣ Baca petunjuk, cari jawabannya.\n"
    "3️⃣ Jawab dengan format <b>nomor + jawaban</b>:\n"
    "     <code>3. gula</code> · <code>3.gula</code> · <code>3 gula</code> · <code>3gula</code>\n"
    "     <i>(spasi/titik opsional — semua terbaca)</i>\n"
    "4️⃣ Jawaban benar ✅ → kotak otomatis terisi & huruf tersorot 🟩.\n"
    "5️⃣ Game selesai saat semua kotak terisi atau waktu habis ⏰.\n\n"
    "💯 <b>Poin</b>: makin panjang kata, makin besar poin "
    "(10 × jumlah huruf) — ala Family 100.\n"
    "🏆 <b>Peringkat</b>: dihitung dari total poin & jumlah jawaban benar.\n"
    "👥 Bisa dimainkan <b>rame-rame</b> — siapa cepat dia dapat!\n\n"
    "⌨️ <b>Perintah:</b> /new · /stop · /peringkat · /stats · /soal · /help"
)


def _mode_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🟢 Mudah", callback_data="tts:mode:easy"),
            InlineKeyboardButton("🟡 Normal", callback_data="tts:mode:normal"),
        ],
        [
            InlineKeyboardButton("🔴 Sulit", callback_data="tts:mode:hard"),
            InlineKeyboardButton("💀 Nightmare", callback_data="tts:mode:nightmare"),
        ],
        [InlineKeyboardButton("📖 Cara Main", callback_data="tts:info")],
    ])


async def _board_bytes(session, highlight=None) -> bytes:
    title = f"TTS · {G.MODE_LABEL.get(session.mode, session.mode)}  " \
            f"({len(session.solved_ids)}/{session.total_words()})"
    return render(session.puzzle, session.solved_cells, highlight, title)


def _reset_timer(client, chat_id):
    session = SESSIONS.get(chat_id)
    if not session:
        return
    if session.timer_task and not session.timer_task.done():
        session.timer_task.cancel()
    session.timer_task = asyncio.create_task(_timeout(client, chat_id))


async def _timeout(client, chat_id):
    try:
        await asyncio.sleep(GAME_TIMEOUT)
    except asyncio.CancelledError:
        return
    session = SESSIONS.get(chat_id)
    if not session or not session.active:
        return
    await _finish(client, chat_id, timed_out=True)


async def _finish(client, chat_id, timed_out=False):
    session = SESSIONS.pop(chat_id, None)
    if not session:
        return
    _save_sessions()
    session.active = False
    if session.timer_task and not session.timer_task.done():
        session.timer_task.cancel()

    # Hapus papan & soal terakhir agar hanya hasil akhir yang tersisa
    await _del(client, chat_id, session.last_board_id)
    await _del(client, chat_id, session.last_clue_id)

    G.reveal_all(session)
    data = await _board_bytes(session)

    # Catat statistik persisten
    if session.players:
        stats.record_games(list(session.players.values()))
    winners = []
    if session.scores:
        top = max(d["points"] for d in session.scores.values())
        winners = [uid for uid, d in session.scores.items() if d["points"] == top]
        stats.record_wins(winners)

    if timed_out:
        head = "⏰ <b>WAKTU HABIS!</b>\nJawaban yang tersisa dibuka semua. 👇\n"
    else:
        head = "🎉🎉 <b>SELESAI — SEMUA TERJAWAB!</b> 🎉🎉\n"
    caption = (
        f"{head}<code>{HAIR}</code>\n"
        f"🏆 <b>HASIL AKHIR</b>\n\n{G.scoreboard(session)}"
    )
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("🔁 Main Lagi", callback_data="tts:menu"),
        InlineKeyboardButton("🏆 Peringkat", callback_data="tts:rank"),
    ]])
    await client.send_photo(chat_id, _photo(data), caption=caption, reply_markup=kb)


# ─────────────────────────── commands ───────────────────────────

@app.on_message(filters.command("start"))
async def on_start(client, message: Message):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 Main Sekarang", callback_data="tts:menu")],
        [InlineKeyboardButton("📖 Cara Main", callback_data="tts:info")],
    ])
    await message.reply(
        "🧩 <b>Selamat datang di TEKA-TEKI SILANG!</b> 🧩\n"
        f"<code>{HAIR}</code>\n"
        "Game asah otak: susun kata bersilangan, tebak jawaban dari "
        "petunjuk, dan rebut posisi teratas di papan peringkat! 🏆\n\n"
        "Tekan <b>🎮 Main Sekarang</b> atau ketik /new untuk mulai.\n"
        "Baru pertama kali? Baca dulu <b>📖 Cara Main</b>.",
        reply_markup=kb,
    )


@app.on_message(filters.command("help"))
async def on_help(client, message: Message):
    await message.reply(HELP_TEXT)


@app.on_message(filters.command(["new", "tts"]) & (filters.group | filters.private))
async def on_new(client, message: Message):
    chat_id = message.chat.id
    if chat_id in SESSIONS:
        await message.reply("⚠️ Masih ada game berjalan. Ketik /stop dulu untuk mengakhiri.")
        return
    await message.reply(PICK_TEXT, reply_markup=_mode_kb())


@app.on_message(filters.command("stop") & (filters.group | filters.private))
async def on_stop(client, message: Message):
    chat_id = message.chat.id
    if chat_id not in SESSIONS:
        await message.reply("Tidak ada game aktif.")
        return
    await _finish(client, chat_id, timed_out=True)


@app.on_message(filters.command(["peringkat", "leaderboard", "lb"]))
async def on_leaderboard(client, message: Message):
    arg = (message.command[1].lower() if len(message.command) > 1 else "")
    kind = "weekly" if arg in ("mingguan", "minggu", "weekly", "week") else "global"
    await message.reply(stats.format_leaderboard(kind, 10))


@app.on_message(filters.command(["stats", "statistik", "profil"]))
async def on_stats(client, message: Message):
    u = message.from_user
    s = stats.user_stats(u.id)
    if not s:
        await message.reply("📊 Kamu belum punya statistik. Main dulu lewat /new!")
        return
    await message.reply(
        f"📊 <b>Statistik {u.first_name}</b>\n\n"
        f"🏅 Total poin: <b>{s['points']}</b>\n"
        f"✅ Jawaban benar: <b>{s['correct']}</b>\n"
        f"🎮 Game dimainkan: <b>{s['games']}</b>\n"
        f"🏆 Menang: <b>{s['wins']}</b>"
    )


@app.on_message(filters.command("backup") & filters.user(list(OWNER_IDS)))
async def on_backup(client, message: Message):
    if not LOG_GROUP:
        await message.reply("LOG_GROUP belum diatur di .env.")
        return
    ok = await do_backup(client)
    await message.reply("✅ Backup terkirim ke grup database." if ok
                        else "⚠️ Backup gagal (cek bot ada di grup & DB ada).")


@app.on_message(filters.command("soal"))
async def on_soal(client, message: Message):
    c = count_by_tier()
    await message.reply(
        "🗂 <b>Bank soal</b>\n"
        f"🟢 Mudah: {c['easy']}\n"
        f"🟡 Normal: {c['normal']}\n"
        f"🔴 Sulit: {c['hard']}\n"
        f"💀 Nightmare: {c['nightmare']}\n"
        f"Σ Total: <b>{sum(c.values())}</b> kata "
        "(dirangkai acak jadi papan berbeda tiap game)."
    )


# ─────────────────────────── callbacks ───────────────────────────

@app.on_callback_query(filters.regex(r"^tts:info$"))
async def on_info(client, callback: CallbackQuery):
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("🎮 Main Sekarang", callback_data="tts:menu")
    ]])
    try:
        await callback.message.edit_text(HELP_TEXT, reply_markup=kb)
    except Exception:
        await client.send_message(callback.message.chat.id, HELP_TEXT, reply_markup=kb)
    await callback.answer()


@app.on_callback_query(filters.regex(r"^tts:menu$"))
async def on_menu(client, callback: CallbackQuery):
    chat_id = callback.message.chat.id
    if chat_id in SESSIONS:
        await callback.answer("Masih ada game berjalan. Ketik /stop dulu.", show_alert=True)
        return
    try:
        await callback.message.edit_text(PICK_TEXT, reply_markup=_mode_kb())
    except Exception:
        await client.send_message(chat_id, PICK_TEXT, reply_markup=_mode_kb())
    await callback.answer()


@app.on_callback_query(filters.regex(r"^tts:rank$"))
async def on_rank(client, callback: CallbackQuery):
    await client.send_message(callback.message.chat.id,
                              stats.format_leaderboard("global", 10))
    await callback.answer()


@app.on_callback_query(filters.regex(r"^tts:mode:"))
async def on_mode(client, callback: CallbackQuery):
    mode = callback.data.split(":")[2]
    chat_id = callback.message.chat.id
    if chat_id in SESSIONS:
        await callback.answer("Sudah ada game berjalan.", show_alert=True)
        return
    await callback.answer("Menyusun papan…")
    session = await asyncio.to_thread(G.new_session, chat_id, mode)
    SESSIONS[chat_id] = session

    try:
        await callback.message.delete()
    except Exception:
        pass

    ic, lbl, wc, desc = MODE_INFO[mode]
    data = await _board_bytes(session)
    board = await client.send_photo(
        chat_id, _photo(data),
        caption=(
            f"🧩 <b>TTS DIMULAI!</b> {ic} <b>{lbl}</b>\n"
            f"<code>{HAIR}</code>\n"
            f"📊 {session.total_words()} kata · {desc}\n"
            f"⏱ Waktu: {GAME_TIMEOUT // 60} menit\n\n"
            f"💬 Jawab dengan <b>nomor + jawaban</b>, mis. <code>3 gula</code>.\n"
            f"Semangat! 🔥"
        ),
    )
    clue = await client.send_message(chat_id, G.clue_text(session))
    session.last_board_id = board.id
    session.last_clue_id = clue.id
    _save_sessions()
    _reset_timer(client, chat_id)


# ─────────────────────────── answers ───────────────────────────

@app.on_message(filters.text & (filters.group | filters.private) & ~filters.via_bot)
async def on_text(client, message: Message):
    text = message.text or ""
    if text.startswith("/"):
        return
    chat_id = message.chat.id
    session = SESSIONS.get(chat_id)
    if not session or not session.active:
        return

    # Sesi baru dipulihkan dari restart? Kirim notif sekarang (peer sudah dikenal).
    if getattr(session, "resume_pending", False):
        await _greet_resume(client, chat_id, session)

    parsed = G.parse_answer(text)
    if not parsed:
        return
    number, answer = parsed

    res = G.submit(session, number, answer)
    if res.status == "unknown_number":
        return  # nomor tak ada — abaikan (mungkin ngobrol biasa)
    if res.status == "wrong":
        return  # salah — diam saja agar tak spam
    if res.status == "already":
        return  # sudah terjawab

    # BENAR
    u = message.from_user
    session.register_player(u)
    G.add_score(session, u, res.points)
    stats.record_answer(u.id, u.first_name or "Pemain", u.username or "", res.points)

    p = res.placement
    data = await _board_bytes(session, highlight=set(p.cells()))
    arah = "Mendatar ➡️" if p.direction == ACROSS else "Menurun ⬇️"
    done = len(session.solved_ids)
    total = session.total_words()
    bar = _progress_bar(done, total)
    name = (u.first_name or "Pemain").replace("<", "&lt;").replace(">", "&gt;")

    # Hapus papan & soal lama biar chat tidak menumpuk (ala Ular Tangga)
    await _del(client, chat_id, session.last_board_id)
    await _del(client, chat_id, session.last_clue_id)
    session.last_board_id = session.last_clue_id = 0

    board = await client.send_photo(
        chat_id, _photo(data),
        caption=(
            f"✅ <b>{name}</b> benar! <b>+{res.points} poin</b> 🎯\n"
            f"<b>{p.number} {arah}</b> — <b>{p.word}</b>\n"
            f"{bar}  {done}/{total}"
        ),
    )
    session.last_board_id = board.id

    if session.is_complete():
        await _finish(client, chat_id, timed_out=False)
    else:
        # kirim ulang sisa soal supaya tak perlu scroll ke atas
        clue = await client.send_message(chat_id, G.clue_text(session, only_remaining=True))
        session.last_clue_id = clue.id
        _save_sessions()
        _reset_timer(client, chat_id)


# ─────────────────────────── backup ───────────────────────────

async def do_backup(client) -> bool:
    """Kirim file DB statistik ke grup database (LOG_GROUP)."""
    if not LOG_GROUP:
        return False
    db_path = stats._DB_PATH
    if not os.path.exists(db_path):
        return False
    try:
        from datetime import datetime
        cap = f"🗄 Backup statistik TTS — {datetime.now():%Y-%m-%d %H:%M}"
        await client.send_document(LOG_GROUP, db_path, caption=cap)
        return True
    except Exception as e:
        logging.warning("Backup gagal: %s", e)
        return False


async def backup_loop(client):
    """Backup otomatis tiap 24 jam."""
    while True:
        await asyncio.sleep(24 * 3600)
        await do_backup(client)


# ─────────────────────────── startup ───────────────────────────

async def _restore_sessions():
    """Pulihkan game yang berjalan setelah restart — TANPA kirim pesan di sini.
    Sesaat setelah start, Pyrogram belum mengenal peer (Peer id invalid), jadi
    notifikasi ditunda: dikirim saat pesan pertama masuk dari chat itu (lihat
    on_text), ketika peer sudah dikenal."""
    restored = _load_sessions()
    n = 0
    for chat_id, session in restored.items():
        if not getattr(session, "active", False):
            continue
        session.resume_pending = True
        SESSIONS[chat_id] = session
        _reset_timer(app, chat_id)
        n += 1
    if n:
        logging.info("Memulihkan %d sesi game (notif ditunda sampai pesan masuk).", n)
    _save_sessions()


async def _greet_resume(client, chat_id, session):
    """Kirim notif 'game dilanjutkan' sekali, saat peer sudah dikenal."""
    session.resume_pending = False
    try:
        await client.send_message(
            chat_id,
            "♻️ Bot sempat diperbarui — <b>game dilanjutkan!</b>\n"
            f"Progres: {len(session.solved_ids)}/{session.total_words()}. "
            "Lanjut jawab seperti biasa. 🧩",
        )
        clue = await client.send_message(chat_id, G.clue_text(session, only_remaining=True))
        session.last_clue_id = clue.id
        _save_sessions()
    except Exception as e:
        logging.warning("Gagal kirim notif lanjut sesi %s: %s", chat_id, e)


async def main():
    stats.init_db()
    await app.start()
    c = count_by_tier()
    print(f"✅ Bot TTS jalan! Bank soal: {sum(c.values())} kata "
          f"(easy {c['easy']}, normal {c['normal']}, hard {c['hard']}, "
          f"nightmare {c['nightmare']}).", flush=True)
    await _restore_sessions()
    if LOG_GROUP:
        asyncio.create_task(backup_loop(app))
    await asyncio.Event().wait()


if __name__ == "__main__":
    app.run(main())
