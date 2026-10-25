"""
Bank soal Teka-Teki Silang — loader.

Soal disimpan di file teks `data/<tier>.txt`, satu soal per baris:

    JAWABAN|petunjuk/soal

- JAWABAN: satu kata, huruf A-Z (ASCII) saja — tanpa spasi/angka/tanda baca.
- Baris kosong atau diawali '#' diabaikan (komentar).

Tingkat: easy | normal | hard | nightmare.

Menambah soal: cukup tambah baris baru di file data yang sesuai, atau jalankan
`python build_bank.py` untuk regenerasi otomatis dari dataset terkurasi.
"""
import os

TIERS = ["easy", "normal", "hard", "nightmare"]
_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
_CACHE = {}


def _load(tier: str):
    if tier in _CACHE:
        return _CACHE[tier]
    path = os.path.join(_DATA_DIR, f"{tier}.txt")
    out = []
    seen = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "|" not in line:
                    continue
                ans, clue = line.split("|", 1)
                ans = ans.strip().upper()
                clue = clue.strip()
                if not ans or not clue:
                    continue
                if not (ans.isascii() and ans.isalpha()):
                    continue
                if ans in seen:
                    continue
                seen.add(ans)
                out.append((ans, clue))
    _CACHE[tier] = out
    return out


def by_tier(tier: str):
    """Kembalikan daftar (jawaban, petunjuk) untuk sebuah tingkat."""
    return list(_load(tier))


def count_by_tier():
    return {t: len(_load(t)) for t in TIERS}


def reload_bank():
    _CACHE.clear()
    return count_by_tier()
