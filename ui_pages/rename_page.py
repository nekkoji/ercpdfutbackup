import os
import re
import cv2
import platform
import numpy as np
import pytesseract
from PyQt5.QtWidgets import ( 
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QProgressBar, QFileDialog, QMessageBox,
    QProgressDialog, QApplication, QDialog, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QRubberBand
)
from PyQt5.QtGui import QFont, QPixmap, QImage
from PyQt5.QtCore import Qt
from PIL import Image, ImageOps, ImageFilter
from pdf2image import convert_from_path
from config.constants import FONT_SIZE, DEFAULT_FONT, SECONDARY_COLOR
from core.logger import log_action
from ui_pages.rename_option_dialog import RenameOptionDialog
from utils.image_utils import preprocess_image, pil_image_to_qimage
from ui_pages.saro_fallback_dialog import SaroFallbackDialog


def create_styled_button(text):
    button = QPushButton(text)
    button.setFixedWidth(250)
    button.setStyleSheet("""
        QPushButton {
            background-color: #6c63ff;
            color: white;
            padding: 10px 20px;
            border-radius: 12px;
            font-size: 14px;
            font-family: 'Segoe UI';
            font-weight: 500;
            border: none;
        }
        QPushButton:hover {
            background-color: #574fd6;
        }
        QPushButton:pressed {
            background-color: #4c45c4;
        }
    """)
    return button

def extract_nca_number(image):
    try:
        text = pytesseract.image_to_string(image, config="--psm 6")
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        for i, line in enumerate(lines):
            if "2067" in line:
                if i > 0:
                    potential_nca = lines[i - 1]

                    # Priority: 7-digit NCA format
                    match = re.search(r"(NCA-[A-Z]{2,5}-[A-Z]-\d{2,4}-\d{7})", potential_nca)
                    if match:
                        return match.group(1).strip()

                    # Fallback: 6-digit variant
                    match = re.search(r"(NCA-[A-Z]{2,5}-[A-Z]-\d{2,4}-\d{6})", potential_nca)
                    if match:
                        return match.group(1).strip()

                    # Fallback: plain numeric code like '345247-0'
                    match = re.search(r"(\d{5,7}[-–]\d{1,3})", potential_nca)
                    if match:
                        return match.group(1).strip()

        return None
    except Exception as e:
        print(f"Error during OCR: {e}")
        return None
    
def extract_saro_number_from_image(image: Image.Image) -> str:
    # Convert image to grayscale for better OCR accuracy
    gray = image.convert("L")

    # Crop bottom-right corner (where SARO No. usually appears)
    width, height = gray.size
    cropped = gray.crop((int(width * 0.5), int(height * 0.75), width, height))

    # Run OCR on cropped section
    text = pytesseract.image_to_string(cropped)

    # Regex patterns for SARO No.
    patterns = [
        r"(SARO[-\s]?[A-Z]{3}[-\s]?[A-Z]?[-\s]?\d{2}[-\s]?\d{7})",  # e.g. SARO-BMB-A-08-0016104
        r"\b([A-Z]{1}-\d{2}-\d{5})\b"  # e.g. A-01-05818
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).replace(" ", "").strip()

    print("OCR text (no match):", text)
    return None


class RenamePage(QWidget):
    def __init__(self, switch_page_callback, username="Unknown"):
        super().__init__()
        self.switch_page = switch_page_callback
        self.username = username
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)

        button_row = QHBoxLayout()
        button_row.setSpacing(20)

        rename_btn = create_styled_button("Start Renaming")
        rename_btn.clicked.connect(self.extract_and_rename_dialog)
        button_row.addWidget(rename_btn)

        back_btn = create_styled_button("Back")
        back_btn.clicked.connect(lambda: self.switch_page("main"))
        button_row.addWidget(back_btn)

        layout.addLayout(button_row, stretch=0)
        layout.setAlignment(button_row, Qt.AlignCenter)
        layout.addStretch()
        self.setLayout(layout)

    def extract_and_rename_dialog(self):
        dialog = RenameOptionDialog(self)
        choice = dialog.exec_()
        if choice == 1:
            self.rename_obr_files()
            log_action(self.username, "Renamed PDFs", ["Mode: OBR"])
        elif choice == 2:
            self.rename_nca_files()
            log_action(self.username, "Renamed PDFs", ["Mode: NCA"])
        elif choice == 3:
            self.rename_saro_files()
            log_action(self.username, "Renamed PDFs", ["Mode: SARO"])

    def rename_obr_files(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder with OBR PDFs")
        if not folder:
            return

        pdf_files = [f for f in os.listdir(folder) if f.lower().endswith(".pdf")]
        if not pdf_files:
            QMessageBox.information(self, "No PDFs", "No PDF files found in the folder.")
            return

        progress = QProgressDialog("Renaming OBR files...", "Cancel", 0, len(pdf_files), self)
        progress.setWindowTitle("Renaming OBR Files")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)

        renamed, skipped, summary = 0, [], []

        for i, file in enumerate(pdf_files):
            progress.setValue(i)
            progress.setLabelText(f"Processing {file} ({i+1}/{len(pdf_files)})")
            QApplication.processEvents()

            if progress.wasCanceled():
                break

            path = os.path.join(folder, file)
            try:
                image = convert_from_path(path, first_page=1, last_page=1)[0]
                text = pytesseract.image_to_string(image)

                match = re.search(r"(CA\-MOOE\S+|MOOE\S+|PGF\S+|PS\S+)", text)
                if match:
                    serial = match.group(1).strip()
                    new_name = f"{serial}.pdf"
                    new_path = os.path.join(folder, new_name)
                    if not os.path.exists(new_path):
                        os.rename(path, new_path)
                        renamed += 1
                        summary.append(f"{file} ➔ {new_name}")
                    else:
                        skipped.append(f"{file} (already exists as {new_name})")
                    continue

                # Fallback: prepare preview and suggestions
                full_qimage = pil_image_to_qimage(image)
                width, height = full_qimage.width(), full_qimage.height()
                crop = full_qimage.copy(width // 2, 0, width // 2, height // 2)

                guesses = []  # no guesses if match not found
                from ui_pages.obr_fallback_dialog import ObrFallbackDialog
                fallback_dialog = ObrFallbackDialog(guesses, crop, path, self)

                if fallback_dialog.exec_() == fallback_dialog.Accepted:
                    fallback_text = fallback_dialog.get_selected_text()
                    if fallback_text:
                        new_name = f"{fallback_text}.pdf"
                        new_path = os.path.join(folder, new_name)
                        if not os.path.exists(new_path):
                            os.rename(path, new_path)
                            renamed += 1
                            summary.append(f"{file} ➔ {new_name}")
                        else:
                            skipped.append(f"{file} (already exists as {new_name})")
                    else:
                        skipped.append(f"{file} (manual input blank)")
                else:
                    skipped.append(f"{file} (manual cancel)")

            except Exception as e:
                print(f"Error processing {file}: {e}")
                skipped.append(f"{file} (error)")

        progress.close()

        message = f"✅ Renamed {renamed} OBR files."
        if skipped:
            message += "\n\n⚠ Skipped Files:\n" + "\n".join(skipped[:10])
            if len(skipped) > 10:
                message += "\n..."

        QMessageBox.information(self, "Renaming Complete", message)

        if skipped:
            self.show_skipped_files_preview(skipped)

    def rename_saro_files(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder with SARO PDFs")
        if not folder:
            return

        pdf_files = [f for f in os.listdir(folder) if f.lower().endswith(".pdf")]
        if not pdf_files:
            QMessageBox.information(self, "No PDFs", "No PDF files found in the folder.")
            return

        progress = QProgressDialog("Renaming files...", "Cancel", 0, len(pdf_files), self)
        progress.setWindowTitle("Renaming SARO Files")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)

        renamed, skipped, summary = 0, [], []

        for i, file in enumerate(pdf_files):
            progress.setValue(i)
            progress.setLabelText(f"Processing {file} ({i+1}/{len(pdf_files)})")
            QApplication.processEvents()

            if progress.wasCanceled():
                break

            path = os.path.join(folder, file)
            try:
                image = convert_from_path(path, first_page=1, last_page=1)[0]
                text = pytesseract.image_to_string(image)

                auto_guess = None
                match = re.search(r"SARO\s*No\.?.?[:\-~]?\s*([A-Z0-9\-~]+)", text, re.IGNORECASE)
                if match:
                    auto_guess = match.group(1).replace("~", "-").replace("–", "-").strip()
                    if not auto_guess.upper().startswith(("SARO-", "A-")):
                        auto_guess = "A-" + auto_guess

                lines = text.splitlines()
                guesses = []
                if auto_guess:
                    guesses.append(auto_guess)

                for line in lines:
                    cleaned = line.strip().replace("~", "-").replace("–", "-")
                    if re.match(r"^(SARO-[A-Z]{3}-[A-Z]?-?\d{2}-\d{7}|[A-Z]{1,4}-\d{2}-\d{5,7})$", cleaned):
                        if cleaned not in guesses:
                            guesses.append(cleaned)

                guesses = list(dict.fromkeys(guesses))[:3]

                full_qimage = pil_image_to_qimage(image)

                fallback_dialog = SaroFallbackDialog(guesses, full_qimage, path, self)
                if fallback_dialog.exec_() == fallback_dialog.Accepted:
                    fallback_name = fallback_dialog.get_selected_text()
                    if fallback_name:
                        if not fallback_name.upper().startswith(("SARO-", "A-")):
                            fallback_name = "A-" + fallback_name
                        new_name = f"{fallback_name}.pdf"
                        new_path = os.path.join(folder, new_name)
                        if not os.path.exists(new_path):
                            os.rename(path, new_path)
                            renamed += 1
                            summary.append(f"{file} ➔ {new_name}")
                        else:
                            skipped.append(f"{file} (already exists as {new_name})")
                    else:
                        skipped.append(f"{file} (manual input blank)")
                else:
                    skipped.append(f"{file} (manual cancel)")

            except Exception as e:
                print(f"Error processing {file}: {e}")
                skipped.append(f"{file} (error)")

        progress.close()

        message = f"✅ Renamed {renamed} SARO files."
        if skipped:
            message += "\n\n⚠ Skipped Files:\n" + "\n".join(skipped[:10])
            if len(skipped) > 10:
                message += "\n..."

        QMessageBox.information(self, "Renaming Complete", message)

        if skipped:
            self.show_skipped_files_preview(skipped)

    def show_skipped_files_preview(self, skipped_files):
        dialog = QDialog(self)
        dialog.setWindowTitle("Skipped Files Preview")
        dialog.setMinimumSize(500, 400)

        layout = QVBoxLayout()
        text_area = QTextEdit()
        text_area.setReadOnly(True)
        text_area.setText("\n".join(skipped_files))

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)

        layout.addWidget(text_area)
        layout.addWidget(close_btn, alignment=Qt.AlignRight)
        dialog.setLayout(layout)

        dialog.exec_()
