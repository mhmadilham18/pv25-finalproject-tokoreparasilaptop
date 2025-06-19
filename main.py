import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QStackedWidget,
                             QAction, QStatusBar, QLabel, QMessageBox,
                             QDialog, QVBoxLayout, QHBoxLayout, QPushButton)
from PyQt5.QtCore import QSettings, Qt

from login import LoginForm
from dashboard import Dashboard
import database


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tentang Aplikasi")
        self.setFixedWidth(650)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        summary_label = QLabel()
        summary_label.setWordWrap(True)
        summary_label.setTextFormat(Qt.RichText)
        summary_text = """
        <h3>Sistem Manajemen Service Komputer</h3>
        <p>Aplikasi ini adalah sistem manajemen desktop yang dirancang untuk membantu pemilik atau pegawai toko servis komputer dalam mencatat, melacak, dan mengelola data perbaikan serta transaksi secara efisien.</p>
        
        <hr> 
        <b>Fitur Utama:</b>
        <ul>
            <li>Manajemen Login Pegawai yang aman.</li>
            <li>Pencatatan Data Perbaikan Pelanggan secara detail.</li>
            <li>Sistem Pencatatan Transaksi dan Pendapatan.</li>
            <li>Fitur untuk melihat dan menyegarkan data.</li>
            <li>Ekspor Laporan (Data Perbaikan & Transaksi) ke format CSV.</li>
        </ul>

        <p>Dikembangkan menggunakan Python dengan library PyQt5 untuk antarmuka pengguna dan SQLite untuk penyimpanan data lokal yang persisten.</p>

        <hr> 

        <p><b>Pengembang:</b><br>
        M. Ilham Abdul Shaleh (F1D022061)</p>

        <p><b>Versi:</b> 2.1 - 2025</p>
        """
        summary_label.setText(summary_text)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addStretch()

        layout.addWidget(summary_label)
        layout.addLayout(button_layout)

        self.adjustSize()


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        database.init_database()

        self.setWindowTitle("Sistem Manajemen Service Komputer")
        self.setWindowIcon(QIcon("assets/icon-app.png"))

        self.settings = QSettings("MyCompany", "ServiceApp")

        self._create_menu_bar()
        self._create_status_bar()
        self._load_stylesheet()

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.dashboard = None
        self.login_form = LoginForm(self.show_dashboard, self.switch_to_login)

        self.stacked_widget.addWidget(self.login_form)

        self.resizeAndCenter(0.4, 0.6)

        self.try_auto_login()

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")

        self.logout_action = QAction("Logout", self)
        self.logout_action.triggered.connect(self.logout)
        self.logout_action.setEnabled(False)
        file_menu.addAction(self.logout_action)

        file_menu.addSeparator()

        self.export_action = QAction("&Export Data...", self)
        self.export_action.triggered.connect(self.export_data)
        self.export_action.setEnabled(False)
        file_menu.addAction(self.export_action)

        file_menu.addSeparator()

        exit_action = QAction("&Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = menu_bar.addMenu("&Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def _create_status_bar(self):
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        status_bar.showMessage("Aplikasi Siap.")


    def _load_stylesheet(self):
        try:
            with open("styles.qss", "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print("Peringatan: styles.qss tidak ditemukan. Tampilan default akan digunakan.")

    def resizeAndCenter(self, width_ratio=0.6, height_ratio=0.6):
        screen = self.screen().availableGeometry()
        width = int(screen.width() * width_ratio)
        height = int(screen.height() * height_ratio)
        self.resize(width, height)
        self.move((screen.width() - width) // 2, (screen.height() - height) // 2)

    def show_dashboard(self, nama_pegawai):
        if self.dashboard is not None:
            self.stacked_widget.removeWidget(self.dashboard)
            self.dashboard.deleteLater()

        self.dashboard = Dashboard(nama_pegawai)
        self.stacked_widget.addWidget(self.dashboard)

        self.setCurrentWidget(self.dashboard)
        self.resizeAndCenter(0.8, 0.85)

        self.export_action.setEnabled(True)
        self.logout_action.setEnabled(True)

    def setCurrentWidget(self, widget):
        self.stacked_widget.setCurrentWidget(widget)
        if isinstance(widget, LoginForm):
            self.setWindowTitle("Login - Sistem Manajemen")
        elif isinstance(widget, Dashboard):
            self.setWindowTitle("Dashboard - Sistem Manajemen")

    def switch_to_login(self):
        self.export_action.setEnabled(False)
        self.logout_action.setEnabled(False)
        self.statusBar().showMessage("Silakan login untuk memulai.")
        self.setCurrentWidget(self.login_form)
        self.resizeAndCenter(0.4, 0.6)

    def logout(self):
        self.settings.remove("last_user")
        self.switch_to_login()

    def try_auto_login(self):
        last_user = self.settings.value("last_user", defaultValue=None)
        if last_user:
            conn = database.get_db_connection()
            user_record = conn.execute("SELECT nama FROM pegawai WHERE username = ?", (last_user,)).fetchone()
            conn.close()
            if user_record:
                self.show_dashboard(user_record['nama'])

    def export_data(self):
        if self.dashboard and self.dashboard.data_view:
            self.dashboard.data_view.export_data_to_csv()

    def show_about_dialog(self):
        dialog = AboutDialog(self)
        dialog.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())