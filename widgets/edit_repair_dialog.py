from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QTextEdit, QComboBox, QPushButton, QMessageBox)
import database


class EditRepairDialog(QDialog):
    def __init__(self, repair_id, parent=None):
        super().__init__(parent)
        self.repair_id = repair_id

        self.setWindowTitle(f"Edit Data Perbaikan ID: {self.repair_id}")
        self.setMinimumWidth(750)

        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)

        self.nama_pelanggan_input = QLineEdit()
        self.model_laptop_input = QLineEdit()
        self.keluhan_input = QTextEdit()
        self.detail_input = QTextEdit()
        self.status_input = QComboBox()
        self.status_input.addItems(['Baru Masuk', 'Dikerjakan', 'Selesai', 'Diambil'])

        self.keluhan_input.setMinimumHeight(100)
        self.detail_input.setMinimumHeight(100)

        form_layout.addRow("Nama Pelanggan:", self.nama_pelanggan_input)
        form_layout.addRow("Model Laptop:", self.model_laptop_input)
        form_layout.addRow("Status:", self.status_input)
        form_layout.addRow("Keluhan:", self.keluhan_input)
        form_layout.addRow("Detail Perbaikan:", self.detail_input)

        self.save_button = QPushButton("Simpan Perubahan")
        self.cancel_button = QPushButton("Batal")

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)

        self.save_button.clicked.connect(self.save_changes)
        self.cancel_button.clicked.connect(self.reject)

        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)

        self.load_data()

    def load_data(self):
        conn = database.get_db_connection()
        data = conn.execute("SELECT * FROM perbaikan WHERE id = ?", (self.repair_id,)).fetchone()
        conn.close()
        if data:
            self.nama_pelanggan_input.setText(data['nama_pelanggan'])
            self.model_laptop_input.setText(data['model_laptop'])
            self.keluhan_input.setText(data['keluhan'])
            self.detail_input.setText(data['detail_perbaikan'])
            self.status_input.setCurrentText(data['status'])

    def save_changes(self):
        nama_pelanggan = self.nama_pelanggan_input.text().strip()
        model_laptop = self.model_laptop_input.text().strip()
        status = self.status_input.currentText()
        keluhan = self.keluhan_input.toPlainText().strip()
        detail = self.detail_input.toPlainText().strip()
        if not all([nama_pelanggan, model_laptop, keluhan]):
            QMessageBox.warning(self, "Peringatan", "Nama Pelanggan, Model, dan Keluhan tidak boleh kosong.")
            return
        try:
            conn = database.get_db_connection()
            conn.execute(
                "UPDATE perbaikan SET nama_pelanggan = ?, model_laptop = ?, status = ?, keluhan = ?, detail_perbaikan = ? WHERE id = ?",
                (nama_pelanggan, model_laptop, status, keluhan, detail, self.repair_id))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Sukses", "Data perbaikan berhasil diperbarui.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan data: {e}")