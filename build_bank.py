"""
build_bank.py — Regenerasi bank soal TTS ke data/<tier>.txt

Menggabungkan dataset terkurasi (yang bisa diverifikasi & tak ambigu untuk
pencocokan tepat) menjadi baris "JAWABAN|petunjuk". Aman dijalankan ulang;
menimpa file data.

Jalankan:  python build_bank.py
"""
import os
import re

DATA = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA, exist_ok=True)

# tier -> list[(ANSWER, clue)]
BANK = {"easy": [], "normal": [], "hard": [], "nightmare": []}
_SEEN = {t: set() for t in BANK}
_SEEN_CLUE = set()   # cegah klu identik dipakai 2 jawaban (ambigu)


def add(tier, answer, clue):
    a = re.sub(r"[^A-Za-z]", "", answer).upper()
    if not a or not a.isascii() or len(a) < 3 or len(a) > 14:
        return
    # Tolak klu yang membocorkan jawaban (jawaban muncul sebagai kata di klu)
    if a.lower() in re.sub(r"[^a-z]", " ", clue.lower()).split():
        return
    # Tolak klu identik yang sudah dipakai jawaban lain (ambigu)
    cl = clue.strip().lower()
    if cl in _SEEN_CLUE:
        return
    if a in _SEEN[tier]:
        return
    # hindari kata yang sama muncul di >1 tier (pakai yang tier lebih mudah dulu)
    for t in ("easy", "normal", "hard", "nightmare"):
        if a in _SEEN[t]:
            return
    _SEEN[tier].add(a)
    _SEEN_CLUE.add(cl)
    BANK[tier].append((a, clue.strip()))


# ═══════════════ BILINGUAL: Bahasa Inggris dari kata Indonesia ═══════════════
# (kata konkret → terjemahan tunggal yang tak ambigu). tier: easy
EN = {
    "kucing": "cat", "anjing": "dog", "burung": "bird", "ikan": "fish",
    "kuda": "horse", "sapi": "cow", "kambing": "goat", "domba": "sheep",
    "babi": "pig", "ayam": "chicken", "bebek": "duck", "kelinci": "rabbit",
    "tikus": "mouse", "singa": "lion", "harimau": "tiger", "beruang": "bear",
    "gajah": "elephant", "monyet": "monkey", "rubah": "fox", "serigala": "wolf",
    "ular": "snake", "katak": "frog", "lebah": "bee", "semut": "ant",
    "laba-laba": "spider", "nyamuk": "mosquito", "lalat": "fly", "kupu-kupu": "butterfly",
    "buku": "book", "pena": "pen", "pensil": "pencil", "kertas": "paper",
    "meja": "table", "kursi": "chair", "pintu": "door", "jendela": "window",
    "kunci": "key", "jam": "clock", "lampu": "lamp", "tempat tidur": "bed",
    "rumah": "house", "sekolah": "school", "kota": "city", "desa": "village",
    "jalan": "road", "jembatan": "bridge", "gereja": "church", "kebun": "garden",
    "pohon": "tree", "bunga": "flower", "daun": "leaf", "rumput": "grass",
    "akar": "root", "biji": "seed", "hutan": "forest", "gunung": "mountain",
    "sungai": "river", "danau": "lake", "laut": "sea", "pantai": "beach",
    "pulau": "island", "langit": "sky", "matahari": "sun", "bulan": "moon",
    "bintang": "star", "awan": "cloud", "hujan": "rain", "salju": "snow",
    "angin": "wind", "api": "fire", "air": "water", "tanah": "soil",
    "batu": "stone", "pasir": "sand", "es": "ice", "asap": "smoke",
    "kepala": "head", "rambut": "hair", "mata": "eye", "hidung": "nose",
    "mulut": "mouth", "gigi": "tooth", "lidah": "tongue", "telinga": "ear",
    "leher": "neck", "bahu": "shoulder", "lengan": "arm", "jari": "finger",
    "kaki": "foot", "lutut": "knee", "jantung": "heart", "darah": "blood",
    "tulang": "bone", "kulit": "skin", "roti": "bread", "nasi": "rice",
    "telur": "egg", "susu": "milk", "keju": "cheese", "daging": "meat",
    "garam": "salt", "gula": "sugar", "madu": "honey", "minyak": "oil",
    "teh": "tea", "kopi": "coffee", "apel": "apple", "pisang": "banana",
    "jeruk": "orange", "anggur": "grape", "mangga": "mango", "nanas": "pineapple",
    "semangka": "watermelon", "stroberi": "strawberry", "tomat": "tomato",
    "kentang": "potato", "wortel": "carrot", "bawang": "onion", "jagung": "corn",
    "baju": "shirt", "celana": "pants", "sepatu": "shoe", "topi": "hat",
    "jaket": "jacket", "tas": "bag", "dompet": "wallet", "cincin": "ring",
    "mobil": "car", "sepeda": "bike", "kereta": "train", "kapal": "ship",
    "perahu": "boat", "pesawat": "plane", "bus": "bus", "truk": "truck",
    "guru": "teacher", "murid": "student", "dokter": "doctor", "perawat": "nurse",
    "petani": "farmer", "koki": "cook", "raja": "king", "ratu": "queen",
    "teman": "friend", "musuh": "enemy", "bayi": "baby", "anak": "child",
    "ibu": "mother", "ayah": "father", "kakak": "brother", "keluarga": "family",
    "cinta": "love", "waktu": "time", "hari": "day", "malam": "night",
    "tahun": "year", "warna": "color", "suara": "voice", "kata": "word",
    "nama": "name", "angka": "number", "uang": "money", "harga": "price",
    "pekerjaan": "job", "permainan": "game", "musik": "music", "lagu": "song",
    "cerita": "story", "gambar": "picture", "surat": "letter", "koran": "newspaper",
    "putih": "white", "hitam": "black", "merah": "red", "biru": "blue",
    "hijau": "green", "kuning": "yellow", "besar": "big", "kecil": "small",
    "panjang": "long", "pendek": "short", "tinggi": "tall", "panas": "hot",
    "dingin": "cold", "baru": "new", "lama": "old", "cepat": "fast",
    "lambat": "slow", "kuat": "strong", "lemah": "weak", "mudah": "easy",
    "sulit": "hard", "bahagia": "happy", "sedih": "sad", "marah": "angry",
    "takut": "afraid", "berani": "brave", "pintar": "smart", "bodoh": "stupid",
    "kaya": "rich", "miskin": "poor", "bersih": "clean", "kotor": "dirty",
    "makan": "eat", "minum": "drink", "tidur": "sleep", "lari": "run",
    "jalan kaki": "walk", "lompat": "jump", "duduk": "sit", "berdiri": "stand",
    "membaca": "read", "menulis": "write", "berbicara": "speak", "mendengar": "hear",
    "melihat": "see", "membeli": "buy", "menjual": "sell", "membuka": "open",
    "menutup": "close", "bekerja": "work", "bermain": "play", "menyanyi": "sing",
    "menari": "dance", "tersenyum": "smile", "menangis": "cry", "tertawa": "laugh",
}
for indo, eng in EN.items():
    if eng.isalpha():
        add("easy", eng, f"Bahasa Inggris dari '{indo}'")

# Reverse (Inggris → Indonesia) untuk kata yang jawabannya satu kata Indonesia
for indo, eng in EN.items():
    ind = re.sub(r"[^A-Za-z]", "", indo)
    if ind.isalpha() and 3 <= len(ind) <= 14 and " " not in indo and "-" not in indo:
        add("easy", indo, f"Terjemahan Indonesia dari '{eng}' (Inggris)")


# ═══════════════ KOSAKATA HARIAN (deskriptif) — EASY ═══════════════
EASY_DESC = [
    ("PAGAR", "Struktur sekeliling rumah"),
    ("RODA", "Bagian kendaraan berbentuk bundar"),
    ("BUMI", "Planet tempat manusia tinggal"),
    ("KURSI", "Tempat untuk duduk"),
    ("PIRING", "Wadah tempat menaruh makanan"),
    ("GELAS", "Wadah untuk minum"),
    ("SENDOK", "Alat makan untuk nasi berkuah"),
    ("GARPU", "Alat makan bergigi tajam"),
    ("PISAU", "Alat tajam untuk memotong"),
    ("KIPAS", "Alat pendingin dengan angin"),
    ("PAYUNG", "Pelindung dari hujan"),
    ("KACA", "Benda bening pemantul bayangan"),
    ("SABUN", "Untuk membersihkan badan saat mandi"),
    ("SIKAT", "Alat menggosok gigi"),
    ("HANDUK", "Kain pengering badan"),
    ("BANTAL", "Alas kepala saat tidur"),
    ("SELIMUT", "Penghangat tubuh saat tidur"),
    ("TANGGA", "Untuk naik ke lantai atas"),
    ("ATAP", "Bagian paling atas rumah"),
    ("LANTAI", "Bagian bawah yang diinjak di rumah"),
    ("DINDING", "Pembatas ruangan yang tegak"),
    ("DAPUR", "Tempat memasak di rumah"),
    ("KAMAR", "Ruang untuk tidur"),
    ("SUMUR", "Sumber air galian di tanah"),
    ("EMBER", "Wadah air bergagang"),
    ("SAPU", "Alat membersihkan lantai"),
    ("KAMPUNG", "Permukiman di pedesaan"),
    ("SAWAH", "Lahan basah tempat menanam padi"),
    ("LADANG", "Lahan kering pertanian"),
    ("PASAR", "Tempat jual beli barang"),
    ("BOLA", "Benda bulat untuk sepak"),
    ("PELANGI", "Busur tujuh warna setelah hujan"),
    ("KABUT", "Uap tebal yang menghalangi pandangan"),
    ("PETIR", "Kilatan cahaya saat badai"),
    ("GEMPA", "Getaran permukaan bumi"),
    ("KUCING", "Hewan peliharaan mengeong"),
    ("GAJAH", "Hewan besar berbelalai"),
    ("JERAPAH", "Hewan berleher sangat panjang"),
    ("ZEBRA", "Kuda liar bergaris hitam putih"),
    ("BUAYA", "Reptil besar penghuni sungai"),
    ("PENYU", "Kura-kura laut"),
    ("HIU", "Ikan besar pemangsa di laut"),
    ("PAUS", "Mamalia terbesar di laut"),
    ("LUMBA", "Mamalia laut cerdas suka melompat"),
    ("MERPATI", "Burung pembawa pesan"),
    ("ELANG", "Burung pemangsa bermata tajam"),
    ("BEBEK", "Unggas perenang berkaki selaput"),
    ("KAMBING", "Hewan ternak bertanduk pemakan rumput"),
    ("MANGKUK", "Wadah cekung untuk sup"),
    ("TEKO", "Wadah untuk menyeduh teh"),
    ("PANCI", "Wadah masak bergagang"),
    ("WAJAN", "Alat menggoreng"),
    ("KOMPOR", "Alat memasak berapi"),
    ("KULKAS", "Lemari pendingin makanan"),
    ("TELEVISI", "Kotak penyaji siaran gambar"),
    ("RADIO", "Alat penyiar suara gelombang"),
    ("PENGGARIS", "Alat untuk membuat garis lurus dan mengukur panjang"),
    ("PENGHAPUS", "Alat menghapus tulisan pensil"),
    ("SPIDOL", "Pena tebal untuk papan tulis"),
    ("KRAYON", "Pensil warna dari lilin"),
    ("BENDERA", "Kain lambang negara"),
    ("SEMUT", "Serangga kecil suka gula"),
    ("MADU", "Cairan manis dari lebah"),
    ("ROTI", "Makanan dari tepung dipanggang"),
    ("MENTEGA", "Olesan lembut kuning untuk roti"),
    ("COKELAT", "Camilan manis dari biji kakao"),
    ("PERMEN", "Gula-gula manis kesukaan anak"),
    ("KERUPUK", "Camilan renyah pendamping nasi"),
    ("BAKSO", "Bola daging dalam kuah"),
    ("SATE", "Daging ditusuk lalu dibakar"),
    ("SOTO", "Sup berkuah kuning khas Indonesia"),
    ("RENDANG", "Masakan daging bumbu Padang"),
]
for a, c in EASY_DESC:
    add("easy", a, c)


# ═══════════════ IBU KOTA NEGARA — NORMAL (ejaan Indonesia baku) ═══════════════
CAPITALS = {
    "Indonesia": "Jakarta", "Malaysia": "KualaLumpur", "Thailand": "Bangkok",
    "Filipina": "Manila", "Vietnam": "Hanoi", "Singapura": "Singapura",
    "Jepang": "Tokyo", "Korea Selatan": "Seoul", "China": "Beijing",
    "India": "NewDelhi", "Inggris": "London", "Prancis": "Paris",
    "Jerman": "Berlin", "Italia": "Roma", "Spanyol": "Madrid",
    "Portugal": "Lisbon", "Belanda": "Amsterdam", "Rusia": "Moskow",
    "Mesir": "Kairo", "Australia": "Canberra", "Kanada": "Ottawa",
    "Brasil": "Brasilia", "Argentina": "BuenosAires", "Yunani": "Athena",
    "Turki": "Ankara", "Iran": "Teheran", "Irak": "Baghdad",
    "Arab Saudi": "Riyadh", "Austria": "Wina", "Swiss": "Bern",
    "Swedia": "Stockholm", "Norwegia": "Oslo", "Finlandia": "Helsinki",
    "Polandia": "Warsawa", "Hongaria": "Budapest", "Irlandia": "Dublin",
    "Kuba": "Havana", "Meksiko": "MexicoCity", "Peru": "Lima",
    "Chili": "Santiago", "Kenya": "Nairobi", "Nigeria": "Abuja",
    "Afrika Selatan": "Pretoria", "Maroko": "Rabat", "Pakistan": "Islamabad",
    "Bangladesh": "Dhaka", "Myanmar": "Naypyidaw", "Kamboja": "PhnomPenh",
    "Laos": "Vientiane", "Mongolia": "Ulanbator", "Korea Utara": "Pyongyang",
}
for negara, kota in CAPITALS.items():
    k = re.sub(r"[^A-Za-z]", "", kota)
    if len(k) >= 3:
        add("normal", kota, f"Ibu kota negara {negara}")


# ═══════════════ MATA UANG — NORMAL ═══════════════
CURRENCY = {
    "Indonesia": "Rupiah", "Jepang": "Yen", "Amerika Serikat": "Dolar",
    "Inggris": "Poundsterling", "Uni Eropa": "Euro", "Korea": "Won",
    "Thailand": "Baht", "Malaysia": "Ringgit", "India": "Rupee",
    "Arab Saudi": "Riyal", "China": "Yuan", "Rusia": "Rubel",
    "Vietnam": "Dong", "Filipina": "Peso", "Bangladesh": "Taka",
    "Afrika Selatan": "Rand", "Turki": "Lira", "Israel": "Syekel",
}
for negara, uang in CURRENCY.items():
    add("normal", uang, f"Mata uang negara {negara}")


# ═══════════════ IBU KOTA PROVINSI INDONESIA — NORMAL ═══════════════
PROVINSI = {
    "Jawa Barat": "Bandung", "Jawa Tengah": "Semarang", "Jawa Timur": "Surabaya",
    "Banten": "Serang", "Yogyakarta": "Yogyakarta", "Bali": "Denpasar",
    "Sumatra Utara": "Medan", "Sumatra Barat": "Padang", "Riau": "Pekanbaru",
    "Jambi": "Jambi", "Bengkulu": "Bengkulu", "Lampung": "Bandarlampung",
    "Aceh": "BandaAceh", "Kalimantan Barat": "Pontianak", "Kalimantan Timur": "Samarinda",
    "Kalimantan Selatan": "Banjarmasin", "Kalimantan Tengah": "Palangkaraya",
    "Sulawesi Selatan": "Makassar", "Sulawesi Utara": "Manado",
    "Sulawesi Tengah": "Palu", "Sulawesi Tenggara": "Kendari",
    "Gorontalo": "Gorontalo", "Papua": "Jayapura", "Maluku": "Ambon",
    "Nusa Tenggara Barat": "Mataram", "Nusa Tenggara Timur": "Kupang",
}
for prov, kota in PROVINSI.items():
    add("normal", kota, f"Ibu kota provinsi {prov}")


# ═══════════════ PENGETAHUAN UMUM — NORMAL (deskriptif) ═══════════════
NORMAL_DESC = [
    ("GARUDA", "Lambang negara Indonesia"),
    ("PANCASILA", "Dasar negara Indonesia"),
    ("PROKLAMASI", "Pernyataan kemerdekaan 1945"),
    ("PRESIDEN", "Kepala negara republik"),
    ("MENTERI", "Pembantu presiden urus bidang tertentu"),
    ("PEMILU", "Pesta demokrasi memilih pemimpin"),
    ("KOMPAS", "Alat penunjuk arah mata angin"),
    ("TEROPONG", "Alat melihat benda jauh"),
    ("MIKROSKOP", "Alat melihat benda sangat kecil"),
    ("TERMOMETER", "Alat pengukur suhu"),
    ("BAROMETER", "Alat pengukur tekanan udara"),
    ("MAGNET", "Benda penarik logam besi"),
    ("BATERAI", "Sumber listrik portabel"),
    ("TSUNAMI", "Gelombang laut besar akibat gempa"),
    ("OKSIGEN", "Gas untuk bernapas"),
    ("VITAMIN", "Zat gizi penjaga daya tahan"),
    ("PROTEIN", "Zat pembangun tubuh dari lauk"),
    ("JANTUNG", "Organ pemompa darah"),
    ("GINJAL", "Organ penyaring darah"),
    ("VAKSIN", "Zat untuk kekebalan penyakit"),
    ("GALAKSI", "Kumpulan miliaran bintang"),
    ("KOMET", "Bintang berekor di langit"),
    ("METEOR", "Bintang jatuh terbakar di atmosfer"),
    ("SATELIT", "Benda yang mengelilingi planet"),
    ("GRAVITASI", "Gaya tarik bumi"),
    ("GAMELAN", "Alat musik tradisional Jawa"),
    ("ANGKLUNG", "Alat musik bambu dari Sunda"),
    ("BATIK", "Kain khas Indonesia bermotif"),
    ("WAYANG", "Pertunjukan boneka kulit"),
    ("KOMODO", "Kadal raksasa dari Nusa Tenggara"),
    ("ORANGUTAN", "Kera besar dari Kalimantan"),
    ("STADION", "Tempat pertandingan olahraga besar"),
    ("MARATON", "Lomba lari jarak sangat jauh"),
    ("EKONOMI", "Ilmu tentang uang dan kebutuhan"),
    ("KOPERASI", "Badan usaha bersama anggota"),
    ("INFLASI", "Kenaikan harga barang secara umum"),
    ("BIOLOGI", "Ilmu tentang makhluk hidup"),
    ("KIMIA", "Ilmu tentang zat dan reaksinya"),
    ("FISIKA", "Ilmu tentang gaya dan energi"),
    ("SASTRA", "Karya tulis bernilai seni"),
    ("PANTUN", "Puisi lama empat baris bersajak"),
    ("KAMUS", "Buku daftar kata dan artinya"),
    ("ATLAS", "Buku kumpulan peta"),
    ("MERKURIUS", "Planet terdekat dari matahari"),
    ("VENUS", "Planet terpanas di tata surya"),
    ("YUPITER", "Planet terbesar di tata surya"),
    ("SATURNUS", "Planet bercincin indah"),
    ("NEPTUNUS", "Planet terjauh dari matahari"),
]
for a, c in NORMAL_DESC:
    add("normal", a, c)


# ═══════════════ SAINS & ISTILAH — HARD ═══════════════
HARD_DESC = [
    ("FOTOSINTESIS", "Proses tumbuhan membuat makanan"),
    ("KLOROFIL", "Zat hijau daun"),
    ("EKOSISTEM", "Hubungan makhluk hidup dan lingkungan"),
    ("SIMBIOSIS", "Hubungan timbal balik dua makhluk"),
    ("METAMORFOSIS", "Perubahan bentuk hewan bertahap"),
    ("FERMENTASI", "Peragian menghasilkan zat baru"),
    ("KONDENSASI", "Perubahan gas menjadi cair"),
    ("EVAPORASI", "Penguapan air menjadi uap"),
    ("ENZIM", "Katalis biologis dalam tubuh"),
    ("KROMOSOM", "Pembawa sifat keturunan"),
    ("GENETIKA", "Ilmu tentang pewarisan sifat"),
    ("EVOLUSI", "Perubahan makhluk hidup bertahap lama"),
    ("ARKEOLOGI", "Ilmu tentang peninggalan kuno"),
    ("ASTRONOMI", "Ilmu tentang benda langit"),
    ("NEBULA", "Awan gas dan debu antarbintang"),
    ("SUPERNOVA", "Ledakan bintang raksasa"),
    ("ASTEROID", "Batuan kecil mengorbit matahari"),
    ("ATMOSFER", "Lapisan udara pembungkus bumi"),
    ("LITOSFER", "Lapisan batuan kulit bumi"),
    ("KHATULISTIWA", "Garis lintang nol derajat"),
    ("MONSUN", "Angin musiman pembawa hujan"),
    ("MINERAL", "Bahan tambang dari dalam bumi"),
    ("ELEKTRON", "Partikel bermuatan negatif"),
    ("PROTON", "Partikel bermuatan positif inti atom"),
    ("NEUTRON", "Partikel netral dalam inti atom"),
    ("MOLEKUL", "Gabungan dua atom atau lebih"),
    ("SENYAWA", "Zat gabungan beberapa unsur"),
    ("OKSIDASI", "Reaksi pengikatan oksigen"),
    ("KOROSI", "Perkaratan logam"),
    ("SPEKTRUM", "Uraian cahaya menjadi warna"),
    ("FREKUENSI", "Jumlah getaran per detik"),
    ("RESONANSI", "Ikut bergetar karena frekuensi sama"),
    ("REFRAKSI", "Pembiasan cahaya"),
    ("KAPASITOR", "Komponen penyimpan muatan listrik"),
    ("RESISTOR", "Komponen penghambat arus listrik"),
    ("ALGORITMA", "Langkah logis pemecah masalah"),
    ("ENKRIPSI", "Penyandian data agar aman"),
    ("DEMOKRASI", "Pemerintahan dari rakyat"),
    ("KONSTITUSI", "Hukum dasar sebuah negara"),
    ("DIPLOMASI", "Hubungan resmi antarnegara"),
    ("MONOPOLI", "Penguasaan pasar oleh satu pihak"),
    ("HIPOTESIS", "Dugaan sementara sebuah penelitian"),
    ("METAFORA", "Kiasan tanpa kata pembanding"),
    ("PSIKOLOGI", "Ilmu tentang jiwa dan perilaku"),
    ("SOSIOLOGI", "Ilmu tentang masyarakat"),
    ("URBANISASI", "Perpindahan desa ke kota"),
]
for a, c in HARD_DESC:
    add("hard", a, c)

# Unsur kimia (nama) — HARD
ELEMENTS = {
    "H": "Hidrogen", "He": "Helium", "Li": "Litium", "C": "Karbon",
    "N": "Nitrogen", "O": "Oksigen", "F": "Fluor", "Na": "Natrium",
    "Mg": "Magnesium", "Al": "Aluminium", "Si": "Silikon", "P": "Fosfor",
    "S": "Belerang", "Cl": "Klorin", "K": "Kalium", "Ca": "Kalsium",
    "Fe": "Besi", "Cu": "Tembaga", "Zn": "Seng", "Ag": "Perak",
    "Au": "Emas", "Hg": "Raksa", "Pb": "Timbal", "U": "Uranium",
}
for sym, nama in ELEMENTS.items():
    add("hard", nama, f"Unsur kimia berlambang {sym}")


# ═══════════════ NIGHTMARE — sangat sulit / istilah langka ═══════════════
NIGHTMARE_DESC = [
    ("PALEONTOLOGI", "Ilmu tentang fosil purba"),
    ("STRATOSFER", "Lapisan atmosfer tempat lapisan ozon"),
    ("TERMODINAMIKA", "Ilmu tentang panas dan energi"),
    ("ELEKTROMAGNETIK", "Gelombang gabungan listrik dan magnet"),
    ("SEMIKONDUKTOR", "Bahan antara isolator dan konduktor"),
    ("FOTOLISTRIK", "Efek keluarnya elektron karena cahaya"),
    ("RELATIVITAS", "Teori ruang-waktu Einstein"),
    ("ENTROPI", "Ukuran ketidakteraturan sistem"),
    ("ISOTOP", "Atom sama nomor beda massa"),
    ("KATALISATOR", "Zat yang mempercepat reaksi tanpa ikut bereaksi"),
    ("POLIMER", "Molekul rantai panjang berulang"),
    ("MITOKONDRIA", "Organel penghasil energi sel"),
    ("RIBOSOM", "Organel tempat sintesis protein"),
    ("SITOPLASMA", "Cairan pengisi dalam sel"),
    ("FAGOSITOSIS", "Sel menelan partikel padat"),
    ("HEMOGLOBIN", "Protein pengikat oksigen dalam darah"),
    ("NEUROTRANSMITER", "Zat pengantar sinyal antarsaraf"),
    ("FOTORESEPTOR", "Sel mata penangkap cahaya"),
    ("BIOLUMINESENSI", "Cahaya yang dihasilkan makhluk hidup"),
    ("EKSOPLANET", "Planet di luar tata surya"),
    ("HELIOSENTRIS", "Paham matahari sebagai pusat"),
    ("PARALAKS", "Pergeseran posisi benda karena sudut pandang"),
    ("KUANTUM", "Satuan terkecil energi"),
    ("SUBLIMASI", "Perubahan padat langsung ke gas"),
    ("DEPOSISI", "Perubahan gas langsung ke padat"),
    ("VISKOSITAS", "Kekentalan zat cair"),
    ("KAPILARITAS", "Naiknya zat cair di pipa sempit"),
    ("ELEKTROLISIS", "Penguraian zat dengan arus listrik"),
    ("STOIKIOMETRI", "Perhitungan kuantitatif reaksi kimia"),
    ("EPISTEMOLOGI", "Cabang filsafat tentang pengetahuan"),
    ("METAFISIKA", "Cabang filsafat tentang hakikat ada"),
    ("HERMENEUTIKA", "Ilmu tentang penafsiran teks"),
    ("DIALEKTIKA", "Metode berpikir tesis-antitesis-sintesis"),
    ("ONTOLOGI", "Cabang filsafat tentang keberadaan"),
    ("SILOGISME", "Penarikan kesimpulan logika deduktif"),
    ("PARADOKS", "Pernyataan tampak bertentangan"),
    ("OKSIMORON", "Gabungan dua kata berlawanan makna"),
    ("SINESTESIA", "Bercampurnya persepsi antarindra"),
    ("HEGEMONI", "Dominasi kekuasaan satu kelompok"),
    ("BIROKRASI", "Sistem administrasi berjenjang"),
    ("OLIGARKI", "Kekuasaan di tangan segelintir orang"),
    ("PLUTOKRASI", "Pemerintahan oleh orang kaya"),
    ("MERITOKRASI", "Sistem berbasis prestasi/kemampuan"),
    ("DEFLASI", "Penurunan harga barang secara umum"),
    ("OKSIDATOR", "Zat penyebab oksidasi"),
]
for a, c in NIGHTMARE_DESC:
    add("nightmare", a, c)


# ═══════════════ EKSPANSI 2 — lebih banyak bilingual (EASY) ═══════════════
EN2 = {
    "singa laut": "seal", "gurita": "octopus", "udang": "shrimp", "kepiting": "crab",
    "cacing": "worm", "siput": "snail", "kadal": "lizard", "kura-kura": "turtle",
    "unta": "camel", "keledai": "donkey", "tupai": "squirrel", "landak": "hedgehog",
    "kelelawar": "bat", "merak": "peacock", "angsa": "swan", "burung hantu": "owl",
    "sapu tangan": "handkerchief", "sarung tangan": "glove", "kaus kaki": "sock",
    "sabuk": "belt", "dasi": "tie", "payudara": "chest", "punggung": "back",
    "perut": "stomach", "siku": "elbow", "pergelangan": "wrist", "tumit": "heel",
    "alis": "eyebrow", "bulu mata": "eyelash", "bibir": "lip", "pipi": "cheek",
    "dagu": "chin", "dahi": "forehead", "otak": "brain", "paru": "lung",
    "hati": "liver", "otot": "muscle", "urat": "vein", "saraf": "nerve",
    "pagi": "morning", "siang": "noon", "sore": "afternoon", "minggu": "week",
    "bulan kalender": "month", "musim": "season", "kemarin": "yesterday",
    "besok": "tomorrow", "sekarang": "now", "nanti": "later",
    "utara": "north", "selatan": "south", "timur": "east", "barat": "west",
    "kiri": "left", "kanan": "right", "atas": "up", "bawah": "down",
    "depan": "front", "belakang": "back", "tengah": "middle", "dekat": "near",
    "jauh": "far", "dalam": "deep", "luar": "outside", "dunia": "world",
    "negara": "country", "bahasa": "language", "agama": "religion", "budaya": "culture",
    "sejarah": "history", "ilmu": "science", "seni": "art", "hukum": "law",
    "perang": "war", "damai": "peace", "kebebasan": "freedom", "keadilan": "justice",
    "kebenaran": "truth", "kebohongan": "lie", "harapan": "hope", "mimpi": "dream",
    "ingatan": "memory", "pikiran": "mind", "perasaan": "feeling", "jiwa": "soul",
    "tubuh": "body", "kesehatan": "health", "penyakit": "disease", "obat": "medicine",
    "rumah sakit": "hospital", "apotek": "pharmacy", "kantor": "office", "pabrik": "factory",
    "toko": "shop", "restoran": "restaurant", "hotel": "hotel", "bandara": "airport",
    "stasiun": "station", "pelabuhan": "harbor", "penjara": "prison", "museum": "museum",
    "perpustakaan": "library", "taman": "park", "kebun binatang": "zoo",
    "gunung berapi": "volcano", "gua": "cave", "gurun": "desert", "lembah": "valley",
    "air terjun": "waterfall", "kolam": "pond", "mata air": "spring", "banjir": "flood",
    "kekeringan": "drought", "badai": "storm", "guntur": "thunder", "kilat": "lightning",
    "bayangan": "shadow", "cahaya": "light", "kegelapan": "darkness", "warna-warni": "rainbow",
    "logam": "metal", "kayu": "wood", "kaca jendela": "glass", "plastik": "plastic",
    "karet": "rubber", "kain": "cloth", "benang": "thread", "jarum": "needle",
    "paku": "nail", "palu": "hammer", "gergaji": "saw", "tangga lipat": "ladder",
}
for indo, eng in EN2.items():
    if eng.isalpha():
        add("easy", eng, f"Bahasa Inggris dari '{indo}'")
for indo, eng in EN2.items():
    ind = re.sub(r"[^A-Za-z]", "", indo)
    if ind.isalpha() and 3 <= len(ind) <= 14 and " " not in indo and "-" not in indo:
        add("easy", indo, f"Terjemahan Indonesia dari '{eng}' (Inggris)")


# ═══════════════ LAWAN KATA — EASY ═══════════════
ANTONYM = [
    ("KECIL", "besar"), ("PENDEK", "panjang"), ("RENDAH", "tinggi"),
    ("LAMBAT", "cepat"), ("DINGIN", "panas"), ("KERING", "basah"),
    ("TERANG", "gelap"), ("RINGAN", "berat"), ("LEMBUT", "kasar"),
    ("TAJAM", "tumpul"), ("PENUH", "kosong"), ("BENAR", "salah"),
    ("MURAH", "mahal"), ("MUDA", "tua"), ("BANGUN", "tidur"),
    ("MENANG", "kalah"), ("BUKA", "tutup"), ("NAIK", "turun"),
    ("MASUK", "keluar"), ("DATANG", "pergi"), ("MULAI", "selesai"),
    ("BERANI", "takut"), ("RAJIN", "malas"), ("JUJUR", "bohong"),
    ("HEMAT", "boros"), ("SEHAT", "sakit"), ("TEBAL", "tipis"),
    ("LEBAR", "sempit"), ("LURUS", "bengkok"), ("HALUS", "kasar"),
]
for ans, lawan in ANTONYM:
    add("easy", ans, f"Lawan kata '{lawan}'")


# ═══════════════ EKSPANSI EASY (deskriptif) ═══════════════
EASY2 = [
    ("SENDAL", "Alas kaki terbuka santai"),
    ("KACAMATA", "Alat bantu penglihatan di wajah"),
    ("JEMBATAN", "Penghubung dua tepi sungai"),
    ("TEROWONGAN", "Lorong tembus di bawah gunung"),
    ("MENARA", "Bangunan tinggi menjulang"),
    ("BENTENG", "Bangunan pertahanan berdinding tebal"),
    ("ISTANA", "Tempat tinggal raja"),
    ("GUBUK", "Rumah kecil sederhana di ladang"),
    ("PERAHU", "Kendaraan kecil di air"),
    ("JANGKAR", "Penahan kapal agar tak hanyut"),
    ("LAYAR", "Kain penangkap angin di perahu"),
    ("DAYUNG", "Alat mengayuh perahu"),
    ("PANCING", "Alat menangkap ikan berkail"),
    ("JALA", "Jaring penangkap ikan"),
    ("CANGKUL", "Alat menggali tanah petani"),
    ("SABIT", "Alat pemotong rumput melengkung"),
    ("LUMBUNG", "Tempat menyimpan hasil panen"),
    ("KANDANG", "Tempat memelihara ternak"),
    ("SARANG", "Rumah burung dari ranting"),
    ("TELAGA", "Kolam air alami di pegunungan"),
    ("OASE", "Sumber air di tengah gurun"),
    ("KARANG", "Batuan berpori tempat ikan hias"),
    ("OMBAK", "Gelombang air di pantai"),
    ("PASANG", "Naiknya air laut"),
    ("EMBUN", "Titik air pagi di dedaunan"),
    ("SIRIP", "Alat gerak ikan di air"),
    ("SAYAP", "Alat terbang burung"),
    ("PARUH", "Mulut keras burung"),
    ("CAKAR", "Kuku tajam hewan pemangsa"),
    ("SISIK", "Pelindung tubuh ular dan ikan"),
    ("TANDUK", "Senjata keras di kepala sapi"),
    ("BELALAI", "Hidung panjang gajah"),
    ("SURAI", "Rambut di leher singa/kuda"),
    ("EKOR", "Bagian belakang tubuh hewan"),
    ("BULU", "Penutup tubuh burung"),
    ("SUSUK", "—"),
]
for a, c in EASY2:
    if c != "—":
        add("easy", a, c)


# ═══════════════ EKSPANSI NORMAL ═══════════════
NORMAL2 = [
    ("KATULISTIWA", "Garis khayal pembagi bumi utara-selatan"),
    ("MERIDIAN", "Garis bujur pada peta"),
    ("EQUATOR", "Istilah Inggris garis khatulistiwa"),
    ("KARTOGRAFI", "Ilmu pembuatan peta"),
    ("DEMOGRAFI", "Ilmu tentang kependudukan"),
    ("MIGRASI", "Perpindahan penduduk antarwilayah"),
    ("TRANSMIGRASI", "Pindah antarpulau di Indonesia"),
    ("KOLONIALISME", "Paham penjajahan bangsa lain"),
    ("NASIONALISME", "Paham cinta tanah air"),
    ("REVOLUSI", "Perubahan besar dan cepat"),
    ("REFORMASI", "Perubahan menuju perbaikan sistem"),
    ("KABINET", "Dewan para menteri"),
    ("PARLEMEN", "Lembaga perwakilan rakyat"),
    ("MONARKI", "Pemerintahan oleh raja"),
    ("REPUBLIK", "Negara dipimpin presiden"),
    ("FEDERASI", "Gabungan beberapa negara bagian"),
    ("EMBARGO", "Larangan perdagangan suatu negara"),
    ("SUBSIDI", "Bantuan pemerintah menekan harga"),
    ("PAJAK", "Iuran wajib rakyat ke negara"),
    ("RETRIBUSI", "Pungutan atas jasa pemerintah"),
    ("EKSPOR", "Menjual barang ke luar negeri"),
    ("IMPOR", "Membeli barang dari luar negeri"),
    ("KREDIT", "Pinjaman yang dibayar bertahap"),
    ("DEBIT", "Pengurangan saldo rekening"),
    ("SAHAM", "Bukti kepemilikan perusahaan"),
    ("OBLIGASI", "Surat utang berbunga"),
    ("KOMODITAS", "Barang dagangan pokok"),
    ("PRODUSEN", "Pihak yang menghasilkan barang"),
    ("KONSUMEN", "Pihak yang memakai barang"),
    ("DISTRIBUSI", "Penyaluran barang ke konsumen"),
    ("KATROL", "Roda beralur pengangkat beban"),
    ("PENGUNGKIT", "Tuas untuk mengangkat beban"),
    ("BIDANG", "Permukaan miring pengurang gaya"),
    ("DINAMO", "Pengubah gerak jadi listrik"),
    ("TURBIN", "Roda penggerak pembangkit tenaga"),
    ("GENERATOR", "Pembangkit tenaga listrik"),
    ("TRANSFORMATOR", "Pengubah tegangan listrik"),
    ("KAPILER", "Pembuluh darah terkecil"),
    ("ARTERI", "Pembuluh pembawa darah dari jantung"),
    ("VENA", "Pembuluh pembawa darah ke jantung"),
]
for a, c in NORMAL2:
    add("normal", a, c)


# ═══════════════ EKSPANSI HARD ═══════════════
HARD2 = [
    ("DIFRAKSI", "Pelenturan gelombang"),
    ("INTERFERENSI", "Perpaduan dua gelombang"),
    ("AMPLITUDO", "Simpangan terjauh getaran"),
    ("VOLTASE", "Beda potensial listrik"),
    ("AMPERE", "Satuan kuat arus listrik"),
    ("WATT", "Satuan daya listrik"),
    ("JOULE", "Satuan energi dan usaha"),
    ("NEWTON", "Satuan gaya dalam fisika (lambang N)"),
    ("PASCAL", "Satuan tekanan"),
    ("KALORI", "Satuan energi makanan"),
    ("MASSA", "Ukuran jumlah materi benda"),
    ("VOLUME", "Ukuran ruang yang ditempati benda"),
    ("DENSITAS", "Massa per satuan volume"),
    ("INERSIA", "Kecenderungan benda mempertahankan gerak"),
    ("MOMENTUM", "Hasil kali massa dan kecepatan"),
    ("PROTOZOA", "Hewan bersel satu"),
    ("FUNGI", "Kelompok jamur"),
    ("BAKTERI", "Makhluk bersel satu sangat kecil"),
    ("VIRUS", "Mikroba penyebab penyakit menular"),
    ("PLASMA", "Wujud zat keempat bersuhu tinggi"),
    ("ANTIBODI", "Zat kekebalan pelawan kuman"),
    ("ANTIGEN", "Zat pemicu respon imun"),
    ("HORMON", "Zat pengatur fungsi tubuh"),
    ("INSULIN", "Hormon pengatur gula darah"),
    ("ADRENALIN", "Hormon pemicu semangat/takut"),
    ("SINTESIS", "Penggabungan menjadi satu kesatuan"),
    ("ANALISIS", "Penguraian menjadi bagian-bagian"),
    ("KATALIS", "Zat yang mempercepat reaksi kimia"),
    ("LARUTAN", "Campuran homogen zat terlarut"),
    ("SUSPENSI", "Campuran keruh yang mengendap"),
]
for a, c in HARD2:
    add("hard", a, c)


# ═══════════════ EKSPANSI NIGHTMARE ═══════════════
NIGHTMARE2 = [
    ("BIOTEKNOLOGI", "Pemanfaatan makhluk hidup untuk teknologi"),
    ("NANOTEKNOLOGI", "Teknologi skala molekul/atom"),
    ("KRIPTOGRAFI", "Ilmu penyandian pesan rahasia"),
    ("ASTROFISIKA", "Fisika benda-benda langit"),
    ("KOSMOLOGI", "Ilmu tentang asal usul alam semesta"),
    ("GEOFISIKA", "Fisika tentang bumi"),
    ("SEISMOGRAF", "Alat pencatat getaran gempa"),
    ("SPEKTROSKOPI", "Analisis zat lewat spektrum cahaya"),
    ("KROMATOGRAFI", "Pemisahan campuran zat"),
    ("ELEKTROKARDIOGRAM", "Rekaman aktivitas listrik jantung"),
    ("FOTOSFER", "Lapisan cahaya permukaan matahari"),
    ("MAGNETOSFER", "Zona medan magnet sekitar planet"),
    ("IONOSFER", "Lapisan atmosfer berion pemantul radio"),
    ("TROPOSFER", "Lapisan atmosfer tempat cuaca terjadi"),
    ("SUBDUKSI", "Penunjaman lempeng bumi"),
    ("TEKTONIK", "Berkaitan pergerakan lempeng bumi"),
    ("MAGMA", "Batuan cair di dalam bumi"),
    ("STALAKTIT", "Kerucut kapur menggantung di gua"),
    ("STALAGMIT", "Kerucut kapur tumbuh dari lantai gua"),
    ("FOTOTROPISME", "Gerak tumbuhan ke arah cahaya"),
    ("GEOTROPISME", "Gerak tumbuhan mengikuti gravitasi"),
    ("OSMOSIS", "Perpindahan zat lewat membran"),
    ("DIFUSI", "Penyebaran zat dari pekat ke encer"),
    ("HOMEOSTASIS", "Keseimbangan lingkungan dalam tubuh"),
    ("METABOLISME", "Seluruh reaksi kimia dalam tubuh"),
    ("KATABOLISME", "Penguraian zat menghasilkan energi"),
    ("ANABOLISME", "Penyusunan zat memerlukan energi"),
    ("FILANTROPI", "Kedermawanan menolong sesama"),
    ("ANTROPOSENTRIS", "Paham manusia sebagai pusat"),
    ("EGALITARIAN", "Paham kesetaraan semua orang"),
    ("UTILITARIAN", "Paham manfaat sebesar-besarnya"),
    ("DETERMINISME", "Paham segala sesuatu telah ditentukan"),
    ("EMPIRISME", "Pengetahuan bersumber pengalaman"),
    ("RASIONALISME", "Pengetahuan bersumber akal"),
    ("SKEPTISISME", "Sikap ragu terhadap kebenaran"),
    ("PRAGMATISME", "Paham berorientasi hasil praktis"),
    ("EKSISTENSIALISME", "Paham menekankan keberadaan individu"),
    ("FENOMENOLOGI", "Studi tentang pengalaman kesadaran"),
    ("KOGNISI", "Proses berpikir dan mengetahui"),
    ("INTUISI", "Pemahaman langsung tanpa penalaran"),
]
for a, c in NIGHTMARE2:
    add("nightmare", a, c)


# ═══════════════ EKSPANSI 3 — bilingual tambahan (EASY) ═══════════════
EN3 = {
    "raja hutan": "lion", "kunci pintu": "lock", "cermin": "mirror",
    "keranjang": "basket", "botol": "bottle", "kaleng": "can", "kotak": "box",
    "peti": "chest", "laci": "drawer", "rak": "shelf", "lemari": "cupboard",
    "karpet": "carpet", "tirai": "curtain", "kompor gas": "stove", "oven": "oven",
    "setrika": "iron", "sapu lidi": "broom", "sikat gigi": "toothbrush",
    "gunting": "scissors", "lem": "glue", "cat": "paint", "kuas": "brush",
    "peta": "map", "bendera negara": "flag", "lonceng": "bell", "peluit": "whistle",
    "drum": "drum", "seruling": "flute", "biola": "violin", "terompet": "trumpet",
    "gitar listrik": "guitar", "piano akustik": "piano", "gendang": "drum",
    "matahari terbit": "sunrise", "matahari terbenam": "sunset", "cuaca": "weather",
    "iklim": "climate", "suhu": "temperature", "kelembapan": "humidity",
    "tekanan": "pressure", "kecepatan": "speed", "jarak": "distance", "berat": "weight",
    "tinggi badan": "height", "kedalaman": "depth", "lebar": "width", "bentuk": "shape",
    "lingkaran": "circle", "persegi": "square", "segitiga": "triangle",
    "bintang laut": "starfish", "ubur-ubur": "jellyfish", "kerang": "shell",
    "mutiara": "pearl", "berlian": "diamond", "emas batangan": "gold", "perak logam": "silver",
    "tembaga logam": "copper", "besi baja": "steel", "timah": "tin", "kuningan": "brass",
    "gandum": "wheat", "beras": "rice", "kacang": "bean", "kedelai": "soybean",
    "kapas": "cotton", "sutra": "silk", "wol": "wool", "kulit hewan": "leather",
    "musim semi": "spring", "musim panas": "summer", "musim gugur": "autumn",
    "musim dingin": "winter", "abad": "century", "dekade": "decade", "jam dinding": "clock",
    "menit": "minute", "detik": "second", "kalender": "calendar", "jadwal": "schedule",
    "sarapan": "breakfast", "makan siang": "lunch", "makan malam": "dinner",
    "resep": "recipe", "tepung": "flour", "adonan": "dough", "sup": "soup",
    "salad": "salad", "saus": "sauce", "cuka": "vinegar", "merica": "pepper",
    "jahe": "ginger", "kunyit": "turmeric", "kayu manis": "cinnamon",
    "es krim": "icecream", "kue": "cake", "biskuit": "biscuit", "pai": "pie",
    "selai": "jam", "sirup": "syrup", "jus": "juice", "sup ayam": "soup",
    "raksasa": "giant", "kurcaci": "dwarf", "peri": "fairy", "penyihir": "witch",
    "hantu": "ghost", "naga": "dragon", "pahlawan": "hero", "penjahat": "villain",
    "harta karun": "treasure", "peta harta": "map", "bajak laut": "pirate",
    "kastil": "castle", "mahkota": "crown", "pedang": "sword", "perisai": "shield",
    "panah": "arrow", "busur": "bow", "tombak": "spear", "meriam": "cannon",
}
for indo, eng in EN3.items():
    if eng.isalpha():
        add("easy", eng, f"Bahasa Inggris dari '{indo}'")


# ═══════════════ SINONIM — EASY ═══════════════
SYNONYM = [
    ("PANDAI", "pintar"), ("CANTIK", "elok"), ("GEMBIRA", "senang"),
    ("MARAH", "murka"), ("LELAH", "capai"), ("CEPAT", "kilat"),
    ("INDAH", "elok"), ("SUKAR", "sulit"), ("GEMPAL", "gemuk"),
    ("KURUS", "ceking"), ("PEMBERANI", "gagah"), ("BOHONG", "dusta"),
    ("PAHAM", "mengerti"), ("HEMAT", "irit"), ("RAJIN", "tekun"),
    ("SEDIH", "duka"), ("TAKUT", "cemas"), ("HEBAT", "dahsyat"),
    ("BODOH", "dungu"), ("KOTOR", "jorok"), ("RAMAI", "riuh"),
    ("SEPI", "sunyi"), ("BESAR", "raksasa"), ("MUNGIL", "kecil"),
    ("LUCU", "jenaka"), ("BAU", "busuk"), ("HARUM", "wangi"),
    ("KUAT", "perkasa"), ("DEKAT", "hampir"), ("GELAP", "kelam"),
]
for ans, sinonim in SYNONYM:
    add("easy", ans, f"Sinonim (persamaan kata) dari '{sinonim}'")


# ═══════════════ EKSPANSI EASY 3 (deskriptif) ═══════════════
EASY3 = [
    ("SERULING", "Alat musik tiup dari bambu"),
    ("KENDANG", "Gendang pengiring gamelan"),
    ("REBANA", "Gendang kecil pengiring lagu religi"),
    ("HARMONIKA", "Alat musik tiup kecil di mulut"),
    ("PIANIKA", "Alat musik tiup bertuts di sekolah"),
    ("GITAR", "Alat musik berdawai dipetik"),
    ("DRUM", "Alat musik pukul dalam band"),
    ("SASANDO", "Alat musik petik khas Rote"),
    ("KOLINTANG", "Alat musik pukul kayu dari Minahasa"),
    ("TIFA", "Gendang khas Papua dan Maluku"),
    ("BADMINTON", "Olahraga tepok bulu tangkis"),
    ("VOLI", "Olahraga bola lewat net dengan tangan"),
    ("BASKET", "Olahraga memasukkan bola ke ring"),
    ("RENANG", "Olahraga di dalam air"),
    ("TINJU", "Olahraga adu pukul bersarung"),
    ("KARATE", "Bela diri asal Jepang"),
    ("SILAT", "Bela diri tradisional Indonesia"),
    ("CATUR", "Permainan strategi papan 64 kotak"),
    ("BILIAR", "Olahraga bola dan tongkat di meja"),
    ("GOLF", "Olahraga memukul bola ke lubang"),
    ("PANAHAN", "Olahraga menembak dengan busur"),
    ("GAWANG", "Sasaran gol dalam sepak bola"),
    ("PENALTI", "Tendangan hukuman dari titik putih"),
    ("PIALA", "Hadiah juara berbentuk cangkir"),
    ("MEDALI", "Lencana penghargaan pemenang"),
    ("JUARA", "Pemenang pertama lomba"),
    ("WASIT", "Pemimpin jalannya pertandingan"),
    ("PELATIH", "Pembimbing latihan olahraga"),
    ("STADION", "Tempat pertandingan olahraga besar"),
    ("SERAGAM", "Pakaian resmi sekolah/kantor"),
    ("DASI", "Pelengkap kemeja di leher"),
    ("JAS", "Pakaian resmi berkerah"),
    ("KEBAYA", "Pakaian tradisional wanita Indonesia"),
    ("SARUNG", "Kain bawahan pria untuk salat"),
    ("SELENDANG", "Kain panjang di bahu penari"),
    ("MAHKOTA", "Hiasan kepala raja"),
    ("GELANG", "Perhiasan di pergelangan tangan"),
    ("KALUNG", "Perhiasan di leher"),
    ("ANTING", "Perhiasan di telinga"),
    ("CINCIN", "Perhiasan melingkar di jari"),
]
for a, c in EASY3:
    add("easy", a, c)


# ═══════════════ NEGARA (dari ibu kota) — NORMAL ═══════════════
COUNTRY_SINGLE = {
    "Jakarta": "Indonesia", "Tokyo": "Jepang", "Paris": "Prancis",
    "Berlin": "Jerman", "Roma": "Italia", "Madrid": "Spanyol",
    "London": "Inggris", "Moskow": "Rusia", "Kairo": "Mesir",
    "Bangkok": "Thailand", "Hanoi": "Vietnam", "Manila": "Filipina",
    "Teheran": "Iran", "Baghdad": "Irak", "Ankara": "Turki",
    "Athena": "Yunani", "Lisbon": "Portugal", "Wina": "Austria",
    "Bern": "Swiss", "Oslo": "Norwegia", "Stockholm": "Swedia",
    "Helsinki": "Finlandia", "Warsawa": "Polandia", "Dublin": "Irlandia",
    "Havana": "Kuba", "Lima": "Peru", "Santiago": "Chili",
    "Nairobi": "Kenya", "Rabat": "Maroko", "Islamabad": "Pakistan",
    "Seoul": "Korea", "Beijing": "China", "Canberra": "Australia",
}
for kota, negara in COUNTRY_SINGLE.items():
    add("normal", negara, f"Negara yang beribu kota {kota}")


# ═══════════════ EKSPANSI NORMAL 3 ═══════════════
NORMAL3 = [
    ("KATODA", "Elektrode kutub negatif"),
    ("ANODA", "Elektrode kutub positif"),
    ("ISOLATOR", "Bahan penghambat listrik/panas"),
    ("KONDUKTOR", "Bahan penghantar listrik/panas"),
    ("SEKERING", "Pengaman arus listrik berlebih"),
    ("SAKELAR", "Alat pemutus dan penyambung listrik"),
    ("KABEL", "Penghantar listrik berselubung"),
    ("ANTENA", "Penangkap gelombang sinyal"),
    ("SONAR", "Pendeteksi objek dengan gelombang suara"),
    ("RADAR", "Pendeteksi objek dengan gelombang radio"),
    ("LASER", "Berkas cahaya terfokus kuat"),
    ("PRISMA", "Kaca pengurai cahaya menjadi warna"),
    ("LENSA", "Kaca pengumpul atau penyebar cahaya"),
    ("CERMIN", "Benda pemantul bayangan"),
    ("FOKUS", "Titik pertemuan berkas cahaya"),
    ("BAYANGAN", "Gelap akibat cahaya terhalang"),
    ("KATULISTIWA", "Garis khayal pembagi bumi utara-selatan"),
    ("KUTUB", "Ujung utara atau selatan bumi"),
    ("TROPIS", "Iklim panas di sekitar khatulistiwa"),
    ("SUBTROPIS", "Iklim antara tropis dan sedang"),
    ("DELTA", "Endapan di muara sungai"),
    ("TELUK", "Laut yang menjorok ke daratan"),
    ("SELAT", "Laut sempit antara dua pulau"),
    ("SEMENANJUNG", "Daratan menjorok ke laut"),
    ("TANJUNG", "Ujung daratan yang menjorok ke laut"),
    ("ARKIPELAGO", "Gugusan kepulauan"),
    ("KALDERA", "Kawah besar bekas letusan"),
    ("LAHAR", "Lumpur panas letusan gunung"),
    ("GEISER", "Semburan air panas dari tanah"),
    ("FOSIL", "Sisa makhluk purba membatu"),
]
for a, c in NORMAL3:
    add("normal", a, c)


# ═══════════════ EKSPANSI HARD 3 ═══════════════
HARD3 = [
    ("GEOMETRI", "Cabang matematika tentang bangun"),
    ("ALJABAR", "Cabang matematika dengan simbol/variabel"),
    ("TRIGONOMETRI", "Ilmu ukur sudut segitiga"),
    ("STATISTIKA", "Ilmu pengumpulan dan analisis data"),
    ("LOGARITMA", "Kebalikan dari perpangkatan"),
    ("INTEGRAL", "Operasi kebalikan turunan"),
    ("DIAMETER", "Garis tengah lingkaran"),
    ("RADIUS", "Jari-jari lingkaran"),
    ("HIPOTENUSA", "Sisi miring segitiga siku-siku"),
    ("PARABOLA", "Kurva berbentuk lengkung simetris"),
    ("VEKTOR", "Besaran berarah dan bernilai"),
    ("SKALAR", "Besaran yang hanya bernilai"),
    ("KONSTANTA", "Nilai tetap dalam persamaan"),
    ("VARIABEL", "Nilai yang dapat berubah"),
    ("KOEFISIEN", "Angka pengali variabel"),
    ("FAKTORIAL", "Perkalian bilangan berurutan ke bawah"),
    ("PERMUTASI", "Susunan berurut yang memperhatikan urutan"),
    ("KOMBINASI", "Pemilihan tanpa memperhatikan urutan"),
    ("PROBABILITAS", "Ukuran kemungkinan kejadian"),
    ("HISTOGRAM", "Diagram batang untuk data frekuensi"),
    ("MEDIAN", "Nilai tengah dari data terurut"),
    ("MODUS", "Nilai yang paling sering muncul"),
    ("MEAN", "Nilai rata-rata data"),
    ("ASIMTOT", "Garis yang didekati kurva tak terhingga"),
    ("KUADRAT", "Hasil pangkat dua"),
    ("PANGKAT", "Perkalian bilangan dengan dirinya"),
    ("AKAR", "Kebalikan dari pangkat"),
    ("PECAHAN", "Bilangan pembagian dua bagian"),
    ("DESIMAL", "Bilangan dengan koma"),
    ("BILANGAN", "Lambang untuk menyatakan jumlah"),
]
for a, c in HARD3:
    add("hard", a, c)


# ═══════════════ EKSPANSI NIGHTMARE 3 ═══════════════
NIGHTMARE3 = [
    ("TERMOLUMINESENSI", "Pancaran cahaya akibat pemanasan"),
    ("PIEZOELEKTRIK", "Listrik dari tekanan mekanis"),
    ("SUPERKONDUKTOR", "Penghantar tanpa hambatan pada suhu rendah"),
    ("MAGNETOHIDRODINAMIKA", "Dinamika fluida bermuatan dalam medan magnet"),
    ("SPEKTROFOTOMETER", "Alat ukur serapan cahaya zat"),
    ("INTERFEROMETER", "Alat ukur presisi berbasis interferensi"),
    ("OSILOSKOP", "Alat penampil bentuk gelombang listrik"),
    ("KALORIMETER", "Alat pengukur kalor reaksi"),
    ("MANOMETER", "Alat pengukur tekanan gas"),
    ("HIGROMETER", "Alat pengukur kelembapan udara"),
    ("ANEMOMETER", "Alat pengukur kecepatan angin"),
    ("GALVANOMETER", "Alat pendeteksi arus listrik kecil"),
    ("ELEKTROFORESIS", "Pemisahan molekul dengan medan listrik"),
    ("SENTRIFUGASI", "Pemisahan zat dengan putaran cepat"),
    ("DESTILASI", "Pemurnian cairan lewat penguapan"),
    ("KRISTALISASI", "Pembentukan kristal dari larutan"),
    ("POLIMERISASI", "Penggabungan monomer jadi polimer"),
    ("HIDROLISIS", "Penguraian zat oleh air"),
    ("FOTODISOSIASI", "Penguraian molekul oleh cahaya"),
    ("TERMOKIMIA", "Kajian kalor dalam reaksi kimia"),
    ("ELEKTRONEGATIVITAS", "Kecenderungan atom menarik elektron"),
    ("STEREOKIMIA", "Kajian susunan ruang molekul"),
    ("BIOKATALIS", "Enzim yang mempercepat reaksi hayati"),
    ("PATOGEN", "Organisme penyebab penyakit"),
    ("EPIDEMIOLOGI", "Ilmu penyebaran penyakit di populasi"),
    ("IMUNOLOGI", "Ilmu tentang sistem kekebalan"),
    ("FARMAKOLOGI", "Ilmu tentang khasiat obat"),
    ("TOKSIKOLOGI", "Ilmu tentang racun"),
    ("NEUROLOGI", "Ilmu tentang saraf"),
    ("KARDIOLOGI", "Ilmu tentang jantung"),
    ("ONKOLOGI", "Ilmu tentang kanker"),
    ("RADIOLOGI", "Ilmu pencitraan medis dengan radiasi"),
    ("GENOMIKA", "Kajian keseluruhan gen organisme"),
    ("PROTEOMIKA", "Kajian keseluruhan protein"),
    ("FILOGENETIK", "Kajian hubungan evolusi makhluk"),
    ("BIODIVERSITAS", "Keanekaragaman hayati"),
    ("EKOLOGI", "Ilmu hubungan organisme dan lingkungan"),
    ("ETOLOGI", "Ilmu tentang perilaku hewan"),
    (" ", ""),
]
for a, c in NIGHTMARE3:
    if a.strip() and c:
        add("nightmare", a, c)


# ═══════════════ EKSPANSI 4 — angka/hari/bulan Inggris (EASY) ═══════════════
NUM_EN = {
    "satu": "one", "dua": "two", "tiga": "three", "empat": "four",
    "lima": "five", "enam": "six", "tujuh": "seven", "delapan": "eight",
    "sembilan": "nine", "sepuluh": "ten", "sebelas": "eleven", "dua belas": "twelve",
    "tiga belas": "thirteen", "dua puluh": "twenty", "seratus": "hundred",
    "seribu": "thousand", "sejuta": "million", "nol": "zero",
}
for indo, eng in NUM_EN.items():
    add("easy", eng, f"Bahasa Inggris angka '{indo}'")

DAY_EN = {
    "Senin": "Monday", "Selasa": "Tuesday", "Rabu": "Wednesday",
    "Kamis": "Thursday", "Jumat": "Friday", "Sabtu": "Saturday", "Minggu": "Sunday",
}
for indo, eng in DAY_EN.items():
    add("easy", eng, f"Bahasa Inggris hari {indo}")

MONTH_EN = {
    "Januari": "January", "Februari": "February", "Maret": "March",
    "April": "April", "Mei": "May", "Juni": "June", "Juli": "July",
    "Agustus": "August", "September": "September", "Oktober": "October",
    "November": "November", "Desember": "December",
}
for indo, eng in MONTH_EN.items():
    add("easy", eng, f"Bahasa Inggris bulan {indo}")


# ═══════════════ EKSPANSI 4 — bilingual tambahan (EASY) ═══════════════
EN4 = {
    "guru sekolah": "teacher", "polisi": "police", "tentara": "soldier",
    "pemadam": "firefighter", "tukang pos": "postman", "pelaut": "sailor",
    "pilot": "pilot", "penulis": "writer", "pelukis": "painter", "penyanyi": "singer",
    "penari": "dancer", "pemburu": "hunter", "pedagang": "merchant", "pembeli": "buyer",
    "hakim": "judge", "pengacara": "lawyer", "insinyur": "engineer", "ilmuwan": "scientist",
    "presiden negara": "president", "raja kerajaan": "king", "ratu kerajaan": "queen",
    "pangeran": "prince", "putri": "princess", "ksatria": "knight", "pelayan": "waiter",
    "tukang roti": "baker", "tukang daging": "butcher", "tukang kayu": "carpenter",
    "tukang ledeng": "plumber", "montir": "mechanic", "sopir": "driver",
    "kepala": "head", "wajah": "face", "tenggorokan": "throat", "rahang": "jaw",
    "kuku": "nail", "telapak": "palm", "jempol": "thumb", "betis": "calf",
    "paha": "thigh", "pinggang": "waist", "pinggul": "hip", "dada": "chest",
    "gembira": "glad", "letih": "tired", "lapar": "hungry", "haus": "thirsty",
    "kenyang": "full", "sibuk": "busy", "bosan": "bored", "malu": "shy",
    "bangga": "proud", "cemburu": "jealous", "sombong": "arrogant", "sopan": "polite",
    "ramah": "friendly", "sabar": "patient", "tenang": "calm", "bijak": "wise",
    "jujur": "honest", "setia": "loyal", "murah hati": "generous", "pelit": "greedy",
    "nyata": "real", "palsu": "fake", "penting": "important", "berbahaya": "dangerous",
    "aman": "safe", "gratis": "free", "mahal": "expensive", "murah": "cheap",
    "berguna": "useful", "kosong": "empty", "penuh": "full", "basah": "wet",
    "kering": "dry", "tajam": "sharp", "tumpul": "blunt", "lembut": "soft",
    "keras": "hard", "halus": "smooth", "kasar": "rough", "berat": "heavy",
    "membangun": "build", "menghancurkan": "destroy", "memperbaiki": "repair",
    "memasak": "cook", "membersihkan": "clean", "mencuci": "wash", "menanam": "plant",
    "memanen": "harvest", "menggambar": "draw", "melukis": "paint", "memotong": "cut",
    "mengukur": "measure", "menimbang": "weigh", "menghitung": "count", "menjaga": "guard",
    "menolong": "help", "menyelamatkan": "save", "menyembunyikan": "hide", "menemukan": "find",
    "kehilangan": "lose", "menang": "win", "memberi": "give", "menerima": "receive",
    "meminjam": "borrow", "mengembalikan": "return", "mengirim": "send", "membawa": "bring",
}
for indo, eng in EN4.items():
    if eng.isalpha():
        add("easy", eng, f"Bahasa Inggris dari '{indo}'")


# ═══════════════ GEOGRAFI SUPERLATIF — NORMAL ═══════════════
GEO = [
    ("EVEREST", "Gunung tertinggi di dunia"),
    ("PASIFIK", "Samudra terluas di dunia"),
    ("ATLANTIK", "Samudra terluas kedua di dunia"),
    ("HINDIA", "Samudra di sebelah selatan Asia"),
    ("ARKTIK", "Samudra di kutub utara"),
    ("ASIA", "Benua terluas di dunia"),
    ("EROPA", "Benua tempat Prancis dan Jerman"),
    ("AFRIKA", "Benua tempat Gurun Sahara"),
    ("ANTARTIKA", "Benua es di kutub selatan"),
    ("SAHARA", "Gurun pasir terluas di dunia"),
    ("RUSIA", "Negara terluas di dunia"),
    ("VATIKAN", "Negara terkecil di dunia"),
    ("HIMALAYA", "Pegunungan tertinggi di dunia"),
    ("AMAZON", "Hutan hujan terluas di dunia"),
    ("GREENLAND", "Pulau terbesar di dunia"),
    ("BOROBUDUR", "Candi Buddha terbesar di Indonesia"),
    ("PRAMBANAN", "Candi Hindu terbesar di Indonesia"),
    ("KRAKATAU", "Gunung api terkenal di Selat Sunda"),
    ("MERAPI", "Gunung api paling aktif di Jawa"),
    ("TOBA", "Danau vulkanik terbesar di Indonesia"),
    ("KAPUAS", "Sungai terpanjang di Indonesia"),
    ("PUNCAKJAYA", "Puncak tertinggi di Indonesia"),
]
for a, c in GEO:
    add("normal", a, c)


# ═══════════════ EKSPANSI HARD 4 (biologi/anatomi) ═══════════════
HARD4 = [
    ("KORNEA", "Selaput bening di depan mata"),
    ("RETINA", "Selaput penerima cahaya di mata"),
    ("PUPIL", "Celah hitam tempat cahaya masuk mata"),
    ("IRIS", "Selaput berwarna pada mata"),
    ("KOKLEA", "Rumah siput di telinga dalam"),
    ("GENDANG", "Selaput getar di telinga"),
    ("TRAKEA", "Batang tenggorokan saluran napas"),
    ("BRONKUS", "Cabang batang tenggorokan"),
    ("ALVEOLUS", "Kantong udara di paru-paru"),
    ("DIAFRAGMA", "Otot pernapasan di bawah paru"),
    ("ESOFAGUS", "Kerongkongan penyalur makanan"),
    ("DUODENUM", "Usus dua belas jari"),
    ("PANKREAS", "Kelenjar penghasil insulin"),
    ("EMPEDU", "Cairan hati pencerna lemak"),
    ("NEFRON", "Unit penyaring pada ginjal"),
    ("NEURON", "Sel penghantar impuls pada sistem saraf"),
    ("SINAPSIS", "Celah sambungan antarneuron"),
    ("SEREBRUM", "Otak besar pusat berpikir"),
    ("SEREBELUM", "Otak kecil pengatur keseimbangan"),
    ("MEDULA", "Sumsum penghubung otak dan tulang belakang"),
    ("PLASENTA", "Ari-ari penghubung ibu dan janin"),
    ("EMBRIO", "Bakal janin tahap awal"),
    ("ZIGOT", "Sel hasil pembuahan"),
    ("GAMET", "Sel kelamin jantan atau betina"),
    ("MEIOSIS", "Pembelahan sel kelamin"),
    ("MITOSIS", "Pembelahan sel tubuh"),
    ("KLOROPLAS", "Organel tempat fotosintesis"),
    ("STOMATA", "Mulut daun tempat pertukaran gas"),
    ("XILEM", "Pembuluh pengangkut air pada tumbuhan"),
    ("FLOEM", "Pembuluh pengangkut makanan pada tumbuhan"),
]
for a, c in HARD4:
    add("hard", a, c)


# ═══════════════ EKSPANSI NIGHTMARE 4 ═══════════════
NIGHTMARE4 = [
    ("PARTENOGENESIS", "Perkembangbiakan tanpa pembuahan"),
    ("VIVIPAR", "Berkembang biak dengan melahirkan"),
    ("OVIPAR", "Berkembang biak dengan bertelur"),
    ("OVOVIVIPAR", "Bertelur sekaligus melahirkan"),
    ("HERMAFRODIT", "Berkelamin ganda"),
    ("VESTIGIAL", "Organ sisa yang menyusut fungsinya"),
    ("MIMIKRI", "Peniruan bentuk untuk perlindungan"),
    ("KAMUFLASE", "Penyamaran dengan lingkungan"),
    ("HIBERNASI", "Tidur panjang saat musim dingin"),
    ("ESTIVASI", "Tidur panjang saat musim kemarau"),
    ("MIGRASI", "Perpindahan musiman hewan"),
    ("EKOLOKASI", "Navigasi dengan pantulan suara"),
    ("FEROMON", "Zat kimia pemikat antarhewan"),
    ("KARNIVORA", "Pemakan daging"),
    ("HERBIVORA", "Pemakan tumbuhan"),
    ("OMNIVORA", "Pemakan segala"),
    ("DEKOMPOSER", "Pengurai bangkai dan sisa"),
    ("PRODUSEN", "Organisme pembuat makanan sendiri"),
    ("AUTOTROF", "Organisme penyusun makanan sendiri"),
    ("HETEROTROF", "Organisme bergantung makanan lain"),
    ("PLANKTON", "Organisme mikro pengapung di air"),
    ("FITOPLANKTON", "Plankton tumbuhan berfotosintesis"),
    ("ZOOPLANKTON", "Plankton hewan mikroskopis"),
    ("BENTOS", "Organisme dasar perairan"),
    ("NEKTON", "Hewan perenang aktif di air"),
    ("GAMETOFIT", "Fase penghasil gamet pada tumbuhan"),
    ("SPOROFIT", "Fase penghasil spora pada tumbuhan"),
    ("RIZOMA", "Batang menjalar di dalam tanah"),
    ("STOLON", "Batang menjalar di atas tanah"),
    ("TUBER", "Umbi batang penyimpan makanan"),
    ("KAMBIUM", "Jaringan pertumbuhan batang"),
    ("EPIDERMIS", "Jaringan pelindung terluar"),
    ("PARENKIM", "Jaringan dasar pengisi tumbuhan"),
    ("KOLENKIM", "Jaringan penguat tumbuhan muda"),
    ("SKLERENKIM", "Jaringan penguat tumbuhan dewasa"),
    ("TRANSPIRASI", "Penguapan air lewat daun"),
    ("GUTASI", "Pengeluaran air berupa tetesan pada daun"),
    ("IMBIBISI", "Penyerapan air oleh biji"),
    ("VERNALISASI", "Perlakuan dingin untuk memicu pembungaan"),
    ("ETIOLASI", "Pertumbuhan cepat pucat tanpa cahaya"),
]
for a, c in NIGHTMARE4:
    add("nightmare", a, c)


# ═══════════════ EKSPANSI 5 — bilingual tambahan (EASY) ═══════════════
EN5 = {
    "gunting kuku": "clipper", "cukur": "razor", "sisir": "comb", "bedak": "powder",
    "parfum": "perfume", "lipstik": "lipstick", "kaca mata": "glasses", "jam tangan": "watch",
    "koper": "suitcase", "ransel": "backpack", "peta jalan": "map", "tiket": "ticket",
    "paspor": "passport", "kamera": "camera", "ponsel": "phone", "komputer": "computer",
    "papan ketik": "keyboard", "tetikus": "mouse", "layar": "screen", "pengeras suara": "speaker",
    "penyuara kuping": "headphone", "cakram": "disk", "berkas": "file", "map dokumen": "folder",
    "jaringan": "network", "sandi": "password", "surel": "email", "situs": "website",
    "peramban": "browser", "unduhan": "download", "unggahan": "upload", "gawai": "gadget",
    "roket": "rocket", "satelit buatan": "satellite", "planet": "planet", "komet ekor": "comet",
    "teleskop": "telescope", "mikroskop": "microscope", "magnet batang": "magnet",
    "baterai kering": "battery", "kabel listrik": "cable", "colokan": "plug", "sakelar": "switch",
    "obeng": "screwdriver", "kunci inggris": "wrench", "tang": "pliers", "bor": "drill",
    "sekop": "shovel", "garu": "rake", "selang": "hose", "keran": "faucet",
    "pipa air": "pipe", "genteng": "roof", "batu bata": "brick", "semen": "cement",
    "beton": "concrete", "pagar besi": "fence", "gerbang": "gate", "kunci gembok": "padlock",
    "engsel": "hinge", "sekrup": "screw", "mur": "nut", "baut": "bolt",
    "gunung salju": "mountain", "bukit": "hill", "tebing": "cliff", "jurang": "ravine",
    "rawa": "swamp", "padang rumput": "meadow", "sabana rumput": "savanna", "tundra": "tundra",
    "hutan lebat": "jungle", "belantara": "wilderness", "ngarai": "canyon", "gletser": "glacier",
    "petir menyambar": "lightning", "guruh": "thunder", "pelangi warna": "rainbow",
    "embun beku": "frost", "hujan es": "hail", "topan": "typhoon", "angin puyuh": "tornado",
    "gempa bumi": "earthquake", "letusan": "eruption", "banjir bandang": "flood", "longsor": "landslide",
    "sarang lebah": "hive", "jaring laba": "web", "kepompong": "cocoon", "telur burung": "egg",
    "bulu domba": "wool", "kulit ular": "scale", "tanduk rusa": "antler", "gading gajah": "tusk",
    "cakar elang": "claw", "taring": "fang", "moncong": "snout", "ekor kuda": "tail",
    "mahkota raja": "crown", "takhta": "throne", "tongkat kerajaan": "scepter", "jubah": "robe",
    "baju zirah": "armor", "helm perang": "helmet", "panah busur": "arrow", "ketapel": "sling",
}
for indo, eng in EN5.items():
    if eng.isalpha():
        add("easy", eng, f"Bahasa Inggris dari '{indo}'")


# ═══════════════ ZODIAK — NORMAL ═══════════════
ZODIAC = [
    ("ARIES", "domba jantan"), ("TAURUS", "banteng"), ("GEMINI", "si kembar"),
    ("CANCER", "kepiting"), ("LEO", "singa"), ("VIRGO", "sang perawan"),
    ("LIBRA", "timbangan"), ("SCORPIO", "kalajengking"), ("SAGITARIUS", "pemanah"),
    ("CAPRICORN", "kambing laut"), ("AQUARIUS", "pembawa air"), ("PISCES", "ikan"),
]
for a, sym in ZODIAC:
    add("normal", a, f"Zodiak berlambang {sym}")


# ═══════════════ IBU KOTA TAMBAHAN (ejaan stabil) — NORMAL ═══════════════
CAPITALS2 = {
    "Tunisia": "Tunis", "Libya": "Tripoli", "Yordania": "Amman",
    "Lebanon": "Beirut", "Qatar": "Doha", "Afghanistan": "Kabul",
    "Azerbaijan": "Baku", "Belarus": "Minsk", "Bulgaria": "Sofia",
    "Kroasia": "Zagreb", "Latvia": "Riga", "Lituania": "Vilnius",
    "Estonia": "Tallinn", "Sri Lanka": "Kolombo", "Nepal": "Kathmandu",
    "Ceko": "Praha", "Rumania": "Bukarest", "Serbia": "Beograd",
    "Kuwait": "Kuwait", "Georgia": "Tbilisi", "Armenia": "Yerevan",
}
for negara, kota in CAPITALS2.items():
    add("normal", kota, f"Ibu kota negara {negara}")


# ═══════════════ EKSPANSI NORMAL 5 ═══════════════
NORMAL5 = [
    ("FOTOGRAFI", "Seni membuat gambar dengan kamera"),
    ("SINEMATOGRAFI", "Seni pembuatan film"),
    ("KOREOGRAFI", "Seni menyusun gerak tari"),
    ("KALIGRAFI", "Seni menulis huruf indah"),
    ("ARSITEKTUR", "Seni merancang bangunan"),
    ("MOZAIK", "Seni tempel kepingan warna-warni"),
    ("PAHATAN", "Seni ukir tiga dimensi"),
    ("KERAMIK", "Kerajinan dari tanah liat dibakar"),
    ("ANYAMAN", "Kerajinan menjalin bambu/rotan"),
    ("TENUN", "Kain hasil menjalin benang"),
    ("SULAM", "Hiasan benang pada kain"),
    ("UKIRAN", "Hiasan pahat pada kayu"),
    ("PANTOMIM", "Seni peran tanpa suara"),
    ("OPERA", "Drama musik dengan nyanyian"),
    ("ORKESTRA", "Kelompok besar pemain musik"),
    ("DIRIGEN", "Pemimpin orkestra"),
    ("MELODI", "Rangkaian nada lagu"),
    ("HARMONI", "Perpaduan nada yang selaras"),
    ("RITME", "Pola ketukan dalam musik"),
    ("TEMPO", "Cepat lambatnya lagu"),
    ("OKTAF", "Rentang delapan nada"),
    ("PARTITUR", "Lembar notasi musik"),
    ("PROSA", "Karangan bebas tak terikat rima"),
    ("PROLOG", "Kata pembuka sebuah cerita"),
    ("EPILOG", "Kata penutup sebuah cerita"),
    ("SINOPSIS", "Ringkasan isi cerita"),
    ("PROTAGONIS", "Tokoh utama dalam cerita"),
    ("ANTAGONIS", "Tokoh penentang dalam cerita"),
    ("ALEGORI", "Cerita kiasan bermakna tersirat"),
    ("FABEL", "Cerita dengan tokoh binatang"),
]
for a, c in NORMAL5:
    add("normal", a, c)


# ═══════════════ EKSPANSI HARD 5 (unsur & kimia) ═══════════════
ELEMENTS2 = {
    "B": "Boron", "Ne": "Neon", "Ar": "Argon", "Kr": "Kripton",
    "Xe": "Xenon", "Ni": "Nikel", "Co": "Kobalt", "Mn": "Mangan",
    "Cr": "Krom", "Sn": "Timah", "I": "Iodin", "Br": "Bromin",
    "Ba": "Barium", "Pt": "Platina", "W": "Wolfram", "Ti": "Titanium",
}
for sym, nama in ELEMENTS2.items():
    add("hard", nama, f"Unsur kimia berlambang {sym}")

HARD5 = [
    ("EKSOTERM", "Reaksi yang melepas kalor"),
    ("ENDOTERM", "Reaksi yang menyerap kalor"),
    ("EKSOTERMIK", "Bersifat melepas panas"),
    ("VALENSI", "Daya ikat atom suatu unsur"),
    ("ORBITAL", "Daerah kebolehjadian elektron"),
    ("IONISASI", "Pembentukan ion dari atom"),
    ("KATION", "Ion bermuatan positif"),
    ("ANION", "Ion bermuatan negatif"),
    ("MOLARITAS", "Kepekatan larutan per liter"),
    ("TITRASI", "Penentuan kadar zat dengan larutan baku"),
    ("INDIKATOR", "Zat penanda perubahan pH"),
    ("KOLOID", "Campuran zat berukuran sedang"),
    ("EMULSI", "Campuran dua cairan tak menyatu"),
    ("KATALITIK", "Bersifat mempercepat reaksi kimia"),
    ("ISOMER", "Senyawa sama rumus beda struktur"),
    ("HIDROKARBON", "Senyawa karbon dan hidrogen"),
    ("ALKOHOL", "Senyawa organik bergugus hidroksil"),
    ("ALDEHIDA", "Senyawa organik bergugus karbonil ujung"),
    ("ESTER", "Senyawa beraroma buah"),
    ("KARBOHIDRAT", "Zat gizi sumber tenaga utama"),
]
for a, c in HARD5:
    add("hard", a, c)


# ═══════════════ EKSPANSI NIGHTMARE 5 ═══════════════
NIGHTMARE5 = [
    ("ELEKTROENSEFALOGRAF", "Alat perekam gelombang otak"),
    ("MAGNETOMETER", "Alat pengukur kuat medan magnet"),
    ("DENSITOMETER", "Alat pengukur kerapatan optik"),
    ("REFRAKTOMETER", "Alat pengukur indeks bias"),
    ("POLARIMETER", "Alat pengukur putaran bidang polarisasi"),
    ("KOLORIMETER", "Alat pengukur intensitas warna larutan"),
    ("VISKOMETER", "Alat pengukur kekentalan cairan"),
    ("TAKOMETER", "Alat pengukur kecepatan putar"),
    ("ALTIMETER", "Alat pengukur ketinggian"),
    ("ODOMETER", "Alat pengukur jarak tempuh kendaraan"),
    ("KRONOMETER", "Jam presisi tinggi untuk navigasi"),
    ("SEISMOMETER", "Sensor pendeteksi getaran bumi"),
    ("BOLOMETER", "Alat pengukur energi radiasi"),
    ("KALORIMETRI", "Pengukuran kalor reaksi"),
    ("TERMOKOPEL", "Sensor suhu dua logam berbeda"),
    ("SUPERFLUIDITAS", "Sifat cairan mengalir tanpa gesekan"),
    ("KRIOGENIK", "Teknologi bersuhu sangat rendah"),
    ("PLASMONIK", "Kajian gelombang elektron permukaan logam"),
    ("FOTONIKA", "Ilmu pemanfaatan partikel cahaya"),
    ("SPINTRONIK", "Elektronika berbasis putaran elektron"),
    ("KUANTISASI", "Pembatasan besaran menjadi paket diskret"),
    ("SUPERPOSISI", "Keadaan gabungan dua kondisi kuantum"),
    ("DEKOHERENSI", "Hilangnya sifat kuantum sistem"),
    ("SINGULARITAS", "Titik kerapatan tak hingga lubang hitam"),
    ("REDSHIFT", "Pergeseran cahaya ke merah galaksi menjauh"),
    ("KOSMOGONI", "Teori asal usul alam semesta"),
    ("HELIOPAUSE", "Batas pengaruh angin matahari"),
    ("MAGNITUDO", "Ukuran kecerlangan bintang"),
    ("LUMINOSITAS", "Daya pancar total sebuah bintang"),
    ("PARSEK", "Satuan jarak astronomi"),
    ("PERIHELION", "Titik terdekat orbit ke matahari"),
    ("APHELION", "Titik terjauh orbit dari matahari"),
    ("EKLIPTIKA", "Bidang orbit bumi mengelilingi matahari"),
    ("PRESESI", "Gerak gasing sumbu rotasi bumi"),
]
for a, c in NIGHTMARE5:
    add("nightmare", a, c)


# ═══════════════ EKSPANSI 6 — KLU MENARIK (teka-teki & trivia) ═══════════════
# EASY: teka-teki / personifikasi (jawaban tetap satu & jelas)
FUN_EASY = [
    ("SISIR", "Punya banyak gigi tapi tak pernah menggigit; perapi rambut"),
    ("LUBANG", "Makin banyak kau ambil dariku, aku makin besar"),
    ("BOTOL", "Punya leher tapi tak berkepala; wadah air minummu"),
    ("LILIN", "Makin lama menyala tubuhku makin pendek; penerang kala mati lampu"),
    ("BUNGLON", "Reptil yang pandai berganti warna kulit"),
    ("BEO", "Burung yang bisa menirukan ucapan manusia"),
    ("BALON", "Makin banyak diisi udara aku makin besar, lalu dor!"),
    ("LAYANGAN", "Mainan yang terbang tinggi ditarik seutas benang"),
    ("GERGAJI", "Bergigi tajam berbaris rapi, si pemotong kayu"),
    ("SEDOTAN", "Batang berlubang untuk menyeruput minuman"),
    ("TERMOS", "Botol ajaib penjaga air tetap panas atau dingin"),
    ("KUNANG", "Serangga mungil yang menyala di gelap malam"),
    ("CICAK", "Reptil kecil perayap dinding, pemburu nyamuk"),
    ("KEONG", "Siput yang membawa rumahnya ke mana-mana"),
    ("BEKICOT", "Siput darat besar berlendir"),
    ("LIFT", "Kotak naik-turun pengantar orang antarlantai"),
    ("KUMIS", "Rambut yang tumbuh di atas bibir"),
    ("JENGGOT", "Rambut yang tumbuh di dagu"),
    ("JAKUN", "Tonjolan yang menonjol di leher pria"),
    ("GASING", "Mainan yang berputar di atas tanah bila dipilin"),
    ("YOYO", "Mainan naik-turun di ujung benang"),
    ("KELERENG", "Bola kaca kecil untuk permainan anak"),
    ("PETASAN", "Benda kecil yang meletus keras saat dibakar"),
    ("PERANGKO", "Cap kecil ditempel di surat sebagai bayaran pos"),
    ("KOMPAS", "Penunjuk arah yang jarumnya selalu ke utara"),
]
for a, c in FUN_EASY:
    add("easy", a, c)

# NORMAL: trivia hewan & alat unik
FUN_NORMAL = [
    ("STETOSKOP", "Alat dokter untuk mendengar detak jantung"),
    ("MERCUSUAR", "Menara bercahaya penunjuk jalan kapal di malam gelap"),
    ("PERISKOP", "Teropong kapal selam untuk mengintip permukaan"),
    ("KALEIDOSKOP", "Teropong mainan berisi pola warna simetris"),
    ("PARASUT", "Payung raksasa penyelamat penerjun dari langit"),
    ("PENDULUM", "Bandul ayun penjaga irama jam tua"),
    ("PLATIPUS", "Mamalia aneh berparuh bebek yang bertelur"),
    ("KOALA", "Mamalia berkantung pemalas pelahap daun eukaliptus"),
    ("PANDA", "Beruang hitam-putih pemakan bambu dari China"),
    ("FLAMINGO", "Burung merah muda yang berdiri dengan satu kaki"),
    ("PIRANHA", "Ikan bergigi tajam pemangsa dari Sungai Amazon"),
    ("ANAKONDA", "Ular pembelit raksasa penghuni rawa Amazon"),
    ("TARANTULA", "Laba-laba besar berbulu yang menyeramkan"),
    ("CENDERAWASIH", "Burung surga nan cantik dari tanah Papua"),
    ("KASUARI", "Burung besar tak bisa terbang dari Papua"),
    ("AKSOLOTL", "Salamander yang bisa menumbuhkan kembali anggota tubuh"),
    ("TRENGGILING", "Mamalia bersisik yang menggulung seperti bola"),
    ("KOLIBRI", "Burung mungil yang bisa terbang mundur"),
    ("BELALANG", "Serangga hijau pelompat jauh"),
]
for a, c in FUN_NORMAL:
    add("normal", a, c)

# HARD/NIGHTMARE: sains & pikiran, dibingkai menarik
FUN_HARD = [
    ("INSOMNIA", "Penyakit gagal tidur di malam hari"),
    ("AMNESIA", "Kondisi kehilangan ingatan"),
    ("FOBIA", "Rasa takut berlebihan yang tak masuk akal"),
    ("VERTIGO", "Sensasi dunia berputar dan oleng"),
    ("MIGRAIN", "Sakit kepala berdenyut hebat sebelah"),
    ("ALERGI", "Reaksi tubuh berlebihan terhadap zat tertentu"),
    ("HALUSINASI", "Melihat atau mendengar yang tak nyata"),
    ("ENDORFIN", "Hormon bahagia pereda rasa sakit"),
    ("DOPAMIN", "Zat otak pemicu rasa senang dan semangat"),
    ("MELATONIN", "Hormon yang mengundang rasa kantuk"),
    ("SEROTONIN", "Hormon pengatur suasana hati"),
    ("PLASEBO", "Obat kosong yang menyembuhkan karena sugesti"),
    ("REFLEKS", "Gerak tubuh spontan tanpa disadari"),
    ("METABOLISME", "Dapur kimia tubuh pengolah makanan jadi energi"),
    ("HIBERNASI", "Tidur panjang beruang menembus musim dingin"),
]
for a, c in FUN_HARD:
    add("hard", a, c)

FUN_NIGHTMARE = [
    ("DEJAVU", "Perasaan pernah mengalami sesuatu yang baru terjadi"),
    ("PAREIDOLIA", "Melihat wajah pada benda mati seperti awan"),
    ("SINESTESIA", "Bercampurnya indra: 'melihat' warna dari suara"),
    ("PROPRIOSEPSI", "Indra sadar posisi tubuh tanpa melihat"),
    ("PLASTISITAS", "Kemampuan otak membentuk ulang koneksinya"),
    ("EPIGENETIKA", "Perubahan gen aktif tanpa mengubah DNA"),
    ("TELOMER", "Tudung ujung kromosom yang memendek saat menua"),
    ("APOPTOSIS", "Bunuh diri sel yang terprogram"),
    ("BIORITME", "Jam biologis alami dalam tubuh"),
    ("KIRALITAS", "Sifat molekul yang bayangan cerminnya tak berimpit"),
    ("ANTIMATERI", "Kembaran materi yang saling memusnahkan"),
    ("NEUTRINO", "Partikel hantu yang menembus tubuhmu tiap detik"),
    ("TAKION", "Partikel hipotetis lebih cepat dari cahaya"),
    ("FRAKTAL", "Pola yang berulang serupa di tiap skala"),
    ("ENTANGLEMENT", "Keterkaitan kuantum dua partikel dari jarak jauh"),
]
for a, c in FUN_NIGHTMARE:
    add("nightmare", a, c)


# ═══════════════ EKSPANSI 7 — tembus 2000 (klu hidup) ═══════════════
FUN_EASY7 = [
    ("SENTER", "Lampu genggam penerang saat gelap"),
    ("GAYUNG", "Alat penciduk air saat mandi"),
    ("TIMBA", "Ember bertali penimba air sumur"),
    ("CANGKIR", "Wadah kecil bergagang teman si kopi"),
    ("NAMPAN", "Baki datar pembawa gelas dan piring"),
    ("KESET", "Alas di depan pintu untuk melap kaki"),
    ("GEMBOK", "Kunci gantung pengaman pintu pagar"),
    ("PERANGKAP", "Alat penjebak tikus yang nakal"),
    ("KOREK", "Pemantik api mungil di saku"),
    ("STAPLER", "Penjepret kertas dengan kawat kecil"),
]
for a, c in FUN_EASY7:
    add("easy", a, c)

FUN_NORMAL7 = [
    ("ALMANAK", "Buku penanggalan lengkap dengan ramalan cuaca"),
    ("ENSIKLOPEDIA", "Buku himpunan pengetahuan dari A sampai Z"),
    ("TESAURUS", "Buku kumpulan padanan dan sinonim kata"),
    ("BIOGRAFI", "Kisah hidup seseorang yang ditulis orang lain"),
    ("AUTOBIOGRAFI", "Kisah hidup yang ditulis oleh dirinya sendiri"),
    ("KOMIK", "Cerita bergambar berpanel-panel"),
    ("NUMISMATIK", "Hobi mengoleksi mata uang kuno"),
    ("FILATELI", "Hobi mengoleksi perangko"),
]
for a, c in FUN_NORMAL7:
    add("normal", a, c)

FUN_HARD7 = [
    ("ORNITOLOGI", "Ilmu yang mempelajari burung"),
    ("ENTOMOLOGI", "Ilmu yang mempelajari serangga"),
    ("IKTIOLOGI", "Ilmu yang mempelajari ikan"),
    ("MIKOLOGI", "Ilmu yang mempelajari jamur"),
    ("BOTANI", "Ilmu yang mempelajari tumbuhan"),
    ("ZOOLOGI", "Ilmu yang mempelajari hewan"),
    ("VIROLOGI", "Ilmu yang mempelajari virus"),
    ("ANATOMI", "Ilmu tentang susunan tubuh makhluk hidup"),
]
for a, c in FUN_HARD7:
    add("hard", a, c)

FUN_NIGHTMARE7 = [
    ("SPELEOLOGI", "Ilmu yang mempelajari gua"),
    ("VULKANOLOGI", "Ilmu yang mempelajari gunung berapi"),
    ("OSEANOGRAFI", "Ilmu yang mempelajari lautan"),
    ("METEOROLOGI", "Ilmu yang mempelajari cuaca"),
    ("GRAFOLOGI", "Membaca kepribadian dari tulisan tangan"),
    ("HERPETOLOGI", "Ilmu tentang reptil dan amfibi"),
    ("SITOLOGI", "Ilmu yang mempelajari sel"),
    ("HISTOLOGI", "Ilmu yang mempelajari jaringan tubuh"),
]
for a, c in FUN_NIGHTMARE7:
    add("nightmare", a, c)


# ═══════════════ EKSPANSI 8 — BUDAYA INDONESIA (NORMAL) ═══════════════
BUDAYA = [
    ("SAMAN", "Tari seribu tangan dari Aceh"),
    ("KECAK", "Tari api penuh seruan 'cak' dari Bali"),
    ("PENDET", "Tari penyambutan tamu dari Bali"),
    ("LEGONG", "Tari klasik nan anggun dari Bali"),
    ("JAIPONG", "Tari enerjik khas Jawa Barat"),
    ("SERIMPI", "Tari halus keraton Jawa"),
    ("GAMBYONG", "Tari penyambutan dari Jawa Tengah"),
    ("REOG", "Kesenian topeng singa raksasa dari Ponorogo"),
    ("REMO", "Tari penyambutan khas Jawa Timur"),
    ("TORTOR", "Tari khas suku Batak"),
    ("ZAPIN", "Tari pergaulan khas Melayu"),
    ("CAKALELE", "Tari perang dari Maluku"),
    ("MAENGKET", "Tari syukur panen dari Minahasa"),
    ("YOSPAN", "Tari pergaulan riang dari Papua"),
    ("KERIS", "Senjata tikam khas Jawa yang berlekuk"),
    ("RENCONG", "Senjata tradisional kebanggaan Aceh"),
    ("MANDAU", "Parang khas suku Dayak Kalimantan"),
    ("CELURIT", "Senjata sabit khas Madura"),
    ("KUJANG", "Senjata pusaka khas Sunda"),
    ("BADIK", "Senjata tikam khas Bugis-Makassar"),
    ("GADANG", "Rumah adat Minang beratap tanduk kerbau"),
    ("JOGLO", "Rumah adat Jawa dengan atap tumpang"),
    ("TONGKONAN", "Rumah adat Toraja beratap seperti perahu"),
    ("HONAI", "Rumah adat Papua berbentuk jamur"),
    ("LIMAS", "Rumah adat khas Sumatra Selatan"),
    ("SALUANG", "Alat musik tiup bambu dari Minangkabau"),
    ("SERUNAI", "Alat musik tiup tradisional bersuara melengking"),
    ("REBAB", "Alat musik gesek tradisional berdawai dua"),
    ("KECAPI", "Alat musik petik lembut khas Sunda"),
    ("BONANG", "Deretan gong kecil dalam gamelan"),
    ("ULOS", "Kain tenun sakral khas Batak"),
    ("SONGKET", "Kain tenun bertabur benang emas"),
    ("PECI", "Penutup kepala hitam khas pria Indonesia"),
    ("BLANGKON", "Penutup kepala khas pria Jawa"),
    ("ANGKLUNG", "Alat musik bambu digoyang dari Sunda"),
]
for a, c in BUDAYA:
    add("normal", a, c)


# ═══════════════ EKSPANSI 8 — IBU KOTA DUNIA TAMBAHAN (NORMAL) ═══════════════
CAPITALS3 = {
    "Amerika Serikat": "Washington", "Selandia Baru": "Wellington",
    "Kolombia": "Bogota", "Venezuela": "Caracas", "Ekuador": "Quito",
    "Paraguay": "Asuncion", "Uruguay": "Montevideo", "Suriah": "Damaskus",
    "Belgia": "Brussel", "Denmark": "Kopenhagen", "Islandia": "Reykjavik",
    "Bhutan": "Thimphu", "Ukraina": "Kiev", "Yaman": "Sana",
    "Oman": "Muskat", "Sudan": "Khartum", "Ghana": "Accra",
    "Senegal": "Dakar", "Angola": "Luanda", "Zimbabwe": "Harare",
}
for negara, kota in CAPITALS3.items():
    add("normal", kota, f"Ibu kota negara {negara}")


# ═══════════════ EKSPANSI 8 — MITOLOGI (NORMAL/HARD) ═══════════════
MITOS = [
    ("ZEUS", "Raja para dewa dalam mitologi Yunani"),
    ("HERA", "Ratu para dewa Yunani, istri Zeus"),
    ("POSEIDON", "Dewa penguasa lautan Yunani"),
    ("HADES", "Dewa penguasa dunia bawah Yunani"),
    ("ARES", "Dewa perang dalam mitologi Yunani"),
    ("APOLLO", "Dewa matahari, musik, dan panahan"),
    ("ARTEMIS", "Dewi perburuan dan bulan Yunani"),
    ("APHRODITE", "Dewi cinta dan kecantikan Yunani"),
    ("HERMES", "Dewa utusan berkaki sayap"),
    ("DEMETER", "Dewi panen dan kesuburan Yunani"),
    ("MARS", "Dewa perang dalam mitologi Romawi"),
    ("MEDUSA", "Monster wanita berambut ular"),
    ("MINOTAUR", "Monster berkepala banteng bertubuh manusia"),
    ("PEGASUS", "Kuda bersayap dalam mitologi Yunani"),
    ("CENTAUR", "Makhluk separuh manusia separuh kuda"),
    ("CYCLOPS", "Raksasa bermata satu"),
    ("HYDRA", "Ular raksasa berkepala banyak"),
    ("SPHINX", "Makhluk berkepala manusia bertubuh singa"),
]
for a, c in MITOS:
    add("normal", a, c)


# ═══════════════ EKSPANSI 8 — bilingual verba/sifat (EASY) ═══════════════
EN6 = {
    "melempar": "throw", "menangkap": "catch", "mendorong": "push",
    "menarik": "pull", "menjatuhkan": "drop", "melipat": "fold",
    "merobek": "tear", "menjahit": "sew", "mengikat": "tie",
    "menggali": "dig", "mengubur": "bury", "memetik": "pick",
    "berteriak": "shout", "berbisik": "whisper", "mengunyah": "chew",
    "menelan": "swallow", "meniup": "blow", "bernapas": "breathe",
    "batuk": "cough", "bersin": "sneeze", "menguap": "yawn",
    "mendengkur": "snore", "berenang": "swim", "menyelam": "dive",
    "merangkak": "crawl", "memanjat": "climb", "berputar": "spin",
    "gemetar": "tremble", "jatuh": "fall", "menghitung": "count",
    "gema": "echo", "kabut": "fog", "uap": "steam", "abu": "ash",
    "debu": "dust", "lumpur": "mud", "kerikil": "gravel", "arang": "charcoal",
    "bensin": "gasoline", "racun": "poison", "rempah": "spice",
    "lembap": "damp", "kaku": "stiff", "licin": "slippery", "lengket": "sticky",
    "padat": "solid", "beku": "frozen", "matang": "ripe", "mentah": "raw",
    "busuk": "rotten", "segar": "fresh", "asam": "sour", "pahit": "bitter",
    "asin": "salty", "pedas": "spicy", "manis": "sweet", "gelap": "dark",
    "sempit": "narrow", "luas": "wide", "curam": "steep", "datar": "flat",
    "bulat": "round", "lurus": "straight", "melengkung": "curved", "tajam": "sharp",
    "terang": "bright", "kusam": "dull", "berkilau": "shiny", "buram": "blurry",
    "bising": "noisy", "sunyi": "silent", "hangat": "warm", "sejuk": "cool",
}
for indo, eng in EN6.items():
    if eng.isalpha():
        add("easy", eng, f"Bahasa Inggris dari '{indo}'")


# ═══════════════ EKSPANSI 8 — HARD (istilah lanjutan) ═══════════════
HARD8 = [
    ("SEISMOLOGI", "Ilmu tentang gempa bumi"),
    ("GEOLOGI", "Ilmu tentang lapisan dan batuan bumi"),
    ("MINERALOGI", "Ilmu tentang mineral"),
    ("KLIMATOLOGI", "Ilmu tentang iklim"),
    ("HIDROLOGI", "Ilmu tentang air di bumi"),
    ("EMBRIOLOGI", "Ilmu tentang perkembangan embrio"),
    ("MIKROBIOLOGI", "Ilmu tentang mikroorganisme"),
    ("BAKTERIOLOGI", "Ilmu tentang bakteri"),
    ("EKOSISTEM", "Kesatuan makhluk hidup dan lingkungannya"),
    ("BIOMA", "Wilayah ekosistem besar seperti gurun atau tundra"),
    ("HABITAT", "Tempat tinggal alami makhluk hidup"),
    ("POPULASI", "Kumpulan individu sejenis di satu wilayah"),
    ("KOMUNITAS", "Kumpulan berbagai populasi di satu tempat"),
    ("PREDATOR", "Hewan pemangsa"),
    ("MANGSA", "Hewan yang diburu predator"),
    ("PARASIT", "Makhluk yang hidup merugikan inangnya"),
    ("INANG", "Tempat parasit menumpang hidup"),
    ("RANTAI", "Urutan makan-dimakan dalam ekosistem"),
    ("PIRAMIDA", "Gambaran tingkatan energi ekosistem"),
    ("NICHE", "Peran suatu spesies dalam ekosistem"),
    ("ADAPTASI", "Penyesuaian diri makhluk pada lingkungan"),
    ("SELEKSI", "Penyaringan alam atas yang paling sesuai"),
    ("MUTASI", "Perubahan susunan materi genetik"),
    ("REGENERASI", "Kemampuan menumbuhkan bagian tubuh yang hilang"),
    ("DORMANSI", "Masa istirahat biji atau organisme"),
    ("KLONING", "Penggandaan makhluk secara identik"),
    ("TRANSPLANTASI", "Pencangkokan organ tubuh"),
    ("TRANSFUSI", "Pemindahan darah ke tubuh lain"),
    ("DIAGNOSIS", "Penentuan jenis penyakit"),
    ("PROGNOSIS", "Perkiraan perjalanan penyakit"),
]
for a, c in HARD8:
    add("hard", a, c)


# ═══════════════ EKSPANSI 8 — NIGHTMARE (istilah langka) ═══════════════
NIGHTMARE8 = [
    ("PSIKOLINGUISTIK", "Kajian hubungan bahasa dan pikiran"),
    ("SOSIOLINGUISTIK", "Kajian bahasa dalam masyarakat"),
    ("MORFOLOGI", "Kajian bentuk dan struktur kata"),
    ("FONOLOGI", "Kajian sistem bunyi bahasa"),
    ("SINTAKSIS", "Kajian susunan kalimat"),
    ("SEMANTIK", "Kajian makna kata dan kalimat"),
    ("PRAGMATIK", "Kajian bahasa sesuai konteks"),
    ("ETIMOLOGI", "Kajian asal usul kata"),
    ("LEKSIKOGRAFI", "Ilmu penyusunan kamus"),
    ("PALEOGRAFI", "Kajian tulisan-tulisan kuno"),
    ("EPIGRAFI", "Kajian prasasti dan inskripsi"),
    ("NUMEROLOGI", "Kepercayaan makna mistis angka"),
    ("KOSMOLOGI", "Kajian struktur dan asal usul semesta"),
    ("TEOLOGI", "Ilmu tentang ketuhanan"),
    ("MITOLOGI", "Kajian tentang mitos dan legenda"),
    ("ANTOLOGI", "Kumpulan karya sastra pilihan"),
    ("KRONOLOGI", "Urutan waktu suatu peristiwa"),
    ("TIPOGRAFI", "Seni penataan huruf cetak"),
    ("KARTOGRAFI", "Ilmu dan seni pembuatan peta"),
    ("HIDROGRAFI", "Pemetaan perairan dan dasar laut"),
    ("TOPOGRAFI", "Pemetaan bentuk permukaan tanah"),
    ("STRATIGRAFI", "Kajian lapisan batuan bumi"),
    ("PETROGRAFI", "Deskripsi dan klasifikasi batuan"),
    ("KOREOGRAFI", "Seni menyusun rangkaian gerak tari"),
    ("BIBLIOGRAFI", "Daftar rujukan buku dan sumber"),
    ("HAGIOGRAFI", "Penulisan riwayat orang suci"),
    ("DEMONOLOGI", "Kajian tentang makhluk jahat"),
    ("ANGELOLOGI", "Kajian tentang malaikat"),
    ("ESKATOLOGI", "Ajaran tentang akhir zaman"),
]
for a, c in NIGHTMARE8:
    add("nightmare", a, c)


# ═══════════════ PERBAIKAN — re-klu kata yang tadi klu-nya bocor ═══════════════
FIX_EASY = [
    ("HOTEL", "Tempat menginap berbayar bagi pelancong"),
    ("MUSEUM", "Gedung penyimpan benda bersejarah untuk dipamerkan"),
    ("PIANO", "Alat musik bertuts hitam dan putih"),
    ("SALAD", "Hidangan sayuran segar bercampur saus"),
    ("PILOT", "Orang yang menerbangkan pesawat"),
    ("PLANET", "Benda langit besar yang mengelilingi matahari"),
    ("BUS", "Kendaraan umum besar pengangkut banyak penumpang"),
    ("OVEN", "Alat pemanggang roti dan kue"),
    ("TUNDRA", "Padang beku tanpa pohon di daerah kutub"),
    ("DRUM", "Alat musik pukul dalam sebuah band"),
    ("APRIL", "Bulan keempat dalam setahun"),
    ("SEPTEMBER", "Bulan kesembilan dalam setahun"),
    ("NOVEMBER", "Bulan kesebelas dalam setahun"),
]
for a, c in FIX_EASY:
    add("easy", a, c)

FIX_NORMAL = [
    ("SINGAPURA", "Negara-kota terkecil di Asia Tenggara"),
    ("YOGYAKARTA", "Kota pelajar berjuluk, lokasi Keraton dan Malioboro"),
    ("KUWAIT", "Negara kaya minyak kecil di tepi Teluk Persia"),
    ("BENGKULU", "Provinsi di pesisir barat daya Pulau Sumatra"),
    ("JAMBI", "Provinsi Sumatra yang dilintasi Sungai Batanghari"),
    ("GORONTALO", "Provinsi kecil di leher Pulau Sulawesi"),
]
for a, c in FIX_NORMAL:
    add("normal", a, c)


# ═══════════════ EKSPANSI 9 — buah & makanan lokal (EASY) ═══════════════
LOKAL_EASY = [
    ("MANGGIS", "Buah ungu berdaging putih, dijuluki ratu buah"),
    ("DURIAN", "Buah berduri tajam beraroma menyengat, raja buah"),
    ("RAMBUTAN", "Buah merah berambut, manis berair"),
    ("SALAK", "Buah bersisik cokelat rasanya sepat-manis"),
    ("KELENGKENG", "Buah kecil bening manis berbiji hitam"),
    ("SIRSAK", "Buah berduri lunak, daging putih asam-manis"),
    ("ALPUKAT", "Buah hijau berdaging lembut dan berlemak"),
    ("MARKISA", "Buah asam berbiji banyak, sering dibuat sirup"),
    ("KEDONDONG", "Buah hijau renyah berbiji berserat untuk rujak"),
    ("DUKU", "Buah bulat kecil kekuningan manis berkelompok"),
    ("JAMBU", "Buah berdaging renyah, ada yang merah dan putih"),
    ("PEPAYA", "Buah oranye panjang kaya vitamin A"),
    ("NANGKA", "Buah besar berduri lunak beraroma manis"),
    ("PEMPEK", "Makanan ikan khas Palembang bersaus cuko"),
    ("GUDEG", "Masakan nangka muda manis khas Yogyakarta"),
    ("RAWON", "Sup daging berkuah hitam berbumbu kluwek"),
    ("KLEPON", "Kue bola hijau berisi gula merah cair"),
    ("LONTONG", "Nasi padat yang dibungkus daun pisang"),
    ("KETUPAT", "Nasi dalam anyaman daun kelapa khas Lebaran"),
    ("GETUK", "Camilan manis dari singkong yang ditumbuk"),
    ("SERABI", "Kue bundar dari tepung beras bersantan"),
    ("MARTABAK", "Kue tebal manis atau telur gurih yang dilipat"),
    ("PECEL", "Sayuran rebus bersaus kacang khas Jawa"),
    ("KOLAK", "Hidangan manis pisang berkuah santan saat puasa"),
    ("CENDOL", "Minuman hijau kenyal bersantan dan gula merah"),
    ("BANDREK", "Minuman jahe hangat khas Sunda"),
    ("BAJIGUR", "Minuman santan-jahe hangat khas Sunda"),
    ("WEDANG", "Minuman rempah tradisional yang disajikan hangat"),
]
for a, c in LOKAL_EASY:
    add("easy", a, c)

# hewan tambahan (EASY)
HEWAN_EASY = [
    ("RUSA", "Hewan berlari cepat bertanduk bercabang"),
    ("KERBAU", "Hewan pembajak sawah bertanduk melengkung"),
    ("BADAK", "Hewan besar berkulit tebal dan bercula"),
    ("TAPIR", "Mamalia berbelalai pendek berwarna hitam-putih"),
    ("KUKANG", "Primata kecil bergerak lambat, aktif malam"),
    ("MUSANG", "Hewan malam pemakan buah, terkait kopi luwak"),
    ("LANDAK", "Hewan kecil bertubuh penuh duri tajam"),
    ("SIGUNG", "Hewan yang menyemprot bau busuk saat terancam"),
    ("WALABI", "Kerabat kanguru bertubuh lebih kecil"),
    ("MEERKAT", "Mamalia gurun yang berdiri mengawasi bahaya"),
]
for a, c in HEWAN_EASY:
    add("easy", a, c)


# ═══════════════ EKSPANSI 9 — alat musik / tari / olahraga dunia (NORMAL) ═══════════════
NORMAL9 = [
    ("HARPA", "Alat musik petik besar berbentuk segitiga"),
    ("AKORDEON", "Alat musik tekan yang dipompa dengan tangan"),
    ("SAKSOFON", "Alat musik tiup logam melengkung khas jazz"),
    ("TROMBON", "Alat musik tiup logam berpipa geser"),
    ("HARMONIKA", "Alat musik tiup kecil yang diapit bibir"),
    ("MANDOLIN", "Alat musik petik kecil berdawai ganda"),
    ("BANJO", "Alat musik petik bertubuh bundar khas country"),
    ("BALET", "Tari klasik Eropa dengan gerak jinjit anggun"),
    ("FLAMENCO", "Tari dan musik penuh hentakan khas Spanyol"),
    ("TANGO", "Tari berpasangan penuh gairah asal Argentina"),
    ("SALSA", "Tari berpasangan energik asal Amerika Latin"),
    ("SAMBA", "Tari karnaval yang riang khas Brasil"),
    ("GULAT", "Olahraga bela diri saling membanting"),
    ("ANGGAR", "Olahraga adu pedang berpelindung"),
    ("DAYUNG", "Olahraga mengayuh perahu di air"),
    ("SELANCAR", "Olahraga meluncur di atas ombak"),
    ("KRIKET", "Olahraga bola dan tongkat khas Inggris-India"),
    ("RUGBI", "Olahraga bola lonjong penuh tabrakan"),
    ("HOKI", "Olahraga bola kecil dengan tongkat bengkok"),
    ("BISBOL", "Olahraga pukul bola dan lari antar-base"),
    ("KARTINI", "Pahlawan pelopor emansipasi wanita Indonesia"),
    ("DIPONEGORO", "Pangeran pemimpin Perang Jawa melawan Belanda"),
    ("PATTIMURA", "Pahlawan dari Maluku melawan penjajah"),
    ("HAYAMWURUK", "Raja terbesar Kerajaan Majapahit"),
    ("GAJAHMADA", "Mahapatih Majapahit pengucap Sumpah Palapa"),
]
for a, c in NORMAL9:
    add("normal", a, c)


# ═══════════════ EKSPANSI 9 — cabang ilmu & fisika (HARD) ═══════════════
HARD9 = [
    ("PATOLOGI", "Ilmu tentang penyakit dan penyebabnya"),
    ("FISIOLOGI", "Ilmu tentang fungsi organ tubuh"),
    ("SITOLOGI", "Ilmu yang mempelajari sel"),
    ("OPTIKA", "Cabang fisika tentang cahaya"),
    ("AKUSTIKA", "Cabang fisika tentang bunyi"),
    ("MEKANIKA", "Cabang fisika tentang gerak dan gaya"),
    ("KINEMATIKA", "Ilmu gerak tanpa memperhatikan penyebabnya"),
    ("DINAMIKA", "Ilmu gerak dengan memperhatikan gaya"),
    ("ELEKTRONIKA", "Ilmu tentang aliran elektron dalam rangkaian"),
    ("MAGNETISME", "Gejala tarik-menarik akibat medan magnet"),
    ("GRAVIMETRI", "Pengukuran berdasarkan gaya gravitasi"),
    ("KALORIMETRI", "Pengukuran jumlah kalor"),
    ("BIOKIMIA", "Ilmu tentang reaksi kimia makhluk hidup"),
    ("GEOKIMIA", "Ilmu kimia unsur-unsur di bumi"),
    ("ASTROKIMIA", "Ilmu kimia benda-benda antariksa"),
    ("PALEOBOTANI", "Ilmu tentang tumbuhan purba"),
    ("DENDROLOGI", "Ilmu yang mempelajari pohon"),
    ("KARDIOLOGI", "Ilmu tentang jantung dan pembuluhnya"),
    ("NEFROLOGI", "Ilmu tentang ginjal"),
    ("DERMATOLOGI", "Ilmu tentang kulit"),
    ("OFTALMOLOGI", "Ilmu tentang mata"),
    ("PSIKIATRI", "Ilmu kedokteran tentang gangguan jiwa"),
    ("ORTOPEDI", "Ilmu kedokteran tentang tulang"),
    ("GERIATRI", "Ilmu kedokteran tentang lanjut usia"),
    ("PEDIATRI", "Ilmu kedokteran tentang anak"),
]
for a, c in HARD9:
    add("hard", a, c)


# ═══════════════ EKSPANSI 9 — ilmu langka (NIGHTMARE) ═══════════════
NIGHTMARE9 = [
    ("TAKSONOMI", "Ilmu penggolongan dan penamaan makhluk hidup"),
    ("BIOGEOGRAFI", "Kajian penyebaran makhluk hidup di bumi"),
    ("ETNOBOTANI", "Kajian pemanfaatan tumbuhan oleh masyarakat"),
    ("PALINOLOGI", "Ilmu tentang serbuk sari dan spora"),
    ("MALAKOLOGI", "Ilmu yang mempelajari moluska"),
    ("ARAKNOLOGI", "Ilmu yang mempelajari laba-laba"),
    ("MIRMEKOLOGI", "Ilmu yang mempelajari semut"),
    ("KARSINOLOGI", "Ilmu yang mempelajari udang dan kepiting"),
    ("PRIMATOLOGI", "Ilmu yang mempelajari primata"),
    ("SPELUNKING", "Kegiatan menjelajah gua sebagai olahraga"),
    ("GLASIOLOGI", "Ilmu yang mempelajari gletser dan es"),
    ("LIMNOLOGI", "Ilmu yang mempelajari danau dan air tawar"),
    ("SPELEOTEM", "Endapan mineral khas dalam gua"),
    ("VEXILOLOGI", "Kajian tentang bendera"),
    ("HOROLOGI", "Ilmu tentang pengukuran waktu dan jam"),
    ("KAMPANOLOGI", "Ilmu tentang lonceng dan cara membunyikannya"),
    ("ENOLOGI", "Ilmu tentang pembuatan anggur minuman"),
    ("SOMMELIER", "Ahli penyaji dan pemadu minuman anggur"),
    ("TIPOLOGI", "Kajian penggolongan berdasarkan tipe"),
    ("SEMIOTIKA", "Ilmu tentang tanda dan makna"),
    ("FONETIK", "Kajian bunyi ujaran secara fisik"),
    ("DIALEKTOLOGI", "Kajian tentang dialek bahasa"),
    ("LEKSIKOLOGI", "Kajian tentang kosakata dan maknanya"),
    ("ORTOGRAFI", "Sistem ejaan suatu bahasa"),
    ("KODIKOLOGI", "Kajian naskah kuno sebagai benda fisik"),
]
for a, c in NIGHTMARE9:
    add("nightmare", a, c)


# ═══════════════ TULIS FILE ═══════════════
def write_all():
    for tier, rows in BANK.items():
        path = os.path.join(DATA, f"{tier}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# Bank soal TTS — tier {tier} ({len(rows)} soal)\n")
            f.write("# Format: JAWABAN|petunjuk\n")
            for a, c in rows:
                f.write(f"{a}|{c}\n")
    return {t: len(BANK[t]) for t in BANK}


if __name__ == "__main__":
    counts = write_all()
    total = sum(counts.values())
    print("Bank soal ditulis ke", DATA)
    for t in ("easy", "normal", "hard", "nightmare"):
        print(f"  {t:10s}: {counts[t]}")
    print(f"  {'TOTAL':10s}: {total}")
