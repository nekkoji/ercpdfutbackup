# ERC PDF Utility Tool

A multifunctional PyQt5-based desktop application to streamline and automate PDF-related document processing tasks for the Energy Regulatory Commission.

---

## 🚀 Features

### 📂 File Management
- **Extract & Rename of OBR, NCA, and SARO PDFs** based on content (e.g., Serial No., NCA No., SARO No.)
- **Split PDFs** into individual pages
- **Manage PDFs**: Open, rename, delete, and move files

### 🧾 OBR Extractor
- OCR-based data extraction from PDF forms
- Intelligent parsing of Payee, Date, Particulars, Amount
- Table editing with:
  - Cell-level editing
  - Undo/Redo
  - Copy/Paste
  - Inline audit logs
- Manual OCR region scan per cell (crop & extract)
- Save to CSV, Excel, and PDF
- Smart summary row calculation

### 🏢 SharePoint Integration
- Authenticate to a SharePoint site
- Extract PDF links from folders
- Export result as a hyperlinked Excel file

### 🎨 Theme Support
- 🌗 Dark/Light mode toggle
- Theme preference is saved between sessions

---

## 📁 Project Structure
```
erc_app/
│
├── main.py
├── theme_config.json
├── budget.xlsx
├── icon.png
├── sun.png
├── moon.png
├── README.md
├── obr_extractor.py
│
├── core/
│   ├── file_utils.py
│   ├── pdf_utils.py
│   ├── budget_utils.py
│   └── sharepoint_utils.py
│
├── config/
│   ├── constants.py
│   └── theme_config.py
│
├── ui_pages/
    ├── main_window.py
    ├── main_menu.py
    ├── rename_page.py
    ├── obr_page.py
    ├── split_page.py
    ├── sharepoint_page.py

```x`

---

## 🤝 Developers:
- Engr. Rolando Celeste - celeste.landon667@gmail.com
- Engr. Cris John Perez - perezcj2003@gmail.com

