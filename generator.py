"""
Generator papan Teka-Teki Silang.

Mengambil sejumlah kata dari bank lalu menyusunnya menjadi papan yang saling
bersilangan (crossword) memakai algoritma penempatan bertetangga:

- Kata pertama diletakkan di tengah (mendatar).
- Kata berikutnya hanya boleh ditempatkan bila memotong huruf yang sama pada
  kata yang sudah ada (minimal 1 persilangan) dan tidak menabrak/menempel kata
  lain secara tidak sah.
- Nomor petunjuk diberikan dengan memindai sel awal tiap kata (urut baca).

Hasil: objek Puzzle dengan daftar penempatan + nomor + arah (D/T).
"""
import random
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

# Arah
ACROSS = "A"  # Mendatar (D pada tampilan)
DOWN = "D"    # Menurun (T pada tampilan)


@dataclass
class Placement:
    word: str
    clue: str
    row: int
    col: int
    direction: str          # ACROSS / DOWN
    number: int = 0

    def cells(self) -> List[Tuple[int, int]]:
        if self.direction == ACROSS:
            return [(self.row, self.col + i) for i in range(len(self.word))]
        return [(self.row + i, self.col) for i in range(len(self.word))]


@dataclass
class Puzzle:
    placements: List[Placement]
    grid: Dict[Tuple[int, int], str]      # (r,c) -> huruf jawaban benar
    min_row: int
    min_col: int
    height: int
    width: int
    number_at: Dict[Tuple[int, int], int] = field(default_factory=dict)

    def across(self) -> List[Placement]:
        return sorted([p for p in self.placements if p.direction == ACROSS],
                      key=lambda p: p.number)

    def down(self) -> List[Placement]:
        return sorted([p for p in self.placements if p.direction == DOWN],
                      key=lambda p: p.number)


def _fits(grid, word, row, col, direction) -> bool:
    """Cek apakah word muat di (row,col) arah direction tanpa konflik."""
    intersections = 0
    if direction == ACROSS:
        # sel sebelum & sesudah harus kosong
        if (row, col - 1) in grid:
            return False
        if (row, col + len(word)) in grid:
            return False
        for i, ch in enumerate(word):
            r, c = row, col + i
            cur = grid.get((r, c))
            if cur is not None:
                if cur != ch:
                    return False
                intersections += 1
            else:
                # sel baru: tetangga atas/bawah harus kosong
                if (r - 1, c) in grid or (r + 1, c) in grid:
                    return False
    else:  # DOWN
        if (row - 1, col) in grid:
            return False
        if (row + len(word), col) in grid:
            return False
        for i, ch in enumerate(word):
            r, c = row + i, col
            cur = grid.get((r, c))
            if cur is not None:
                if cur != ch:
                    return False
                intersections += 1
            else:
                if (r, c - 1) in grid or (r, c + 1) in grid:
                    return False
    return intersections >= 1


def _place(grid, word, row, col, direction):
    for i, ch in enumerate(word):
        if direction == ACROSS:
            grid[(row, col + i)] = ch
        else:
            grid[(row + i, col)] = ch


def _try_build(entries: List[Tuple[str, str]], max_words: int) -> List[Placement]:
    """Coba susun satu papan. Kembalikan daftar placement (bisa < max_words)."""
    grid: Dict[Tuple[int, int], str] = {}
    placements: List[Placement] = []

    # Kata pertama di tengah, mendatar
    first_word, first_clue = entries[0]
    _place(grid, first_word, 0, 0, ACROSS)
    placements.append(Placement(first_word, first_clue, 0, 0, ACROSS))

    for word, clue in entries[1:]:
        if len(placements) >= max_words:
            break
        placed = False
        # Titik kandidat: tiap huruf word cocok dengan tiap sel terisi
        candidates = []
        for i, ch in enumerate(word):
            for (r, c), gch in grid.items():
                if gch != ch:
                    continue
                # coba tegak lurus terhadap arah kata pemilik sel — cukup coba
                # kedua arah, _fits yang menyaring.
                # word DOWN memotong di baris r,kolom c: start = (r - i, c)
                candidates.append((r - i, c, DOWN))
                # word ACROSS memotong di baris r,kolom c: start = (r, c - i)
                candidates.append((r, c - i, ACROSS))
        random.shuffle(candidates)
        for (rr, cc, direction) in candidates:
            if _fits(grid, word, rr, cc, direction):
                _place(grid, word, rr, cc, direction)
                placements.append(Placement(word, clue, rr, cc, direction))
                placed = True
                break
        # kalau tak dapat tempat, lewati kata ini (coba kata berikutnya)
        _ = placed
    return placements


def _finalize(placements: List[Placement]) -> Puzzle:
    grid: Dict[Tuple[int, int], str] = {}
    for p in placements:
        _place(grid, p.word, p.row, p.col, p.direction)

    rows = [r for (r, _) in grid]
    cols = [c for (_, c) in grid]
    min_row, max_row = min(rows), max(rows)
    min_col, max_col = min(cols), max(cols)

    # Penomoran: sel yang menjadi awal kata across dan/atau down
    starts = sorted({(p.row, p.col) for p in placements})
    number_at: Dict[Tuple[int, int], int] = {}
    n = 0
    # urut baca: baris lalu kolom
    for (r, c) in sorted(starts):
        n += 1
        number_at[(r, c)] = n
    for p in placements:
        p.number = number_at[(p.row, p.col)]

    return Puzzle(
        placements=placements,
        grid=grid,
        min_row=min_row,
        min_col=min_col,
        height=max_row - min_row + 1,
        width=max_col - min_col + 1,
        number_at=number_at,
    )


def generate(entries: List[Tuple[str, str]], target_words: int,
             attempts: int = 40) -> Puzzle:
    """
    Susun papan dari daftar (jawaban, petunjuk).
    Mengulang beberapa kali dan memilih papan dengan kata terbanyak & terpadat.
    """
    pool = [(w.upper(), c) for (w, c) in entries if w.isalpha()]
    best: List[Placement] = []
    best_score = -1

    for _ in range(attempts):
        random.shuffle(pool)
        # kata panjang duluan → papan lebih rapat & saling silang
        ordered = sorted(pool, key=lambda x: len(x[0]), reverse=True)
        # sedikit acak supaya tak selalu sama
        head = ordered[: target_words * 2]
        random.shuffle(head)
        ordered = head + ordered[target_words * 2:]

        placements = _try_build(ordered, target_words)
        if len(placements) < 2:
            continue
        # skor: jumlah kata + jumlah persilangan (semakin banyak makin bagus)
        tmp_grid: Dict[Tuple[int, int], int] = {}
        cross = 0
        for p in placements:
            for cell in p.cells():
                tmp_grid[cell] = tmp_grid.get(cell, 0) + 1
        cross = sum(1 for v in tmp_grid.values() if v > 1)
        score = len(placements) * 10 + cross
        if score > best_score:
            best_score = score
            best = placements
        if len(placements) >= target_words:
            # cukup bagus, tapi teruskan sedikit demi kepadatan
            if cross >= target_words - 1:
                break

    if not best:
        # fallback: minimal satu kata
        w, c = pool[0]
        best = [Placement(w, c, 0, 0, ACROSS)]
    return _finalize(best)


# Parameter tiap mode: (jumlah kata target)
MODE_WORDS = {
    "easy": 6,
    "normal": 9,
    "hard": 13,
    "nightmare": 18,
}
