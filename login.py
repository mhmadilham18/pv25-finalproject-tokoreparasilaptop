from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
                             QHBoxLayout, QMessageBox, QCheckBox)  # <-- Tambahkan QCheckBox
from PyQt5.QtCore import Qt, QSettings  # <-- Tambahkan QSettings
from PyQt5.QtGui import QIcon, QPixmap
import database
import hashlib


class LoginForm(QWidget):
    def __init__(self, switch_to_dashboard, switch_to_login_func):
        super().__init__()
        self.switch_to_dashboard = switch_to_dashboard

        self.settings = QSettings("MyCompany", "ServiceApp")
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        container = QWidget()
        container_layout = QVBoxLayout()
        container.setObjectName("mainContainer")
        container_layout.setContentsMargins(50, 40, 50, 40)
        container_layout.setAlignment(Qt.AlignCenter)
        container.setLayout(container_layout)
        container.setFixedWidth(650)

        icon_label = QLabel()
        pixmap = QPixmap("assets/login-icon.png")
        pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignCenter)

        heading = QLabel("Sistem Manajemen Service Komputer")
        heading.setAlignment(Qt.AlignCenter)
        heading.setWordWrap(True)
        heading.setObjectName('loginHeading')

        subheading = QLabel("Silakan login untuk mengakses dashboard")
        subheading.setAlignment(Qt.AlignCenter)
        subheading.setWordWrap(True)
        subheading.setObjectName(('loginSubHeading'))


        username_label = QLabel("Username")
        username_label.setObjectName("formTitle")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Masukkan Username Anda")

        password_label = QLabel("Password")
        password_label.setObjectName("formTitle")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Masukkan Password Anda")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.remember_me_checkbox = QCheckBox("Ingat Saya")
        self.remember_me_checkbox.setObjectName('checkBox')

        login_button = QPushButton("Login")
        login_button.clicked.connect(self.check_login)
        self.password_input.returnPressed.connect(self.check_login)

        form_layout = QVBoxLayout()
        form_layout.setSpacing(10)
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.remember_me_checkbox)
        form_layout.addSpacing(20)
        form_layout.addWidget(login_button)

        container_layout.addWidget(icon_label)
        container_layout.addWidget(heading)
        container_layout.addWidget(subheading)
        container_layout.addLayout(form_layout)

        main_layout.addWidget(container)
        self.setLayout(main_layout)

    def check_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.show_message("Input Tidak Lengkap", "Username dan Password tidak boleh kosong.", "warning")
            return

        conn = database.get_db_connection()
        user_record = conn.execute("SELECT nama, password FROM pegawai WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user_record:
            stored_password_hash = user_record['password']
            input_password_hash = hashlib.sha256(password.encode()).hexdigest()

            if stored_password_hash == input_password_hash:
                # Logika untuk menyimpan atau menghapus sesi
                if self.remember_me_checkbox.isChecked():
                    self.settings.setValue("last_user", username)
                else:
                    self.settings.remove("last_user")

                nama_pegawai = user_record['nama']
                self.switch_to_dashboard(nama_pegawai)
                self.password_input.clear()
                return

        self.show_message("Login Gagal", "Pastikan Username dan Password yang dimasukkan benar.", "error")

    def load_settings(self):
        last_user = self.settings.value("last_user", defaultValue=None)
        if last_user:
            self.username_input.setText(last_user)
            self.remember_me_checkbox.setChecked(True)
            self.password_input.setFocus()

    def show_message(self, title, message, status="info"):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(f"<h3>{title}</h3><p style='font-size:14px;'>{message}</p>")

        icon_map = {
            "success": QMessageBox.Information, "information": QMessageBox.Information,
            "error": QMessageBox.Critical, "critical": QMessageBox.Critical,
            "warning": QMessageBox.Warning,
        }
        msg.setIcon(icon_map.get(status, QMessageBox.NoIcon))
        msg.exec_()