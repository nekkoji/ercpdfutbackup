import os
import csv
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QFileDialog, QMessageBox, QSizePolicy, QHeaderView
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from core.logger import log_action


class ActivityLogPage(QWidget):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username
        self.main_window = parent
        self.setStyleSheet("font-family: 'Segoe UI'; font-size: 13px;")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 🔙 Back button
        back_btn = QPushButton("⬅ Back")
        back_btn.setFont(QFont("Segoe UI", 11))
        back_btn.setFixedWidth(120)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #cccccc;
                color: #333;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #bbbbbb;
            }
        """)
        back_btn.clicked.connect(lambda: self.switch_page("main"))
        layout.addWidget(back_btn, alignment=Qt.AlignLeft)

        # 📊 Title
        title = QLabel("📊 Activity Log")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # 📋 Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Timestamp", "Username", "Action", "File(s)"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setMinimumHeight(500)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        layout.addStretch()

        # 🔘 Buttons
        self.refresh_btn = QPushButton("🔄 Refresh Logs")
        self.refresh_btn.clicked.connect(self.load_logs)
        layout.addWidget(self.refresh_btn)

        self.export_btn = QPushButton("📤 Export to CSV")
        self.export_btn.clicked.connect(self.export_logs)
        layout.addWidget(self.export_btn)

        self.setLayout(layout)
        self.load_logs()

    def switch_page(self, page_name):
        if self.main_window:
            self.main_window.set_page(page_name)

    def load_logs(self):
        self.table.setRowCount(0)

        log_file = f"activity_log_{self.username}.csv"
        if not os.path.exists(log_file):
            return

        with open(log_file, newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 4:
                    continue
                row_pos = self.table.rowCount()
                self.table.insertRow(row_pos)
                for col, item in enumerate(row):
                    table_item = QTableWidgetItem(item)

                    # 🎨 Color-code based on action
                    action = row[2].lower()
                    if "login" in action:
                        table_item.setForeground(Qt.green)
                    elif "logout" in action:
                        table_item.setForeground(Qt.red)
                    elif "extract" in action:
                        table_item.setForeground(Qt.blue)
                    elif "export" in action:
                        table_item.setForeground(Qt.darkMagenta)
                    else:
                        table_item.setForeground(Qt.darkGray)

                    self.table.setItem(row_pos, col, table_item)

    def export_logs(self):
        log_file = f"activity_log_{self.username}.csv"
        if not os.path.exists(log_file):
            QMessageBox.information(self, "No Logs", "No activity logs to export.")
            return

        dest, _ = QFileDialog.getSaveFileName(self, "Export Logs", "", "CSV Files (*.csv)")
        if dest:
            with open(log_file, "r") as f_in, open(dest, "w", newline="") as f_out:
                f_out.write(f_in.read())
            QMessageBox.information(self, "Success", "Logs exported successfully.")
