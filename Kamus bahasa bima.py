
import random
import string

random.seed(42) 
ALPHABET = string.ascii_uppercase  #
 
 
# ---------------------------------------------------------------------------
# 1. DATASET KAMUS BAHASA BIMA 
# ---------------------------------------------------------------------------
KAMUS = [
    {"bima": "AU",   "arti": "apa"},
    {"bima": "ANA",  "arti": "anak"},
    {"bima": "AMA",  "arti": "bapak"},
    {"bima": "ARI",  "arti": "adik"},
    {"bima": "ASA",  "arti": "mulut"},
    {"bima": "ADE",  "arti": "hati"},
    {"bima": "CAPI", "arti": "sapi"},
    {"bima": "CARU", "arti": "enak"},
    {"bima": "BURA", "arti": "putih"},
    {"bima": "AMBA", "arti": "pasar"},
    {"bima": "NAHU", "arti": "saya"},
    {"bima": "NDAI", "arti": "kami"},
    {"bima": "ITA",  "arti": "kamu"},
    {"bima": "DOU",  "arti": "orang"},
    {"bima": "UMA",  "arti": "rumah"},
    {"bima": "OI",   "arti": "air"},
    {"bima": "LOA",  "arti": "bisa"},
    {"bima": "MAI",  "arti": "datang"},
    {"bima": "LAO",  "arti": "pergi"},
    {"bima": "NGUPA", "arti": "mencari"},
]
 
KATA_TARGET_KANDIDAT = [k for k in KAMUS if len(k["bima"]) == 4]
 
 
# ---------------------------------------------------------------------------
# 2. STATE / MEMORI ALGORITMA GENETIKA 
# ---------------------------------------------------------------------------
class GAState:
    def __init__(self):
        self.target = None          
        self.pop_size = 6           
        self.generation = 0         
        self.population = []        
        self.fitness = []          
        self.probabilitas = []      
        self.interval = []          
        self.mating_pool = []       
        self.crossover_children = []
        self.crossover_log = []     
        self.mutated_population = []
        self.mutation_log = []      
 
    def is_ready(self):
        return self.target is not None
 
 
STATE = GAState()
 
 
# ---------------------------------------------------------------------------
# 3. FUNGSI-FUNGSI ALGORITMA GENETIKA
# ---------------------------------------------------------------------------
def buat_individu_acak(panjang):
    return "".join(random.choice(ALPHABET) for _ in range(panjang))
 
 
def buat_individu_dekat_target(target, jumlah_huruf_beda=1):
    individu = list(target)
    posisi_diubah = random.sample(range(len(target)), min(jumlah_huruf_beda, len(target)))
    for pos in posisi_diubah:
        huruf_baru = random.choice([c for c in ALPHABET if c != individu[pos]])
        individu[pos] = huruf_baru
    return "".join(individu)
 
 
def buat_populasi_awal(target, pop_size):
    populasi = [buat_individu_dekat_target(target, jumlah_huruf_beda=1) for _ in range(pop_size - 1)]
    populasi.append(buat_individu_acak(len(target)))  # pembanding, biasanya fitness rendah/0
    random.shuffle(populasi)
    return populasi
 
 
def hitung_fitness(individu, target):
    """Fitness = jumlah huruf yang cocok pada posisi yang sama / panjang kata."""
    cocok = sum(1 for a, b in zip(individu, target) if a == b)
    return cocok / len(target)
 
 
def hitung_semua_fitness(population, target):
    return [hitung_fitness(ind, target) for ind in population]
 
 
def hitung_probabilitas_dan_interval(fitness_list):
    total = sum(fitness_list)
    probabilitas = []
    for f in fitness_list:
        if total == 0:
            probabilitas.append(1 / len(fitness_list))  # semua sama rata jika total 0
        else:
            probabilitas.append(f / total)
 
    interval = []
    batas_bawah = 0.0
    for p in probabilitas:
        batas_atas = batas_bawah + p
        interval.append((batas_bawah, batas_atas))
        batas_bawah = batas_atas
    return probabilitas, interval
 
 
def seleksi_roulette_wheel(population, interval, jumlah_seleksi):
    """Memutar roda roulette sebanyak jumlah_seleksi kali."""
    terpilih = []
    detail_putaran = []
    for _ in range(jumlah_seleksi):
        r = random.random()  # angka acak [0,1)
        for idx, (bawah, atas) in enumerate(interval):
            if bawah <= r < atas or (idx == len(interval) - 1 and r >= bawah):
                terpilih.append(population[idx])
                detail_putaran.append((r, idx + 1, population[idx]))
                break
    return terpilih, detail_putaran
 
 
def crossover_satu_titik(parent1, parent2, titik=None):
    panjang = len(parent1)
    if titik is None:
        titik = random.randint(1, panjang - 1)  # titik potong, hindari 0 & panjang
    anak1 = parent1[:titik] + parent2[titik:]
    anak2 = parent2[:titik] + parent1[titik:]
    return anak1, anak2, titik
 
 
def jalankan_crossover(mating_pool, prob_crossover=0.8):
    anak_semua = []
    log = []
    for i in range(0, len(mating_pool) - 1, 2):
        p1, p2 = mating_pool[i], mating_pool[i + 1]
        if random.random() <= prob_crossover:
            a1, a2, titik = crossover_satu_titik(p1, p2)
            log.append({"p1": p1, "p2": p2, "titik": titik, "anak1": a1, "anak2": a2, "crossover": True})
        else:
            a1, a2 = p1, p2
            log.append({"p1": p1, "p2": p2, "titik": None, "anak1": a1, "anak2": a2, "crossover": False})
        anak_semua.extend([a1, a2])
    # Jika jumlah ganjil, individu terakhir dibawa langsung tanpa pasangan
    if len(mating_pool) % 2 == 1:
        anak_semua.append(mating_pool[-1])
    return anak_semua, log
 
 
def jalankan_mutasi(individu_list, prob_mutasi=0.1):
    hasil = []
    log = []
    for individu in individu_list:
        individu_baru = list(individu)
        posisi_mutasi = []
        for posisi in range(len(individu_baru)):
            if random.random() <= prob_mutasi:
                gen_lama = individu_baru[posisi]
                gen_baru = random.choice(ALPHABET)
                individu_baru[posisi] = gen_baru
                posisi_mutasi.append((posisi + 1, gen_lama, gen_baru))
        hasil.append("".join(individu_baru))
        log.append({"asal": individu, "hasil": "".join(individu_baru), "mutasi": posisi_mutasi})
    return hasil, log
 
 
# ---------------------------------------------------------------------------
# 4. FUNGSI-FUNGSI TAMPILAN (MENU)
# ---------------------------------------------------------------------------
def tampilkan_kamus():
    print("\n=== DATASET KAMUS BAHASA BIMA (Nggahi Mbojo) ===")
    print(f"{'No':<4}{'Kata Bima':<12}{'Arti (Indonesia)':<20}")
    print("-" * 36)
    for i, k in enumerate(KAMUS, start=1):
        print(f"{i:<4}{k['bima']:<12}{k['arti']:<20}")
    print(f"\nTotal kata dalam kamus : {len(KAMUS)}")
 
 
def cari_kata():
    kw = input("Masukkan kata Bima ATAU arti Indonesia yang dicari: ").strip().lower()
    hasil = [k for k in KAMUS if kw in k["bima"].lower() or kw in k["arti"].lower()]
    print("\n=== HASIL PENCARIAN KATA ===")
    if hasil:
        for k in hasil:
            print(f"  {k['bima']}  =  {k['arti']}")
    else:
        print("  Kata tidak ditemukan dalam kamus.")
 
 
def pilih_target():
    print("\nPilih salah satu kata (4 huruf) sebagai TARGET pencarian Algoritma Genetika:")
    for i, k in enumerate(KATA_TARGET_KANDIDAT, start=1):
        print(f"  {i}. {k['bima']}  ({k['arti']})")
    while True:
        pilihan = input(f"Pilih nomor [1-{len(KATA_TARGET_KANDIDAT)}] (Enter = acak): ").strip()
        if pilihan == "":
            return random.choice(KATA_TARGET_KANDIDAT)["bima"]
        if pilihan.isdigit() and 1 <= int(pilihan) <= len(KATA_TARGET_KANDIDAT):
            return KATA_TARGET_KANDIDAT[int(pilihan) - 1]["bima"]
        print("Pilihan tidak valid, coba lagi.")
 
 
def jalankan_algoritma_genetika():
    """Menu 3: menjalankan seluruh siklus GA (1 generasi penuh) sekaligus,
    lalu menyimpan setiap tahap ke STATE supaya bisa dilihat lagi lewat
    menu 4-9."""
    target = pilih_target()
    STATE.target = target
    STATE.generation = 0
 
    print(f"\nKata TARGET yang dicari GA: '{target}'")
    STATE.population = buat_populasi_awal(target, STATE.pop_size)
 
    print("\n>>> TAHAP 1: POPULASI AWAL (Generasi ke-0)")
    for i, ind in enumerate(STATE.population, start=1):
        print(f"  Individu {i}: {ind}")
 
    _hasil_fitness(tampilkan=True)
    _hasil_roulette(tampilkan=True)
    _hasil_crossover(tampilkan=True)
    _hasil_mutasi(tampilkan=True)
    _hasil_generasi_baru(tampilkan=True)
 
    print("\n>>> Proses Algoritma Genetika untuk 1 generasi SELESAI.")
    print("Gunakan menu 4-9 untuk melihat kembali detail tiap tahap.")
 
 
def _hasil_fitness(tampilkan=False):
    STATE.fitness = hitung_semua_fitness(STATE.population, STATE.target)
    if tampilkan:
        print(f"\n>>> TAHAP 2: PERHITUNGAN FITNESS (target = '{STATE.target}')")
        print(f"{'Individu':<12}{'Kromosom':<12}{'Cocok':<8}{'Fitness':<10}")
        print("-" * 42)
        for i, (ind, fit) in enumerate(zip(STATE.population, STATE.fitness), start=1):
            cocok = sum(1 for a, b in zip(ind, STATE.target) if a == b)
            print(f"I{i:<11}{ind:<12}{cocok:<8}{fit:<10.3f}")
        print(f"Total Fitness Populasi : {sum(STATE.fitness):.3f}")
 
 
def _hasil_roulette(tampilkan=False):
    STATE.probabilitas, STATE.interval = hitung_probabilitas_dan_interval(STATE.fitness)
    STATE.mating_pool, detail_putaran = seleksi_roulette_wheel(
        STATE.population, STATE.interval, STATE.pop_size
    )
    STATE._detail_putaran = detail_putaran  # simpan sementara untuk ditampilkan
    if tampilkan:
        print("\n>>> TAHAP 3: SELEKSI ROULETTE WHEEL")
        print(f"{'Individu':<10}{'Fitness':<10}{'Probabilitas':<14}{'Interval':<20}")
        print("-" * 54)
        for i, (ind, fit, prob, (lo, hi)) in enumerate(
            zip(STATE.population, STATE.fitness, STATE.probabilitas, STATE.interval), start=1
        ):
            print(f"I{i:<9}{fit:<10.3f}{prob:<14.3f}{lo:.3f} - {hi:.3f}")
 
        print("\nPutaran roda roulette (angka acak r dibandingkan dengan interval):")
        for putaran, (r, idx, ind) in enumerate(detail_putaran, start=1):
            print(f"  Putaran {putaran}: r = {r:.3f}  -> terpilih I{idx} ({ind})")
 
        print("\nMating pool (individu hasil seleksi) :")
        print("  " + ", ".join(STATE.mating_pool))
 
 
def _hasil_crossover(tampilkan=False):
    STATE.crossover_children, STATE.crossover_log = jalankan_crossover(STATE.mating_pool)
    if tampilkan:
        print("\n>>> TAHAP 4: CROSS OVER (Single-Point Crossover)")
        for i, log in enumerate(STATE.crossover_log, start=1):
            print(f"\n  Pasangan {i}:")
            print(f"    Parent 1 : {log['p1']}")
            print(f"    Parent 2 : {log['p2']}")
            if log["crossover"]:
                print(f"    Titik potong: setelah posisi ke-{log['titik']}")
                p1_kiri, p1_kanan = log['p1'][:log['titik']], log['p1'][log['titik']:]
                p2_kiri, p2_kanan = log['p2'][:log['titik']], log['p2'][log['titik']:]
                print(f"      {p1_kiri}|{p1_kanan}  +  {p2_kiri}|{p2_kanan}")
                print(f"    Anak 1   : {log['anak1']}  (dari {p1_kiri} + {p2_kanan})")
                print(f"    Anak 2   : {log['anak2']}  (dari {p2_kiri} + {p1_kanan})")
            else:
                print("    (Tidak terjadi crossover, anak = salinan parent)")
                print(f"    Anak 1   : {log['anak1']}")
                print(f"    Anak 2   : {log['anak2']}")
 
 
def _hasil_mutasi(tampilkan=False):
    STATE.mutated_population, STATE.mutation_log = jalankan_mutasi(STATE.crossover_children)
    if tampilkan:
        print("\n>>> TAHAP 5: MUTASI GEN")
        for i, log in enumerate(STATE.mutation_log, start=1):
            print(f"\n  Individu {i}: {log['asal']} -> {log['hasil']}")
            if log["mutasi"]:
                for posisi, lama, baru in log["mutasi"]:
                    print(f"    Mutasi pada posisi {posisi}: '{lama}' -> '{baru}'")
            else:
                print("    (Tidak ada gen yang bermutasi)")
 
 
def _hasil_generasi_baru(tampilkan=False):
    fitness_baru = hitung_semua_fitness(STATE.mutated_population, STATE.target)
    if tampilkan:
        print(f"\n>>> TAHAP 6: POPULASI / GENERASI BARU (Generasi ke-{STATE.generation + 1})")
        print(f"{'Individu':<10}{'Kromosom':<12}{'Fitness':<10}")
        print("-" * 32)
        for i, (ind, fit) in enumerate(zip(STATE.mutated_population, fitness_baru), start=1):
            tanda = "  <-- TARGET DITEMUKAN!" if ind == STATE.target else ""
            print(f"I{i:<9}{ind:<12}{fit:<10.3f}{tanda}")
        print(f"\nRata-rata Fitness Generasi ke-{STATE.generation} : {sum(STATE.fitness)/len(STATE.fitness):.3f}")
        print(f"Rata-rata Fitness Generasi ke-{STATE.generation + 1} : {sum(fitness_baru)/len(fitness_baru):.3f}")
 
    # Populasi baru menjadi populasi aktif -> generasi bertambah
    STATE.population = STATE.mutated_population
    STATE.fitness = fitness_baru
    STATE.generation += 1
 
 
def menu_tampilkan_populasi():
    if not STATE.is_ready():
        print("\nJalankan menu 3 (Jalankan Algoritma Genetika) terlebih dahulu.")
        return
    print(f"\n=== POPULASI AKTIF (Generasi ke-{STATE.generation}) ===")
    for i, ind in enumerate(STATE.population, start=1):
        print(f"  Individu {i}: {ind}")
 
 
def menu_hasil_fitness():
    if not STATE.is_ready():
        print("\nJalankan menu 3 (Jalankan Algoritma Genetika) terlebih dahulu.")
        return
    _hasil_fitness(tampilkan=True)
 
 
def menu_seleksi_roulette():
    if not STATE.mating_pool:
        print("\nBelum ada data seleksi roulette. Jalankan menu 3 terlebih dahulu.")
        return
    print("\n=== DATA SELEKSI ROULETTE (dari perhitungan terakhir) ===")
    print(f"{'Individu':<10}{'Fitness':<10}{'Probabilitas':<14}{'Interval':<20}")
    for i, (fit, prob, (lo, hi)) in enumerate(
        zip(STATE.fitness, STATE.probabilitas, STATE.interval), start=1
    ):
        print(f"I{i:<9}{fit:<10.3f}{prob:<14.3f}{lo:.3f} - {hi:.3f}")
    print("\nMating pool:", ", ".join(STATE.mating_pool))
 
 
def menu_crossover():
    if not STATE.crossover_log:
        print("\nBelum ada data crossover. Jalankan menu 3 terlebih dahulu.")
        return
    _hasil_crossover_tampil_ulang()
 
 
def _hasil_crossover_tampil_ulang():
    print("\n=== DATA CROSS OVER (dari perhitungan terakhir) ===")
    for i, log in enumerate(STATE.crossover_log, start=1):
        print(f"\n  Pasangan {i}: {log['p1']} x {log['p2']}")
        if log["crossover"]:
            print(f"    Titik potong ke-{log['titik']} -> Anak: {log['anak1']}, {log['anak2']}")
        else:
            print(f"    Tidak crossover -> Anak: {log['anak1']}, {log['anak2']}")
 
 
def menu_mutasi():
    if not STATE.mutation_log:
        print("\nBelum ada data mutasi. Jalankan menu 3 terlebih dahulu.")
        return
    print("\n=== DATA MUTASI (dari perhitungan terakhir) ===")
    for i, log in enumerate(STATE.mutation_log, start=1):
        info = ", ".join(f"posisi {p}: {l}->{b}" for p, l, b in log["mutasi"]) or "tidak ada mutasi"
        print(f"  Individu {i}: {log['asal']} -> {log['hasil']}  ({info})")
 
 
def menu_generasi_baru():
    """Menjalankan satu siklus GA tambahan dari populasi yang sekarang aktif
    (berguna jika ingin melanjutkan ke generasi ke-2, ke-3, dst)."""
    if not STATE.is_ready():
        print("\nJalankan menu 3 (Jalankan Algoritma Genetika) terlebih dahulu.")
        return
    _hasil_fitness(tampilkan=True)
    _hasil_roulette(tampilkan=True)
    _hasil_crossover(tampilkan=True)
    _hasil_mutasi(tampilkan=True)
    _hasil_generasi_baru(tampilkan=True)
 
 
# ---------------------------------------------------------------------------
# 5. PROGRAM UTAMA (MENU)
# ---------------------------------------------------------------------------
def tampilkan_menu():
    print("\n" + "=" * 50)
    print("     === Kamus Bahasa Daerah (Bahasa Bima) ===")
    print("=" * 50)
    print(" 1. Tampilkan Kamus")
    print(" 2. Cari Kata")
    print(" 3. Jalankan Algoritma Genetika")
    print(" 4. Tampilkan Populasi")
    print(" 5. Hasil Fitness")
    print(" 6. Seleksi Roulette")
    print(" 7. Cross Over")
    print(" 8. Mutasi")
    print(" 9. Generasi Baru")
    print("10. Keluar")
 
 
def main():
    while True:
        tampilkan_menu()
        pilihan = input("Pilih menu (1-10): ").strip()
 
        if pilihan == "1":
            tampilkan_kamus()
        elif pilihan == "2":
            cari_kata()
        elif pilihan == "3":
            jalankan_algoritma_genetika()
        elif pilihan == "4":
            menu_tampilkan_populasi()
        elif pilihan == "5":
            menu_hasil_fitness()
        elif pilihan == "6":
            menu_seleksi_roulette()
        elif pilihan == "7":
            menu_crossover()
        elif pilihan == "8":
            menu_mutasi()
        elif pilihan == "9":
            menu_generasi_baru()
        elif pilihan == "10":
            print("\nTerima kasih. Program selesai. (Nahu wa'a - Saya pergi)")
            break
        else:
            print("\nPilihan tidak valid, silakan pilih 1-10.")
 
 
if __name__ == "__main__":
    main()