import os
import sys
import json
import time
import heapq
import re
from datetime import datetime
from collections import deque

# KONFIGURASI FILE DATA
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_FILE = os.path.join(DATA_DIR, "data_klinik.json")


# WARNA TERMINAL
os.system("")

class Warna:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    MERAH = "\033[91m"
    HIJAU = "\033[92m"
    KUNING = "\033[93m"
    BIRU = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    PUTIH = "\033[97m"
    ABU = "\033[90m"


# DATA UTAMA PROGRAM
pasien_db = {}
antrian_prioritas = []
antrian_reguler = deque()
id_dalam_antrian = set()
riwayat_undo = []
pasien_dilayani_hari_ini = []
log_transaksi = []
nomor_kedatangan = 0


# UTILITAS TAMPILAN
def garis(panjang=72):
    return "_" * panjang


def bersihkan_layar():
    os.system("cls" if os.name == "nt" else "clear")


def jeda():
    input(f"\n{Warna.ABU}Tekan Enter untuk kembali ke menu...{Warna.RESET}")


def waktu_sekarang():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def loading(teks="Memproses", durasi=0.8):
    frame = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    jumlah_putaran = max(8, int(durasi / 0.08))

    for i in range(jumlah_putaran):
        simbol = frame[i % len(frame)]
        sys.stdout.write(f"\r{Warna.CYAN}{simbol} {teks}...{Warna.RESET}")
        sys.stdout.flush()
        time.sleep(0.08)

    sys.stdout.write("\r" + " " * (len(teks) + 20) + "\r")
    sys.stdout.flush()


def pesan_sukses(teks):
    print(f"{Warna.HIJAU}✅ {teks}{Warna.RESET}")


def pesan_error(teks):
    print(f"{Warna.MERAH}❌ {teks}{Warna.RESET}")


def pesan_peringatan(teks):
    print(f"{Warna.KUNING}⚠️  {teks}{Warna.RESET}")


def pesan_info(teks):
    print(f"{Warna.CYAN}ℹ️  {teks}{Warna.RESET}")


def judul_halaman(teks):
    print(f"{Warna.CYAN}{garis()}{Warna.RESET}")
    print(f"{Warna.BOLD}{teks.center(72)}{Warna.RESET}")
    print(f"{Warna.CYAN}{garis()}{Warna.RESET}\n")


def format_rupiah(nilai):
    return "Rp" + f"{nilai:,}".replace(",", ".")


# UTILITAS INPUT
def input_tidak_kosong(label):
    while True:
        nilai = input(label).strip()
        if nilai:
            return nilai
        pesan_error("Input tidak boleh kosong.")


def input_angka(label, minimal=None, maksimal=None):
    while True:
        nilai = input(label).strip()
        try:
            angka = int(nilai)
        except ValueError:
            pesan_error("Input harus berupa angka.")
            continue

        if minimal is not None and angka < minimal:
            pesan_error(f"Angka tidak boleh kurang dari {minimal}.")
            continue

        if maksimal is not None and angka > maksimal:
            pesan_error(f"Angka tidak boleh lebih dari {maksimal}.")
            continue

        return angka


def input_ya_tidak(label):
    while True:
        nilai = input(label).strip().lower()
        if nilai in ("y", "ya"):
            return True
        if nilai in ("n", "no", "tidak"):
            return False
        pesan_error("Masukkan y/ya atau n/tidak.")


# SIMPAN DAN MUAT DATA
def pastikan_folder_data():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def data_untuk_disimpan():
    return {
        "metadata": {
            "nama_program": "Sistem Manajemen Klinik Sehat Bersama",
            "pembuat": "By Kelompok 1",
            "terakhir_disimpan": waktu_sekarang()
        },
        "pasien_db": pasien_db,
        "antrian_prioritas": antrian_prioritas,
        "antrian_reguler": list(antrian_reguler),
        "id_dalam_antrian": list(id_dalam_antrian),
        "riwayat_undo": riwayat_undo,
        "pasien_dilayani_hari_ini": pasien_dilayani_hari_ini,
        "log_transaksi": log_transaksi,
        "nomor_kedatangan": nomor_kedatangan
    }


def simpan_data(tampilkan_loading=True):
    pastikan_folder_data()

    if tampilkan_loading:
        loading("Menyimpan data", 0.7)

    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data_untuk_disimpan(), file, indent=4, ensure_ascii=False)
        if tampilkan_loading:
            pesan_sukses(f"Data berhasil disimpan ke: {DATA_FILE}")
        return True
    except OSError as error:
        pesan_error(f"Gagal menyimpan data. Detail: {error}")
        return False


def muat_data(tampilkan_loading=True):
    global pasien_db
    global antrian_prioritas
    global antrian_reguler
    global id_dalam_antrian
    global riwayat_undo
    global pasien_dilayani_hari_ini
    global log_transaksi
    global nomor_kedatangan

    pastikan_folder_data()

    if tampilkan_loading:
        loading("Memuat data", 0.9)

    if not os.path.exists(DATA_FILE):
        if tampilkan_loading:
            pesan_info("File data belum ada. Program memulai dengan data kosong.")
        return False

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        pasien_db = data.get("pasien_db", {})
        antrian_prioritas = data.get("antrian_prioritas", [])
        heapq.heapify(antrian_prioritas)
        antrian_reguler = deque(data.get("antrian_reguler", []))
        id_dalam_antrian = set(data.get("id_dalam_antrian", []))
        riwayat_undo = data.get("riwayat_undo", [])
        pasien_dilayani_hari_ini = data.get("pasien_dilayani_hari_ini", [])
        log_transaksi = data.get("log_transaksi", [])
        nomor_kedatangan = data.get("nomor_kedatangan", 0)

        if tampilkan_loading:
            pesan_sukses("Data berhasil dimuat.")
        return True
    except (OSError, json.JSONDecodeError) as error:
        pesan_error(f"Gagal memuat data. Detail: {error}")
        return False


def simpan_otomatis():
    simpan_data(tampilkan_loading=False)


# FITUR PASIEN
def tentukan_kategori_pasien(usia, kondisi_darurat):
    if kondisi_darurat:
        return "Darurat"
    if usia > 60:
        return "Lansia"
    return "Reguler"


def cari_pasien(id_pasien):
    return pasien_db.get(id_pasien)


def tampilkan_detail_pasien(pasien):
    print(f"{Warna.CYAN}{garis(55)}{Warna.RESET}")
    print(f"ID Pasien      : {pasien['id']}")
    print(f"Nama           : {pasien['nama']}")
    print(f"Usia           : {pasien['usia']} tahun")
    print(f"Keluhan        : {pasien['keluhan']}")
    print(f"Kategori       : {pasien.get('kategori_terakhir', '-')}")
    print(f"Total Riwayat  : {len(pasien.get('riwayat_medis', []))} catatan")
    print(f"{Warna.CYAN}{garis(55)}{Warna.RESET}")


def tambah_ke_antrian(id_pasien, kategori):
    global nomor_kedatangan

    if id_pasien in id_dalam_antrian:
        pesan_peringatan("Pasien ini sudah berada di dalam antrian.")
        return False

    nomor_kedatangan += 1

    if kategori == "Darurat":
        heapq.heappush(antrian_prioritas, [1, nomor_kedatangan, id_pasien])
    elif kategori == "Lansia":
        heapq.heappush(antrian_prioritas, [2, nomor_kedatangan, id_pasien])
    else:
        antrian_reguler.append([nomor_kedatangan, id_pasien])

    id_dalam_antrian.add(id_pasien)
    return True



def buat_id_pasien_otomatis():
    nomor_terbesar = 0

    for id_pasien in pasien_db.keys():
        cocok = re.search(r"ID-(\d+)$", str(id_pasien))
        if cocok:
            nomor = int(cocok.group(1))
            if nomor > nomor_terbesar:
                nomor_terbesar = nomor

    nomor_baru = nomor_terbesar + 1

    while True:
        id_baru = f"ID-{nomor_baru:02d}"
        if id_baru not in pasien_db:
            return id_baru
        nomor_baru += 1


def daftarkan_pasien():
    bersihkan_layar()
    judul_halaman("DAFTARKAN PASIEN")

    # ID pasien dibuat otomatis tanpa perlu input manual.
    id_pasien = buat_id_pasien_otomatis()

    print(f"ID Pasien        : {Warna.BOLD}{id_pasien}{Warna.RESET}")

    nama = input_tidak_kosong("Nama Pasien      : ").title()
    usia = input_angka("Usia Pasien      : ", minimal=0, maksimal=80)
    keluhan = input_tidak_kosong("Keluhan          : ")
    kondisi_darurat = input_ya_tidak("Apakah kondisi pasien darurat? (y/n): ")
    kategori = tentukan_kategori_pasien(usia, kondisi_darurat)

    pasien_db[id_pasien] = {
        "id": id_pasien,
        "nama": nama,
        "usia": usia,
        "keluhan": keluhan,
        "kategori_terakhir": kategori,
        "riwayat_medis": []
    }

    loading("Memproses pendaftaran", 0.7)

    if tambah_ke_antrian(id_pasien, kategori):
        simpan_otomatis()
        pesan_sukses(f"Pasien berhasil didaftarkan ke antrian {kategori}.")
        pesan_info(f"ID pasien: {id_pasien}")
    else:
        simpan_otomatis()

    jeda()


def cari_data_pasien():
    bersihkan_layar()
    judul_halaman("CARI DATA PASIEN")

    id_pasien = input_tidak_kosong("Masukkan ID pasien: ").upper()
    loading("Mencari data pasien", 0.6)

    pasien = cari_pasien(id_pasien)
    if pasien:
        pesan_sukses("Data pasien ditemukan.")
        tampilkan_detail_pasien(pasien)
    else:
        pesan_error("Data pasien tidak ditemukan.")

    jeda()


def perbarui_data_pasien():
    bersihkan_layar()
    judul_halaman("PERBARUI DATA PASIEN")

    id_pasien = input_tidak_kosong("Masukkan ID pasien: ").upper()
    pasien = cari_pasien(id_pasien)

    if not pasien:
        pesan_error("Data pasien tidak ditemukan.")
        jeda()
        return

    tampilkan_detail_pasien(pasien)
    print(f"{Warna.ABU}Kosongkan input jika data tidak ingin diubah.{Warna.RESET}\n")

    nama_baru = input("Nama baru       : ").strip().title()
    usia_baru = input("Usia baru       : ").strip()
    keluhan_baru = input("Keluhan baru    : ").strip()

    if nama_baru:
        pasien["nama"] = nama_baru

    if usia_baru:
        try:
            usia = int(usia_baru)
            if 0 <= usia <= 80:
                pasien["usia"] = usia
            else:
                pesan_peringatan("Usia tidak valid. Batas maksimal usia pasien adalah 80 tahun, data usia tidak diubah.")
        except ValueError:
            pesan_peringatan("Usia harus angka, data usia tidak diubah.")

    if keluhan_baru:
        pasien["keluhan"] = keluhan_baru

    loading("Memperbarui data", 0.6)
    simpan_otomatis()
    pesan_sukses("Data pasien berhasil diperbarui.")
    jeda()


def tampilkan_semua_pasien():
    bersihkan_layar()
    judul_halaman("DAFTAR SELURUH PASIEN")

    if not pasien_db:
        pesan_peringatan("Belum ada data pasien yang terdaftar.")
        jeda()
        return

    print(f"{Warna.BOLD}{'No':<4}{'ID':<12}{'Nama':<25}{'Usia':<8}{'Kategori':<12}{Warna.RESET}")
    print(garis(65))

    daftar_pasien = list(pasien_db.values())
    daftar_pasien.sort(key=lambda data: data["id"])

    for nomor, pasien in enumerate(daftar_pasien, start=1):
        print(
            f"{nomor:<4}"
            f"{pasien['id']:<12}"
            f"{pasien['nama']:<25}"
            f"{str(pasien['usia']):<8}"
            f"{pasien.get('kategori_terakhir', '-'):<12}"
        )

    jeda()


# FITUR ANTRIAN
def nama_prioritas(angka_prioritas):
    if angka_prioritas == 1:
        return "Darurat"
    if angka_prioritas == 2:
        return "Lansia"
    return "Reguler"


def panggil_pasien_berikutnya():
    bersihkan_layar()
    judul_halaman("PANGGIL PASIEN BERIKUTNYA")

    if not antrian_prioritas and not antrian_reguler:
        pesan_peringatan("Antrian masih kosong.")
        jeda()
        return

    loading("Mengambil pasien berikutnya", 0.8)

    if antrian_prioritas:
        prioritas, urutan, id_pasien = heapq.heappop(antrian_prioritas)
        kategori = nama_prioritas(prioritas)
    else:
        urutan, id_pasien = antrian_reguler.popleft()
        kategori = "Reguler"

    id_dalam_antrian.discard(id_pasien)
    pasien = cari_pasien(id_pasien)

    if not pasien:
        pesan_error("Data pasien tidak ditemukan di database.")
        simpan_otomatis()
        jeda()
        return

    pasien_dilayani_hari_ini.append({
        "id_pasien": id_pasien,
        "nama": pasien["nama"],
        "kategori": kategori,
        "waktu_dipanggil": waktu_sekarang()
    })

    simpan_otomatis()

    pesan_sukses("Pasien berikutnya berhasil dipanggil.")
    print()
    print(f"{Warna.BOLD}Nomor Urut  :{Warna.RESET} {urutan}")
    print(f"{Warna.BOLD}ID Pasien   :{Warna.RESET} {id_pasien}")
    print(f"{Warna.BOLD}Nama        :{Warna.RESET} {pasien['nama']}")
    print(f"{Warna.BOLD}Kategori    :{Warna.RESET} {kategori}")
    print(f"{Warna.BOLD}Keluhan     :{Warna.RESET} {pasien['keluhan']}")

    jeda()


def tampilkan_antrian():
    bersihkan_layar()
    judul_halaman("KONDISI ANTRIAN SAAT INI")

    print(f"{Warna.BOLD}Antrian Prioritas{Warna.RESET}")
    print(garis(55))

    if not antrian_prioritas:
        print(f"{Warna.ABU}Belum ada pasien di antrian prioritas.{Warna.RESET}")
    else:
        print(f"{'No':<4}{'ID':<12}{'Nama':<25}{'Kategori':<12}")
        print(garis(55))
        for nomor, item in enumerate(sorted(antrian_prioritas), start=1):
            prioritas, urutan, id_pasien = item
            pasien = cari_pasien(id_pasien)
            nama = pasien["nama"] if pasien else "Data tidak ditemukan"
            print(f"{nomor:<4}{id_pasien:<12}{nama:<25}{nama_prioritas(prioritas):<12}")

    print("\n")
    print(f"{Warna.BOLD}Antrian Reguler{Warna.RESET}")
    print(garis(55))

    if not antrian_reguler:
        print(f"{Warna.ABU}Belum ada pasien di antrian reguler.{Warna.RESET}")
    else:
        print(f"{'No':<4}{'ID':<12}{'Nama':<25}{'Kategori':<12}")
        print(garis(55))
        for nomor, item in enumerate(antrian_reguler, start=1):
            urutan, id_pasien = item
            pasien = cari_pasien(id_pasien)
            nama = pasien["nama"] if pasien else "Data tidak ditemukan"
            print(f"{nomor:<4}{id_pasien:<12}{nama:<25}{'Reguler':<12}")

    print("\n")
    pesan_info(f"Total pasien dalam antrian: {len(id_dalam_antrian)}")
    jeda()


# FITUR REKAM MEDIS DAN UNDO
def catat_tindakan_medis():
    bersihkan_layar()
    judul_halaman("CATAT TINDAKAN MEDIS")

    id_pasien = input_tidak_kosong("Masukkan ID pasien: ").upper()
    pasien = cari_pasien(id_pasien)

    if not pasien:
        pesan_error("Data pasien tidak ditemukan.")
        jeda()
        return

    tampilkan_detail_pasien(pasien)
    diagnosa = input_tidak_kosong("Diagnosa        : ")
    resep = input_tidak_kosong("Resep           : ")
    tindakan = input_tidak_kosong("Tindakan        : ")

    catatan = {
        "waktu": waktu_sekarang(),
        "diagnosa": diagnosa,
        "resep": resep,
        "tindakan": tindakan
    }

    loading("Mencatat tindakan medis", 0.7)

    pasien["riwayat_medis"].append(catatan)
    riwayat_undo.append({
        "id_pasien": id_pasien,
        "catatan": catatan
    })

    simpan_otomatis()
    pesan_sukses("Tindakan medis berhasil dicatat.")
    jeda()


def tampilkan_riwayat_medis():
    bersihkan_layar()
    judul_halaman("RIWAYAT MEDIS PASIEN")

    id_pasien = input_tidak_kosong("Masukkan ID pasien: ").upper()
    pasien = cari_pasien(id_pasien)

    if not pasien:
        pesan_error("Data pasien tidak ditemukan.")
        jeda()
        return

    riwayat = pasien.get("riwayat_medis", [])
    tampilkan_detail_pasien(pasien)

    if not riwayat:
        pesan_peringatan("Pasien belum memiliki riwayat medis.")
        jeda()
        return

    print(f"{Warna.BOLD}Daftar Riwayat Medis:{Warna.RESET}\n")
    for nomor, catatan in enumerate(riwayat, start=1):
        print(f"{Warna.CYAN}{garis(60)}{Warna.RESET}")
        print(f"Catatan ke-{nomor}")
        print(f"Waktu     : {catatan['waktu']}")
        print(f"Diagnosa  : {catatan['diagnosa']}")
        print(f"Resep     : {catatan['resep']}")
        print(f"Tindakan  : {catatan['tindakan']}")
    print(f"{Warna.CYAN}{garis(60)}{Warna.RESET}")

    print("\n")
    catatan_terakhir = riwayat[-1]
    pesan_info("Riwayat tindakan terakhir:")
    print(f"Diagnosa terakhir : {catatan_terakhir['diagnosa']}")
    print(f"Resep terakhir    : {catatan_terakhir['resep']}")
    print(f"Tindakan terakhir : {catatan_terakhir['tindakan']}")

    jeda()


def batalkan_tindakan_terakhir():
    bersihkan_layar()
    judul_halaman("UNDO TINDAKAN TERAKHIR")

    if not riwayat_undo:
        pesan_peringatan("Belum ada tindakan medis yang bisa dibatalkan.")
        jeda()
        return

    data_undo = riwayat_undo.pop()
    id_pasien = data_undo["id_pasien"]
    catatan = data_undo["catatan"]
    pasien = cari_pasien(id_pasien)

    if not pasien:
        pesan_error("Data pasien untuk undo tidak ditemukan.")
        simpan_otomatis()
        jeda()
        return

    loading("Membatalkan tindakan terakhir", 0.7)

    riwayat = pasien.get("riwayat_medis", [])

    if riwayat and riwayat[-1] == catatan:
        riwayat.pop()
        simpan_otomatis()
        pesan_sukses("Tindakan medis terakhir berhasil dibatalkan.")
        print(f"Pasien   : {pasien['nama']} ({id_pasien})")
        print(f"Diagnosa : {catatan['diagnosa']}")
    else:
        pesan_peringatan("Catatan terakhir pasien sudah berubah, undo tidak dilakukan.")
        simpan_otomatis()

    jeda()


# FITUR TRANSAKSI
def catat_transaksi_pembayaran():
    bersihkan_layar()
    judul_halaman("CATAT TRANSAKSI PEMBAYARAN")

    id_pasien = input_tidak_kosong("Masukkan ID pasien : ").upper()
    pasien = cari_pasien(id_pasien)

    if not pasien:
        pesan_error("Data pasien tidak ditemukan.")
        jeda()
        return

    layanan = input_tidak_kosong("Nama layanan       : ")
    biaya = input_angka("Biaya pembayaran   : Rp", minimal=0)
    metode = input_tidak_kosong("Metode pembayaran  : ").title()

    transaksi = {
        "waktu": waktu_sekarang(),
        "id_pasien": id_pasien,
        "nama": pasien["nama"],
        "layanan": layanan,
        "biaya": biaya,
        "metode": metode
    }

    loading("Mencatat pembayaran", 0.7)

    log_transaksi.append(transaksi)
    simpan_otomatis()
    pesan_sukses("Transaksi pembayaran berhasil dicatat.")
    jeda()


def tampilkan_riwayat_transaksi():
    bersihkan_layar()
    judul_halaman("RIWAYAT TRANSAKSI")

    if not log_transaksi:
        pesan_peringatan("Belum ada transaksi pembayaran.")
        jeda()
        return

    total = 0
    print(f"{Warna.BOLD}{'No':<4}{'Waktu':<22}{'ID':<10}{'Nama':<20}{'Biaya':<15}{Warna.RESET}")
    print(garis(76))

    for nomor, transaksi in enumerate(log_transaksi, start=1):
        total += int(transaksi["biaya"])
        print(
            f"{nomor:<4}"
            f"{transaksi['waktu']:<22}"
            f"{transaksi['id_pasien']:<10}"
            f"{transaksi['nama']:<20}"
            f"{format_rupiah(int(transaksi['biaya'])):<15}"
        )

    print(garis(76))
    pesan_info(f"Total pemasukan: {format_rupiah(total)}")
    jeda()


# FITUR LAPORAN
def laporan_harian():
    bersihkan_layar()
    judul_halaman("LAPORAN HARIAN")

    total_pemasukan = sum(int(transaksi["biaya"]) for transaksi in log_transaksi)

    print(f"Total pasien terdaftar        : {len(pasien_db)}")
    print(f"Total pasien dilayani hari ini: {len(pasien_dilayani_hari_ini)}")
    print(f"Sisa antrian prioritas        : {len(antrian_prioritas)}")
    print(f"Sisa antrian reguler          : {len(antrian_reguler)}")
    print(f"Total transaksi pembayaran    : {len(log_transaksi)}")
    print(f"Total pemasukan               : {format_rupiah(total_pemasukan)}")

    print(f"\n{Warna.CYAN}{garis(72)}{Warna.RESET}")
    print(f"{Warna.BOLD}Urutkan daftar pasien:{Warna.RESET}")
    print("[1] Berdasarkan nama")
    print("[2] Berdasarkan ID")
    print("[0] Tidak menampilkan daftar pasien")

    pilihan = input("\nPilih opsi: ").strip()

    if pilihan == "0":
        jeda()
        return

    if pilihan not in ("1", "2"):
        pesan_error("Pilihan tidak valid.")
        jeda()
        return

    if not pasien_db:
        pesan_peringatan("Belum ada data pasien.")
        jeda()
        return

    kunci = "nama" if pilihan == "1" else "id"
    daftar_pasien = list(pasien_db.values())
    daftar_pasien.sort(key=lambda pasien: str(pasien[kunci]).lower())

    print("\n")
    print(f"{Warna.BOLD}{'No':<4}{'ID':<12}{'Nama':<25}{'Usia':<8}{'Kategori':<12}{Warna.RESET}")
    print(garis(65))

    for nomor, pasien in enumerate(daftar_pasien, start=1):
        print(
            f"{nomor:<4}"
            f"{pasien['id']:<12}"
            f"{pasien['nama']:<25}"
            f"{str(pasien['usia']):<8}"
            f"{pasien.get('kategori_terakhir', '-'):<12}"
        )

    jeda()


# MENU UTAMA
def tampilkan_menu_utama():
    """
    Menampilkan menu utama yang clean, menyatu, dan tetap memuat semua fitur.

    Fitur inti pada screenshot tetap ada:
    [1] Daftarkan Pasien Baru
    [2] Panggil Pasien Berikutnya
    [3] Cari Data Pasien
    [4] Catat Tindakan Medis
    [5] Batalkan Tindakan Terakhir (Undo)
    [6] Tampilkan Antrian Saat Ini
    [7] Laporan Harian
    [0] Keluar

    Fitur lain dari program sebelumnya tetap dipertahankan, tetapi disusun menyatu
    dalam satu menu tanpa tulisan "Fitur Tambahan Program".
    """
    bersihkan_layar()

    print(f"{Warna.CYAN}{garis(82)}{Warna.RESET}")
    print(f"{Warna.BOLD}{Warna.PUTIH}{'SISTEM MANAJEMEN KLINIK SEHAT BERSAMA'.center(82)}{Warna.RESET}")
    print(f"{Warna.DIM}{'By Kelompok 1'.center(82)}{Warna.RESET}")
    print(f"{Warna.CYAN}{garis(82)}{Warna.RESET}")
    print()

    # Menu dibuat menyatu, tetapi diberi jarak setiap beberapa pilihan
    # agar tetap rapi dan mudah dibaca.
    print(f"  {Warna.HIJAU}[1]{Warna.RESET}  Daftarkan Pasien Baru")
    print(f"  {Warna.HIJAU}[2]{Warna.RESET}  Panggil Pasien Berikutnya")
    print(f"  {Warna.HIJAU}[3]{Warna.RESET}  Cari Data Pasien")
    print()

    print(f"  {Warna.HIJAU}[4]{Warna.RESET}  Catat Tindakan Medis")
    print(f"  {Warna.HIJAU}[5]{Warna.RESET}  Batalkan Tindakan Terakhir (Undo)")
    print(f"  {Warna.HIJAU}[6]{Warna.RESET}  Tampilkan Antrian Saat Ini")
    print()

    print(f"  {Warna.HIJAU}[7]{Warna.RESET}  Laporan Harian")
    print(f"  {Warna.HIJAU}[8]{Warna.RESET}  Perbarui Data Pasien")
    print(f"  {Warna.HIJAU}[9]{Warna.RESET}  Tampilkan Semua Pasien")
    print()

    print(f"  {Warna.HIJAU}[10]{Warna.RESET} Catat Transaksi Pembayaran")
    print(f"  {Warna.HIJAU}[11]{Warna.RESET} Tampilkan Riwayat Transaksi")
    print(f"  {Warna.HIJAU}[12]{Warna.RESET} Tampilkan Riwayat Medis Pasien")
    print()

    print(f"  {Warna.KUNING}[13]{Warna.RESET} Simpan Data")
    print(f"  {Warna.KUNING}[14]{Warna.RESET} Muat Ulang Data")
    print(f"  {Warna.MERAH}[0]{Warna.RESET}  Keluar")
    print()

    print(f"{Warna.CYAN}{garis(82)}{Warna.RESET}")


def jalankan_program():
    """Fungsi utama untuk menjalankan seluruh program."""
    muat_data(tampilkan_loading=True)
    time.sleep(0.7)

    while True:
        tampilkan_menu_utama()
        pilihan = input(f"{Warna.BOLD}Pilih menu (0-14):{Warna.RESET} ").strip()

        if pilihan == "1":
            daftarkan_pasien()
        elif pilihan == "2":
            panggil_pasien_berikutnya()
        elif pilihan == "3":
            cari_data_pasien()
        elif pilihan == "4":
            catat_tindakan_medis()
        elif pilihan == "5":
            batalkan_tindakan_terakhir()
        elif pilihan == "6":
            tampilkan_antrian()
        elif pilihan == "7":
            laporan_harian()
        elif pilihan == "8":
            perbarui_data_pasien()
        elif pilihan == "9":
            tampilkan_semua_pasien()
        elif pilihan == "10":
            catat_transaksi_pembayaran()
        elif pilihan == "11":
            tampilkan_riwayat_transaksi()
        elif pilihan == "12":
            tampilkan_riwayat_medis()
        elif pilihan == "13":
            bersihkan_layar()
            judul_halaman("SIMPAN DATA")
            simpan_data(tampilkan_loading=True)
            jeda()
        elif pilihan == "14":
            bersihkan_layar()
            judul_halaman("MUAT ULANG DATA")
            muat_data(tampilkan_loading=True)
            jeda()
        elif pilihan == "0":
            bersihkan_layar()
            judul_halaman("KELUAR PROGRAM")
            simpan_data(tampilkan_loading=True)
            pesan_sukses("Terima kasih. Program selesai dijalankan.")
            break
        else:
            pesan_error("Pilihan tidak tersedia. Silakan pilih menu 0 sampai 14.")
            time.sleep(1.1)


if __name__ == "__main__":
    jalankan_program()