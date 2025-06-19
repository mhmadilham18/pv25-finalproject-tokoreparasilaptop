from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QLineEdit, QTextEdit,
                             QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox, QFormLayout)
from PyQt5.QtCore import Qt
from datetime import datetime
import database


class RepairForm(QWidget):
    def __init__(self, nama_pegawai, update_callback=None):
        super().__init__()
        self.nama_pegawai_login = nama_pegawai
        self.update_callback = update_callback
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignTop)

        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(20)
        form_layout.setLabelAlignment(Qt.AlignLeft)

        self.cust_name_input = QLineEdit()
        self.model_device_input = QLineEdit()
        self.pegawai_input = QComboBox()
        self.keluhan_input = QTextEdit()
        self.detail_input = QTextEdit()

        self.populate_pegawai_combo()

        form_layout.addRow(QLabel("Nama Pelanggan:"), self.cust_name_input)
        form_layout.addRow(QLabel("Model Device:"), self.model_device_input)
        form_layout.addRow(QLabel("Nama Pegawai:"), self.pegawai_input)
        form_layout.addRow(QLabel("Keluhan:"), self.keluhan_input)
        form_layout.addRow(QLabel("Detail Perbaikan:"), self.detail_input)

        simpan_button = QPushButton("Simpan Data Perbaikan")
        simpan_button.clicked.connect(self.simpan_data)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(simpan_button)

        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)

    def populate_pegawai_combo(self):
        conn = database.get_db_connection()
        pegawai_list = conn.execute("SELECT id, nama FROM pegawai ORDER BY nama").fetchall()
        conn.close()

        current_index = 0
        for i, p in enumerate(pegawai_list):
            self.pegawai_input.addItem(p["nama"], p["id"])
            if p["nama"] == self.nama_pegawai_login:
                current_index = i
        self.pegawai_input.setCurrentIndex(current_index)

    def simpan_data(self):
        nama_pelanggan = self.cust_name_input.text().strip()
        model_device = self.model_device_input.text().strip()
        keluhan = self.keluhan_input.toPlainText().strip()
        detail_perbaikan = self.detail_input.toPlainText().strip()
        id_pegawai = self.pegawai_input.currentData()

        if not all([nama_pelanggan, model_device, keluhan]):
            QMessageBox.warning(self, "Peringatan", "Nama Pelanggan, Model, dan Keluhan harus diisi.")
            return

        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO perbaikan (nama_pelanggan, model_laptop, keluhan, detail_perbaikan, waktu, id_pegawai)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (nama_pelanggan, model_device, keluhan, detail_perbaikan, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             id_pegawai)
        )
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Sukses", f"Data perbaikan berhasil disimpan dengan ID: {new_id}")
        self.clear_form()
        if self.update_callback:
            self.update_callback()

    def clear_form(self):
        self.cust_name_input.clear()
        self.model_device_input.clear()
        self.keluhan_input.clear()
        self.detail_input.clear()