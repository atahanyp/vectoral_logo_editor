# Vectoral Logo Editor

PDF logo editing and placement application

This application allows you to place vector logos (PDF, SVG) on pages with desired size, position, and layout. With its user-friendly interface, you can quickly scale, align, rotate logos and export the result as a new PDF.

## Features

- Upload and preview vector logos (PDF/SVG)
- Scale logos and lock aspect ratio
- Rotate logos (90° increments)
- Configure number of logos per page and spacing
- Manual or automatic page size adjustment
- Customize page margins
- Choose page background color
- Save and load user settings

## How it Works

- The application directly accepts vector logos in PDF or SVG format.
- SVG logos are converted to PDF using svglib.
- PDF-based logos are embedded into the output PDF at the desired scale and position via PyMuPDF.
- Users define logo dimensions, page layout, and margins through the GUI.
- The background is generated with reportlab and the logos are placed on top.
- Finally, a print-ready PDF file is created, preserving vector quality.

## Installation

1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Run the program:
```bash
python main.py
```

## Usage

1. **Select a logo:**
   - Click "Logo Dosyası Seç" button or use drag & drop.

2. **Adjust size & position:**
   - Set dimensions and rotation.

3. **Configure page layout:**
   - Enter number of logos, spacing and margins.

4. **Create preview:**
   - Use "Automatic" or "Manual" buttons.

5. **Save PDF:**
   - Click "Farklı Kaydet" button.

## Structure

- `main.py` — Main application
- `src/` — Modules
  - `pdf_processor/` — PDF processing
  - `file_manager/` — File management
  - `ui_components/` — UI components
- `requirements.txt` — Dependencies
- `kayitliayar.txt` — User settings
- `temp/` — Temporary files

## Dependencies

- **PyQt5** — GUI
- **PyMuPDF** — PDF processing
- **reportlab** — PDF creation
- **svglib** — SVG to PDF conversion
