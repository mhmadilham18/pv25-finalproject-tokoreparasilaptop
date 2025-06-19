from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QPushButton, QMessageBox)
import database


class EditTransactionDialog(QDialog):
    def __init__(self, transaction_id, parent=None):
        super().__init__(parent)
        self.transaction_id = transaction_id

        self.setWindowTitle(f"Edit Data Transaksi ID: {self.transaction_id}")
        self.setMinimumWidth(400)

        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)

        self.total_biaya_input = QLineEdit()
        self.total_uang_dibayar_input = QLineEdit()
        self.kembalian_input = QLineEdit()
        self.kembalian_input.setReadOnly(True)

        self.total_biaya_input.textChanged.connect(self.update_kembalian)
        self.total_uang_dibayar_input.textChanged.connect(self.update_kembalian)

        form_layout.addRow("Total Biaya (Rp):", self.total_biaya_input)
        form_layout.addRow("Total Uang Dibayar (Rp):", self.total_uang_dibayar_input)
        form_layout.addRow("Kembalian (Rp):", self.kembalian_input)

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
        data = conn.execute("SELECT * FROM transaksi WHERE id = ?", (self.transaction_id,)).fetchone()
        conn.close()

        if data:
            self.total_biaya_input.setText(str(data['total_biaya']))
            self.total_uang_dibayar_input.setText(str(data['total_uang_dibayar']))

    def update_kembalian(self):
        try:
            biaya = float(self.total_biaya_input.text() or 0)
            bayar = float(self.total_uang_dibayar_input.text() or 0)
            self.kembalian_input.setText(f"{bayar - biaya:,.0f}".replace(",", "."))
        except ValueError:
            self.kembalian_input.clear()

    def save_changes(self):
        try:
            total_biaya = float(self.total_biaya_input.text())
            total_uang_dibayar = float(self.total_uang_dibayar_input.text())
            kembalian = total_uang_dibayar - total_biaya
        except ValueError:
            QMessageBox.warning(self, "Peringatan", "Input harus berupa angka.")
            return

        try:
            conn = database.get_db_connection()
            conn.execute("""
                UPDATE transaksi
                SET total_biaya = ?, total_uang_dibayar = ?, kembalian = ?
                WHERE id = ?
            """, (total_biaya, total_uang_dibayar, kembalian, self.transaction_id))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Sukses", "Data transaksi berhasil diperbarui.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan data: {e}")