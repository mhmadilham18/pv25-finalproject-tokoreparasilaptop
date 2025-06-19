import sqlite3
import hashlib
from datetime import datetime, timedelta

DB_NAME = "service_management.db"


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pegawai (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS perbaikan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_pelanggan TEXT NOT NULL,
            model_laptop TEXT NOT NULL,
            keluhan TEXT NOT NULL,
            detail_perbaikan TEXT,
            status TEXT DEFAULT 'Baru Masuk',
            waktu TEXT NOT NULL,
            id_pegawai INTEGER,
            FOREIGN KEY (id_pegawai) REFERENCES pegawai (id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transaksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_perbaikan INTEGER NOT NULL,
            total_biaya REAL NOT NULL,
            total_uang_dibayar REAL NOT NULL,
            kembalian REAL NOT NULL,
            waktu TEXT NOT NULL,
            FOREIGN KEY (id_perbaikan) REFERENCES perbaikan (id)
        )
    """)
    conn.commit()
    conn.close()


def init_pegawai_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    if cursor.execute("SELECT COUNT(*) FROM pegawai").fetchone()[0] == 0:
        def hash_password(password):
            return hashlib.sha256(password.encode()).hexdigest()

        pegawai_awal = [
            ('Ilham', 'ilham', hash_password('ilham123')),
            ('Andi', 'andi', hash_password('andi123')),
            ('Budi', 'budi', hash_password('budi123')),
            ('Citra', 'citra', hash_password('citra123')),
        ]
        cursor.executemany("INSERT INTO pegawai (nama, username, password) VALUES (?, ?, ?)", pegawai_awal)
        conn.commit()
    conn.close()


def init_dummy_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    if cursor.execute("SELECT COUNT(*) FROM perbaikan").fetchone()[0] == 0:
        print("Database kosong, mengisi dengan data dummy...")

        repairs = [
            ('Budi Santoso', 'Dell XPS 15', 'Layar bergaris-garis.', 'Ganti panel LCD.', 'Selesai',
             (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"), 1),
            ('Siti Aminah', 'MacBook Pro 13', 'Keyboard tidak berfungsi sebagian.',
             'Pembersihan dan perbaikan konektor keyboard.', 'Dikerjakan',
             (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"), 2),
            ('Joko Susilo', 'Lenovo ThinkPad T480', 'Baterai cepat habis.', 'Kalibrasi dan penggantian baterai.',
             'Selesai', (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"), 3),
            ('Dewi Lestari', 'HP Spectre x360', 'Laptop mati total.', 'Perbaikan motherboard, ada korsleting.',
             'Dikerjakan', (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S"), 4),
            (
            'Ahmad Yani', 'Asus ROG Strix', 'Overheat saat main game.', 'Pembersihan heatsink dan ganti thermal paste.',
            'Selesai', (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S"), 1),
            ('Rina Hartono', 'Acer Swift 3', 'Gagal booting, masuk BIOS terus.',
             'Install ulang Windows dan perbaikan bootloader.', 'Selesai',
             (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S"), 2),
        ]

        cursor.executemany("""
            INSERT INTO perbaikan (nama_pelanggan, model_laptop, keluhan, detail_perbaikan, status, waktu, id_pegawai)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, repairs)

        transactions = [
            (1, 1500000.0, 1500000.0, 0.0, (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")),
            (3, 850000.0, 900000.0, 50000.0, (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")),
            (5, 450000.0, 500000.0, 50000.0, (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S")),
        ]

        cursor.executemany("""
            INSERT INTO transaksi (id_perbaikan, total_biaya, total_uang_dibayar, kembalian, waktu)
            VALUES (?, ?, ?, ?, ?)
        """, transactions)

        conn.commit()
    conn.close()


def init_database():
    create_tables()
    init_pegawai_data()
    init_dummy_data()