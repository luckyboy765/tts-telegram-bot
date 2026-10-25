"""
game.py — State per-chat, parser jawaban, dan penilaian TTS.

Cara jawab: ketik "<nomor> <jawaban>". Contoh: `3. gula`, `3.gula`,
`3 gula`, atau `3gula` — spasi/titik antara nomor dan jawaban opsional,
semuanya tetap terbaca.
"""
import re
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from generator import Puzzle, Placement, ACROSS, generate, MODE_WORDS
from words import by_tier

MODE_LABEL = {"easy": "Mudah", "normal": "Normal", "hard": "Sulit",
              "nightmare": "Nightmare"}

# Pola: angka di depan, lalu pemisah opsional (. ) - : spasi), lalu jawaban.
_ANS_RE = re.compile(r"^\s*(\d{1,3})\s*[.\)\-:_]*\s*([A-Za-z][A-Za-z\s]*)\s*$")


def parse_answer(text: str) -> Optional[Tuple[int, str]]:
    """Ubah 'ketikan' jadi (nomor, jawaban_bersih_UPPER). None bila bukan jawaban."""
    if not text:
        return None
    m = _ANS_RE.match(text)
    if not m:
        return None
    number = int(m.group(1))
    ans = re.sub(r"[^A-Za-z]", "", m.group(2)).upper()
    if not ans:
        return None
    return number, ans


def word_points(word: str) -> int:
    """Poin sebuah kata — makin panjang makin besar (ala Family 100)."""
    return len(word) * 10


@dataclass
class GameSession:
    chat_id: int
    mode: str
    puzzle: Puzzle
    active: bool = True
    solved_ids: Set[int] = field(default_factory=set)          # index placement
    solved_cells: Dict[Tuple[int, int], str] = field(default_factory=dict)
    scores: Dict[int, dict] = field(default_factory=dict)      # user_id -> data
    players: Dict[int, dict] = field(default_factory=dict)     # peserta
    number_map: Dict[int, List[int]] = field(default_factory=dict)  # nomor -> [idx]
    started: float = field(default_factory=time.time)
    timer_task: object = None
    last_board_id: int = 0    # id pesan papan terakhir (untuk dihapus)
    last_clue_id: int = 0     # id pesan daftar soal terakhir
    resume_pending: bool = False  # true sesudah restore, kirim notif saat pesan pertama

    def build_index(self):
        for idx, p in enumerate(self.puzzle.placements):
            self.number_map.setdefault(p.number, []).append(idx)

    def total_words(self) -> int:
        return len(self.puzzle.placements)

    def is_complete(self) -> bool:
        return len(self.solved_ids) >= self.total_words()

    def register_player(self, user):
        self.players[user.id] = {
            "user_id": user.id,
            "name": user.first_name or "Pemain",
            "username": user.username or "",
        }

    # Agar bisa di-pickle (persist antar restart): buang timer_task yang
    # tidak bisa diserialisasi.
    def __getstate__(self):
        d = self.__dict__.copy()
        d["timer_task"] = None
        return d

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.timer_task = None


def new_session(chat_id: int, mode: str) -> GameSession:
    entries = by_tier(mode)
    puzzle = generate(entries, MODE_WORDS.get(mode, 8))
    s = GameSession(chat_id=chat_id, mode=mode, puzzle=puzzle)
    s.build_index()
    return s


@dataclass
class AnswerResult:
    status: str                    # correct / already / wrong / unknown_number
    placement: Optional[Placement] = None
    points: int = 0
    new_cells: Set[Tuple[int, int]] = field(default_factory=set)


def submit(session: GameSession, number: int, answer: str) -> AnswerResult:
    """Proses satu jawaban terhadap nomor tertentu."""
    idxs = session.number_map.get(number)
    if not idxs:
        return AnswerResult("unknown_number")

    # Cek tiap placement dengan nomor itu (bisa ada Mendatar & Menurun)
    for idx in idxs:
        p = session.puzzle.placements[idx]
        if p.word == answer:
            if idx in session.solved_ids:
                return AnswerResult("already", p)
            session.solved_ids.add(idx)
            new_cells = set()
            for (r, c) in p.cells():
                if (r, c) not in session.solved_cells:
                    new_cells.add((r, c))
                session.solved_cells[(r, c)] = session.puzzle.grid[(r, c)]
            return AnswerResult("correct", p, word_points(p.word), new_cells)

    # Nomor ada tapi jawaban salah (atau sudah semua terjawab benar)
    all_solved = all(i in session.solved_ids for i in idxs)
    if all_solved:
        return AnswerResult("already", session.puzzle.placements[idxs[0]])
    return AnswerResult("wrong", session.puzzle.placements[idxs[0]])


def add_score(session: GameSession, user, points: int):
    """Tambah poin pemain di skor game ini."""
    d = session.scores.get(user.id)
    if not d:
        d = {"user_id": user.id, "name": user.first_name or "Pemain",
             "username": user.username or "", "points": 0, "correct": 0}
        session.scores[user.id] = d
    d["points"] += points
    d["correct"] += 1
    d["name"] = user.first_name or d["name"]
    d["username"] = user.username or d["username"]


def clue_text(session: GameSession, only_remaining: bool = False) -> str:
    """Daftar petunjuk MENDATAR / MENURUN.
    only_remaining=True → hanya tampilkan yang BELUM terjawab (sisa soal)."""
    solved_idx = session.solved_ids
    idx_of = {id(p): i for i, p in enumerate(session.puzzle.placements)}

    def line(p: Placement, idx: int) -> str:
        if idx in solved_idx:
            return f"✅ <b>{p.number}.</b> <s>{p.clue}</s> → <b>{p.word}</b>"
        return f"🔲 <b>{p.number}.</b> {p.clue} <i>({len(p.word)} huruf)</i>"

    def section(header: str, items) -> list:
        rows = []
        for p in items:
            idx = idx_of[id(p)]
            if only_remaining and idx in solved_idx:
                continue
            rows.append(line(p, idx))
        if not rows:
            rows = ["<i>— semua terjawab 🎉</i>"]
        return [header] + rows

    total = session.total_words()
    done = len(solved_idx)
    head = ("📝 <b>SISA SOAL</b>" if only_remaining else "🧩 <b>DAFTAR SOAL</b>")
    out = [f"{head}  ·  <b>{done}/{total}</b> terisi", ""]
    out += section("➡️ <b>MENDATAR</b>", session.puzzle.across())
    out.append("")
    out += section("⬇️ <b>MENURUN</b>", session.puzzle.down())
    out.append("")
    out.append("💬 Jawab: <code>nomor jawaban</code> — mis. <code>3 gula</code>")
    return "\n".join(out)


def scoreboard(session: GameSession) -> str:
    if not session.scores:
        return "Belum ada yang menjawab benar."
    rows = sorted(session.scores.values(),
                  key=lambda d: (d["points"], d["correct"]), reverse=True)
    out = []
    for i, d in enumerate(rows, 1):
        medal = ["🥇", "🥈", "🥉"][i - 1] if i <= 3 else f"{i}."
        name = d["name"].replace("<", "&lt;").replace(">", "&gt;")
        uname = f" (@{d['username']})" if d["username"] else ""
        out.append(f"{medal} {name}{uname} — <b>{d['points']}</b> poin · {d['correct']} benar")
    return "\n".join(out)


def reveal_all(session: GameSession):
    """Buka semua sel (untuk saat game berakhir)."""
    for (r, c), ch in session.puzzle.grid.items():
        session.solved_cells[(r, c)] = ch
