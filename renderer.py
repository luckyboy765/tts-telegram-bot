"""
renderer.py — Render papan Teka-Teki Silang jadi gambar PNG (Pillow).

Sel yang belum terjawab: kotak putih kosong (hanya nomor bila awal kata).
Sel yang sudah terjawab: kotak putih berisi huruf jawaban benar.
Kata yang baru saja benar: disorot hijau.

Referensi gaya papan: damdaman-main/renderer.py (kanvas + ImageDraw).
"""
import io
import os
from typing import Dict, Set, Tuple, Optional

from PIL import Image, ImageDraw, ImageFont

from generator import Puzzle

# ── Warna (mirip screenshot: papan navy, garis sel cyan) ──
BG = (23, 32, 56)
CELL_EMPTY = (245, 247, 250)
CELL_SOLVED = (255, 255, 255)
CELL_HL = (80, 220, 150)          # sorot kata baru benar
BORDER = (90, 210, 200)
LETTER = (20, 28, 45)
NUMBER = (90, 110, 130)

CELL = 68          # ukuran sel (px)
PAD = 26           # margin papan
GAP = 2            # jarak antar sel

# Batas ukuran output supaya tak terlalu besar dikirim ke Telegram
MAX_SIDE = 1600


def _font(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        "arial.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "DejaVuSans.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


_FONT_CACHE: Dict[int, ImageFont.FreeTypeFont] = {}


def font(size: int) -> ImageFont.FreeTypeFont:
    if size not in _FONT_CACHE:
        _FONT_CACHE[size] = _font(size)
    return _FONT_CACHE[size]


def render(puzzle: Puzzle,
           solved_cells: Dict[Tuple[int, int], str],
           highlight: Optional[Set[Tuple[int, int]]] = None,
           title: str = "") -> bytes:
    """
    puzzle: struktur papan.
    solved_cells: {(r,c): huruf} sel yang sudah terbuka.
    highlight: sel yang disorot (kata baru terjawab).
    Return: bytes PNG.
    """
    highlight = highlight or set()
    h, w = puzzle.height, puzzle.width

    # Skala sel bila papan besar agar tak melebihi MAX_SIDE
    cell = CELL
    board_w = w * cell + (w - 1) * GAP
    board_h = h * cell + (h - 1) * GAP
    longest = max(board_w, board_h) + 2 * PAD
    if longest > MAX_SIDE:
        cell = max(28, int(cell * MAX_SIDE / longest))
        board_w = w * cell + (w - 1) * GAP
        board_h = h * cell + (h - 1) * GAP

    top_pad = PAD + (46 if title else 0)
    img_w = board_w + 2 * PAD
    img_h = board_h + PAD + top_pad
    img = Image.new("RGB", (img_w, img_h), BG)
    draw = ImageDraw.Draw(img)

    if title:
        draw.text((PAD, PAD // 2), title, fill=(210, 230, 240), font=font(30))

    num_font = font(max(11, cell // 4))
    letter_font = font(max(20, int(cell * 0.6)))

    for (r, c), correct in puzzle.grid.items():
        gr = r - puzzle.min_row
        gc = c - puzzle.min_col
        x1 = PAD + gc * (cell + GAP)
        y1 = top_pad + gr * (cell + GAP)
        x2 = x1 + cell
        y2 = y1 + cell

        if (r, c) in highlight:
            fill = CELL_HL
        elif (r, c) in solved_cells:
            fill = CELL_SOLVED
        else:
            fill = CELL_EMPTY
        draw.rectangle([x1, y1, x2, y2], fill=fill, outline=BORDER, width=2)

        # Nomor petunjuk di pojok kiri atas sel awal kata
        num = puzzle.number_at.get((r, c))
        if num:
            draw.text((x1 + 4, y1 + 2), str(num), fill=NUMBER, font=num_font)

        # Huruf bila sudah terjawab
        letter = solved_cells.get((r, c))
        if letter:
            bbox = draw.textbbox((0, 0), letter, font=letter_font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            tx = x1 + (cell - tw) / 2 - bbox[0]
            ty = y1 + (cell - th) / 2 - bbox[1]
            draw.text((tx, ty), letter, fill=LETTER, font=letter_font)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()
