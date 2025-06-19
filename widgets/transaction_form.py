from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout,
                             QHBoxLayout, QMessageBox, QFormLayout, QComboBox, QGroupBox)
from PyQt5.QtCore import Qt
import database


class TransactionForm(QWidget):
    def __init__(self, update_callback=None):
        super().__init__()
        self.update_callback = update_callback
        self.repair_data = {}
        self.init_ui()
        self._populate_repairs_combo()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignTop)

        selection_group = QGroupBox("Pilih Perbaikan yang Sudah Selesai")
        selection_layout = QFormLayout(selection_group)
        selection_layout.setVerticalSpacing(15)

        self.repairs_combo = QComboBox()
        self.repairs_combo.currentIndexChanged.connect(self._on_repair_selected)

        self.customer_name_display = QLineEdit()
        self.customer_name_display.setReadOnly(True)
        self.customer_name_display.setStyleSheet("background-color: #f0f0f0;")

        self.laptop_model_display = QLineEdit()
        self.laptop_model_display.setReadOnly(True)
        self.laptop_model_display.setStyleSheet("background-color: #f0f0f0;")

        selection_layout.addRow(QLabel("Pilih ID Perbaikan:"), self.repairs_combo)
        selection_layout.addRow(QLabel("Nama Pelanggan:"), self.customer_name_display)
        selection_layout.addRow(QLabel("Model Laptop:"), self.laptop_model_display)

        payment_group = QGroupBox("Detail Pembayaran")
        form_layout = QFormLayout(payment_group)

        self.total_biaya_input = QLineEdit()
        self.total_uang_dibayar_input = QLineEdit()
        self.kembalian_input = QLineEdit()
        self.kembalian_input.setReadOnly(True)
        self.kembalian_input.setStyleSheet("background-color: #f0f0f0;")

        self.total_biaya_input.textChanged.connect(self._update_kembalian)
        self.total_uang_dibayar_input.textChanged.connect(self._update_kembalian)

        form_layout.addRow(QLabel("Total Biaya (Rp):"), self.total_biaya_input)
        form_layout.addRow(QLabel("Total Uang Dibayar (Rp):"), self.total_uang_dibayar_input)
        form_layout.addRow(QLabel("Kembalian (Rp):"), self.kembalian_input)

        simpan_button = QPushButton("Simpan Data Transaksi")
        simpan_button.clicked.connect(self.simpan_data)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(simpan_button)

        main_layout.addWidget(selection_group)
        main_layout.addWidget(payment_group)
        main_layout.addLayout(button_layout)
        main_layout.addStretch()

    def _populate_repairs_combo(self):
        self.repairs_combo.clear()
        self.repair_data.clear()

        conn = database.get_db_connection()
        query = """
                    SELECT p.id, p.nama_pelanggan, p.model_laptop 
                    FROM perbaikan p
                    LEFT JOIN transaksi t ON p.id = t.id_perbaikan
                    WHERE TRIM(p.status) = 'Selesai' AND t.id IS NULL
                """
        repairs_to_pay = conn.execute(query).fetchall()
        conn.close()

        self.repairs_combo.addItem("--- Pilih Perbaikan ---", None)  # Opsi default
        for repair in repairs_to_pay:
            display_text = f"ID: {repair['id']} - {repair['nama_pelanggan']}"
            self.repairs_combo.addItem(display_text, repair['id'])
            self.repair_data[repair['id']] = repair

    def _on_repair_selected(self):
        selected_id = self.repairs_combo.currentData()

        if selected_id and selected_id in self.repair_data:
            repair_info = self.repair_data[selected_id]
            self.customer_name_display.setText(repair_info['nama_pelanggan'])
            self.laptop_model_display.setText(repair_info['model_laptop'])
        else:
            self.customer_name_display.clear()
            self.laptop_model_display.clear()

    def _update_kembalian(self):
        try:
            biaya = float(self.total_biaya_input.text() or 0)
            bayar = float(self.total_uang_dibayar_input.text() or 0)
            self.kembalian_input.setText(f"{bayar - biaya:,.0f}".replace(",", "."))
        except ValueError:
            self.kembalian_input.clear()

    def clear_form(self):
        self._populate_repairs_combo()
        self.total_biaya_input.clear()
        self.total_uang_dibayar_input.clear()
        self.kembalian_input.clear()

    def simpan_data(self):
        id_perbaikan = self.repairs_combo.currentData()
        if not id_perbaikan:
            QMessageBox.warning(self, "Peringatan", "Anda harus memilih satu data perbaikan terlebih dahulu.")
            return

        try:
            total_biaya = float(self.total_biaya_input.text() or 0)
            total_uang_dibayar = float(self.total_uang_dibayar_input.text() or 0)
            kembalian = total_uang_dibayar - total_biaya
        except ValueError:
            QMessageBox.warning(self, "Peringatan", "Input biaya dan pembayaran harus berupa angka.")
            return

        if total_biaya <= 0:
            QMessageBox.warning(self, "Peringatan", "Total Biaya harus diisi.")
            return

        if kembalian < 0:
            QMessageBox.warning(self, "Peringatan", "Uang yang dibayarkan kurang.")
            return

        from datetime import datetime
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO transaksi (id_perbaikan, total_biaya, total_uang_dibayar, kembalian, waktu)
               VALUES (?, ?, ?, ?, ?)""",
            (id_perbaikan, total_biaya, total_uang_dibayar, kembalian, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        new_id = cursor.lastrowid
        cursor.execute("UPDATE perbaikan SET status = 'Diambil' WHERE id = ?", (id_perbaikan,))

        conn.commit()
        conn.close()

        QMessageBox.information(self, "Sukses", f"Data transaksi berhasil disimpan dengan ID: {new_id}")
        self.clear_form()
        if self.update_callback:
            self.update_callback()