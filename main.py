import sys
import os
import json
import time
from PyQt5.QtWidgets import QApplication, QMessageBox
from ui_pages.main_window import PDFUtilityTool
from ui_pages.login_page import LoginPage

def main():
    app = QApplication(sys.argv)
    window = PDFUtilityTool()

    try:
        with open("remember_me.json", "r") as f:
            saved = json.load(f)
            if "username" in saved and "timestamp" in saved:
                if time.time() - saved["timestamp"] < 30 * 24 * 60 * 60:  # 30 days
                    window.on_login_success(saved["username"])

                    QMessageBox.information(
                        window,
                        "Welcome Back 👋",
                        f"Welcome back, {saved['username']}!"
)
                else:
                    os.remove("remember_me.json")
                    window.setCentralWidget(LoginPage(window.on_login_success))
            else:
                window.setCentralWidget(LoginPage(window.on_login_success))
    except Exception:
        window.setCentralWidget(LoginPage(window.on_login_success))

    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
