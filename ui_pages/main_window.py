import sys
from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QApplication, QLabel
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtCore import Qt
from config.theme_config import load_theme, save_theme
from config.constants import DEFAULT_FONT
from ui_pages.main_menu import MainMenuPage
from ui_pages.rename_page import RenamePage
from ui_pages.split_page import SplitPage
from ui_pages.sharepoint_page import SharepointPage
from ui_pages.obr_page import OBRPage
from ui_pages.login_page import LoginPage
from ui_pages.activity_log_page import ActivityLogPage
from core.logger import log_action
from ui_pages.merge_page import MergePDFPage

class PDFUtilityTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ERC PDF Utility Tool")
        self.setWindowIcon(QIcon("njz.png"))
        self.setGeometry(100, 100, 1200, 800)
        self.logged_in_user = None

        self.login_page = LoginPage(self.on_login_success)
        self.setCentralWidget(self.login_page)

        self.apply_theme(load_theme())

    def on_login_success(self, username):
        self.logged_in_user = username
        log_action(username, "✅ Logged In")
        self.setup_main_app()

    def setup_main_app(self):
        self.stack = QStackedWidget()
        self.pages = {}

        self.pages["activity"] = ActivityLogPage(self.logged_in_user, parent=self)
        self.stack.addWidget(self.pages["activity"])

        self.pages["merge"] = MergePDFPage(self.switch_page)
        self.stack.addWidget(self.pages["merge"])

        self.theme_toggle = QPushButton()
        self.theme_toggle.setCheckable(True)
        self.theme_toggle.setObjectName("ThemeToggle")
        self.theme_toggle.setIcon(QIcon("moon.png") if load_theme() else QIcon("sun.png"))
        self.theme_toggle.setToolTip("Toggle Dark Mode")
        self.theme_toggle.setChecked(load_theme())
        self.theme_toggle.clicked.connect(self.handle_theme_toggle)

        self.user_label = QLabel(f"Logged in as: {self.logged_in_user}")
        self.logout_btn = QPushButton("Log Out")
        self.logout_btn.setToolTip("Log out and return to login page")
        self.logout_btn.setStyleSheet("""
            QPushButton {
                color: #fff;
                background-color: #e53935;
                border-radius: 6px;
                padding: 4px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.logout_btn.clicked.connect(self.logout)

        self.user_label.setStyleSheet("color: gray; padding-right: 15px;")

        header_layout = QHBoxLayout()
        header_layout.addWidget(self.user_label)
        header_layout.addStretch()
        header_layout.addWidget(self.theme_toggle)
        #header_layout.addStretch()
        #header_layout.addWidget(self.logout_btn)

        main_layout = QVBoxLayout()
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.stack)

        main_layout.addStretch()
        self.logout_btn = QPushButton("Log Out")
        self.logout_btn.setToolTip("Log out and return to login screen")
        self.logout_btn.setFixedWidth(100)
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #e53935;
                color: white;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.logout_btn.clicked.connect(self.logout)
        main_layout.addWidget(self.logout_btn, alignment=Qt.AlignHCenter)

        wrapper = QWidget()
        wrapper.setLayout(main_layout)
        self.setCentralWidget(wrapper)

        self.pages["main"] = MainMenuPage(self.switch_page)
        self.pages["rename"] = RenamePage(self.switch_page)
        self.pages["split"] = SplitPage(self.switch_page)
        self.pages["sharepoint"] = SharepointPage(self.switch_page)
        self.pages["obr"] = OBRPage(self.switch_page, self.apply_theme, self.logged_in_user)

        for page in self.pages.values():
            self.stack.addWidget(page)

        self.switch_page("main")

    def switch_page(self, page_name):
        if page_name in self.pages:
            self.stack.setCurrentWidget(self.pages[page_name])

    def set_page(self, name):
        if name in self.pages:
            self.stack.setCurrentWidget(self.pages[name])

    def handle_theme_toggle(self):
        is_dark = self.theme_toggle.isChecked()
        self.apply_theme(is_dark)
        icon_path = "moon.png" if is_dark else "sun.png"
        self.theme_toggle.setIcon(QIcon(icon_path))

    def logout(self):
        self.logged_in_user = None
        log_action(self.logged_in_user, "🚪 Logged Out")
        self.stack = None
        self.pages = {}

        # Go back to login screen
        self.login_page = LoginPage(self.on_login_success)
        self.setCentralWidget(self.login_page)

    def go_back(self):
        if self.main_window:
            self.main_window.set_page("home") 

    def apply_theme(self, dark_mode):
        save_theme(dark_mode)
        app = QApplication.instance()

        if dark_mode:
            dark_palette = QPalette()
            dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.WindowText, QColor("white"))
            dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
            dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ToolTipBase, QColor("white"))
            dark_palette.setColor(QPalette.ToolTipText, QColor("white"))
            dark_palette.setColor(QPalette.Text, QColor("white"))
            dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ButtonText, QColor("white"))
            dark_palette.setColor(QPalette.BrightText, QColor("red"))
            dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.HighlightedText, QColor("black"))
            app.setPalette(dark_palette)

            app.setStyleSheet("""
                QWidget {
                    background-color: #2f3136;
                    color: #dcddde;
                    font-size: 14px;
                }
                QLineEdit, QTableWidget, QTextEdit {
                    background-color: #202225;
                    border: 1px solid #444;
                    color: #dcddde;
                }
                QHeaderView::section {
                    background-color: #2f3136;
                    color: #dcddde;
                    padding: 4px;
                    border: 1px solid #444;
                }
                QTableWidget::item:selected {
                    background-color: #3a3c40;
                }
                QPushButton {
                    background-color: #40444b;
                    color: #dcddde;
                    border: 1px solid #444;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #4f545c;
                }
                QPushButton#ThemeToggle {
                    font-size: 12px;
                    padding: 2px;
                }
                QMenu {
                    background-color: #2f3136;
                    color: #dcddde;
                }
                QScrollBar:vertical {
                    background: #2f3136;
                    width: 12px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background: #72767d;
                    min-height: 20px;
                    border-radius: 6px;
                }
                QScrollBar::add-line:vertical,
                QScrollBar::sub-line:vertical {
                    background: none;
                }
            """)
        else:
            app.setPalette(app.style().standardPalette())
            app.setStyleSheet("")
