from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget,
                             QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox,
                             QPushButton, QDialog, QSizePolicy)
from PyQt5.QtCore import Qt
import database
import csv
from datetime import datetime, timedelta
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from .edit_repair_dialog import EditRepairDialog
from .edit_transaction_dialog import EditTransactionDialog

plt.style.use('fivethirtyeight')
plt.rcParams['axes.labelcolor'] = '#434343'
plt.rcParams['xtick.color'] = '#636363'
plt.rcParams['ytick.color'] = '#636363'


class RepairChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(5, 3), dpi=100, facecolor='none')
        self.canvas = FigureCanvas(self.figure)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setMinimumWidth(450)
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

    def update_chart(self):
        conn = database.get_db_connection()
        query = "SELECT DATE(waktu) as repair_date, COUNT(*) as repair_count FROM perbaikan WHERE DATE(waktu) >= DATE('now', '-6 days', 'localtime') GROUP BY repair_date ORDER BY repair_date ASC;"
        data = {row['repair_date']: row['repair_count'] for row in conn.execute(query).fetchall()}
        conn.close()
        dates, counts = [], []
        for i in range(7):
            day = datetime.now() - timedelta(days=6 - i)
            dates.append(day.strftime("%a"))
            counts.append(data.get(day.strftime("%Y-%m-%d"), 0))

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('#F0F0F0')

        bars = ax.bar(dates, counts, color='#3498DB', width=0.6)
        ax.set_title('Jumlah Perbaikan (7 Hari Terakhir)', fontsize=14, color='#333333')
        ax.set_ylabel('Jumlah Unit', fontsize=10)
        ax.grid(True, which='major', axis='y', linestyle='--', linewidth=0.5)
        ax.bar_label(bars, padding=3, fontsize=9, color='#333333')

        self.figure.tight_layout()
        self.canvas.draw()


class TransactionChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(5, 3), dpi=100, facecolor='none')
        self.canvas = FigureCanvas(self.figure)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setMinimumWidth(450)
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

    def update_chart(self):
        conn = database.get_db_connection()
        query = "SELECT DATE(waktu) as trans_date, SUM(total_biaya) as daily_income FROM transaksi WHERE DATE(waktu) >= DATE('now', '-6 days', 'localtime') GROUP BY trans_date ORDER BY trans_date ASC;"
        data = {row['trans_date']: row['daily_income'] for row in conn.execute(query).fetchall()}
        conn.close()

        dates, incomes = [], []
        for i in range(7):
            day = datetime.now() - timedelta(days=6 - i)
            dates.append(day.strftime("%a"))
            incomes.append(data.get(day.strftime("%Y-%m-%d"), 0))

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('#F0F0F0')

        bars = ax.bar(dates, incomes, color='#2ECC71', width=0.6)
        ax.set_title('Pendapatan (7 Hari Terakhir)', fontsize=14, color='#333333')
        ax.set_ylabel('Pendapatan (Rp)', fontsize=10)

        def currency_formatter(x, pos):
            if x >= 1_000_000:
                return f'{x / 1_000_000:.1f} Jt'
            if x >= 1_000:
                return f'{int(x / 1_000)} Rb'
            return f'{int(x)}'

        ax.get_yaxis().set_major_formatter(plt.FuncFormatter(currency_formatter))
        ax.grid(True, which='major', axis='y', linestyle='--', linewidth=0.5)
        ax.bar_label(bars, padding=3, fontsize=9, color='#333333')
        self.figure.tight_layout()
        self.canvas.draw()

class DataViewWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.refresh_all_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        self.data_tabs = QTabWidget()
        repair_widget = QWidget()
        repair_layout = QHBoxLayout(repair_widget)
        self.repair_table = self._create_table(["ID", "Pelanggan", "Model Laptop", "Pegawai", "Status", "Waktu"])
        self.repair_chart = RepairChartWidget()
        repair_layout.addWidget(self.repair_table)
        repair_layout.addWidget(self.repair_chart)
        trans_widget = QWidget()
        trans_layout = QHBoxLayout(trans_widget)
        self.transaction_table = self._create_table(
            ["ID Transaksi", "ID Perbaikan", "Total Biaya", "Dibayar", "Kembalian", "Waktu"])
        self.transaction_chart = TransactionChartWidget()
        trans_layout.addWidget(self.transaction_table)
        trans_layout.addWidget(self.transaction_chart)
        self.data_tabs.addTab(repair_widget, "Data Perbaikan")
        self.data_tabs.addTab(trans_widget, "Data Transaksi")
        main_layout.addWidget(self.data_tabs)
        self.repair_table.cellDoubleClicked.connect(self.edit_repair_data)
        self.transaction_table.cellDoubleClicked.connect(self.edit_transaction_data)
        self.setup_table_columns()

    def setup_table_columns(self):
        header_repair = self.repair_table.horizontalHeader()
        header_repair.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header_repair.setSectionResizeMode(1, QHeaderView.Stretch)
        header_repair.setSectionResizeMode(2, QHeaderView.Stretch)
        header_repair.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header_repair.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header_repair.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header_trans = self.transaction_table.horizontalHeader()
        for i in range(header_trans.count()):
            header_trans.setSectionResizeMode(i, QHeaderView.ResizeToContents)

    def _create_table(self, headers):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.verticalHeader().setVisible(False)
        return table

    def refresh_all_data(self):
        self._populate_repair_table()
        self._populate_transaction_table()
        self.repair_chart.update_chart()
        self.transaction_chart.update_chart()

    def _populate_repair_table(self):
        self.repair_table.setRowCount(0)
        conn = database.get_db_connection()
        query = "SELECT p.id, p.nama_pelanggan, p.model_laptop, peg.nama, p.status, p.waktu FROM perbaikan p LEFT JOIN pegawai peg ON p.id_pegawai = peg.id ORDER BY p.id DESC"
        for row, data in enumerate(conn.execute(query).fetchall()):
            self.repair_table.insertRow(row)
            self.repair_table.setItem(row, 0, QTableWidgetItem(str(data['id'])))
            self.repair_table.setItem(row, 1, QTableWidgetItem(data['nama_pelanggan']))
            self.repair_table.setItem(row, 2, QTableWidgetItem(data['model_laptop']))
            self.repair_table.setItem(row, 3, QTableWidgetItem(data['nama'] or "N/A"))
            self.repair_table.setItem(row, 4, QTableWidgetItem(data['status']))
            self.repair_table.setItem(row, 5, QTableWidgetItem(data['waktu']))
        conn.close()

    def _populate_transaction_table(self):
        self.transaction_table.setRowCount(0)
        conn = database.get_db_connection()
        query = "SELECT id, id_perbaikan, total_biaya, total_uang_dibayar, kembalian, waktu FROM transaksi ORDER BY id DESC"
        for row, data in enumerate(conn.execute(query).fetchall()):
            self.transaction_table.insertRow(row)
            self.transaction_table.setItem(row, 0, QTableWidgetItem(str(data['id'])))
            self.transaction_table.setItem(row, 1, QTableWidgetItem(str(data['id_perbaikan'])))
            self.transaction_table.setItem(row, 2, QTableWidgetItem(f"Rp {data['total_biaya']:,.0f}".replace(",", ".")))
            self.transaction_table.setItem(row, 3,
                                           QTableWidgetItem(f"Rp {data['total_uang_dibayar']:,.0f}".replace(",", ".")))
            self.transaction_table.setItem(row, 4, QTableWidgetItem(f"Rp {data['kembalian']:,.0f}".replace(",", ".")))
            self.transaction_table.setItem(row, 5, QTableWidgetItem(data['waktu']))
        conn.close()

    def edit_repair_data(self, row, column):
        item_id = self.repair_table.item(row, 0).text()
        dialog = EditRepairDialog(repair_id=item_id, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_all_data()

    def edit_transaction_data(self, row, column):
        item_id = self.transaction_table.item(row, 0).text()
        dialog = EditTransactionDialog(transaction_id=item_id, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_all_data()

    def export_data_to_csv(self):
        current_index = self.data_tabs.currentIndex()
        if current_index == 0:
            table = self.repair_table
            filename = "laporan_perbaikan.csv"
        else:
            table = self.transaction_table
            filename = "laporan_transaksi.csv"
        path, _ = QFileDialog.getSaveFileName(self, "Export ke CSV", filename, "CSV Files (*.csv)")
        if path:
            try:
                with open(path, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    headers = [table.horizontalHeaderItem(i).text() for i in range(table.columnCount())]
                    writer.writerow(headers)
                    for row in range(table.rowCount()):
                        row_data = [table.item(row, col).text() for col in range(table.columnCount())]
                        writer.writerow(row_data)
                QMessageBox.information(self, "Sukses", f"Data berhasil diekspor ke {path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal mengekspor data: {e}")