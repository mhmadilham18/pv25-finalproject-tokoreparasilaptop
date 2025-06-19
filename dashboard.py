from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QTabWidget
from PyQt5.QtCore import Qt
from widgets.cards import CardWidget
from widgets.repair_form import RepairForm
from widgets.transaction_form import TransactionForm
from widgets.data_view import DataViewWidget
import database
from datetime import datetime


class Dashboard(QWidget):
    def __init__(self, nama_pegawai=""):
        super().__init__()
        self.nama_pegawai = nama_pegawai
        self.data_view = None
        self.init_ui()
        self.update_cards()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        header_label = QLabel(f"Selamat Datang, {self.nama_pegawai}!")
        header_label.setObjectName("headerLabel")
        main_layout.addWidget(header_label)

        self.setup_cards()
        main_layout.addLayout(self.cards_layout)

        tab_widget = QTabWidget()
        tab_widget.setFocusPolicy(Qt.NoFocus)

        repair_form = RepairForm(self.nama_pegawai, self.update_all)
        transaction_form = TransactionForm(self.update_all)
        self.data_view = DataViewWidget()

        tab_widget.addTab(repair_form, "Input Perbaikan")
        tab_widget.addTab(transaction_form, "Input Transaksi")
        tab_widget.addTab(self.data_view, "Lihat Semua Data")

        main_layout.addWidget(tab_widget)

    def setup_cards(self):
        self.cards_layout = QHBoxLayout()
        self.cards_layout.setSpacing(20)
        self.card_hari_ini = CardWidget("Perbaikan Hari Ini", "0", "assets/repair-today.png")
        self.card_total_perbaikan = CardWidget("Total Semua Perbaikan", "0", "assets/repair-total.png")
        self.card_total_pendapatan = CardWidget("Total Pendapatan", "Rp 0", "assets/income-total.png")
        self.card_pelanggan_baru = CardWidget("Pelanggan Baru Hari Ini", "0", "assets/cust-total.png")
        self.cards_layout.addWidget(self.card_hari_ini)
        self.cards_layout.addWidget(self.card_total_perbaikan)
        self.cards_layout.addWidget(self.card_total_pendapatan)
        self.cards_layout.addWidget(self.card_pelanggan_baru)

    def update_cards(self):
        conn = database.get_db_connection()
        today_str = datetime.now().strftime("%Y-%m-%d")

        repairs_today_query = "SELECT COUNT(id) FROM perbaikan WHERE DATE(waktu) = ?"
        repairs_today = conn.execute(repairs_today_query, (today_str,)).fetchone()[0]

        total_repairs = conn.execute("SELECT COUNT(id) FROM perbaikan").fetchone()[0]

        total_income_result = conn.execute("SELECT SUM(total_biaya) FROM transaksi").fetchone()[0]
        total_income = total_income_result if total_income_result is not None else 0

        new_customers_query = "SELECT COUNT(DISTINCT nama_pelanggan) FROM perbaikan WHERE DATE(waktu) = ?"
        new_customers_today = conn.execute(new_customers_query, (today_str,)).fetchone()[0]

        conn.close()

        self.card_hari_ini.update_value(str(repairs_today))
        self.card_total_perbaikan.update_value(str(total_repairs))
        self.card_total_pendapatan.update_value(f"Rp {total_income:,.0f}".replace(",", "."))
        self.card_pelanggan_baru.update_value(str(new_customers_today))

    def update_all(self):
        self.update_cards()
        if self.data_view:
            self.data_view.refresh_all_data()