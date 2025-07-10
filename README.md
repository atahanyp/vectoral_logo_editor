# 🎨 Vectoral Logo Editor

PDF logo düzenleme ve yerleştirme uygulaması / PDF logo editing and placement application

Bu uygulama sayesinde vektörel formatta hazırlanmış logoları (PDF, SVG) sayfa üzerine istediğiniz boyut, konum ve düzenle yerleştirebilirsiniz. Kullanıcı dostu arayüzü sayesinde hızlıca boyutlandırabilir, hizalayabilir, döndürebilir ve çıktı olarak yeni bir PDF alabilirsiniz.

*This application allows you to place vector logos (PDF, SVG) on pages with desired size, position, and layout. With its user-friendly interface, you can quickly scale, align, rotate logos and export the result as a new PDF.*

## ✨ Özellikler / Features

- 📄 PDF/SVG logo yükleme ve önizleme / Upload and preview vector logos (PDF/SVG)
- 📐 Logo boyutlandırma ve en/boy oranı kilitleme / Scale logos and lock aspect ratio
- 🔄 Logoları döndürme (90°) / Rotate logos (90° increments)
- 📊 Sayfa üzerindeki logo sayısı ve aralıklarını ayarlama / Configure number of logos per page and spacing
- 📄 Sayfa boyutlarını manuel veya otomatik ayarlama / Manual or automatic page size adjustment
- ↔️ Sayfa kenar boşluklarını özelleştirme / Customize page margins
- 🎨 Arka plan rengi seçimi / Choose page background color
- 💾 Ayarları kaydetme ve yükleme / Save and load user settings

## ⚙️ Çalışma Mantığı / How it Works

**Türkçe:**
- Uygulama, vektörel logoları doğrudan PDF veya SVG formatında alır.
- SVG logolar, svglib kütüphanesi yardımıyla PDF'e dönüştürülür.
- PDF tabanlı logolar, PyMuPDF ile sayfa içerisine gömülür ve istenen ölçüde yerleştirilir.
- Kullanıcı arayüzü üzerinden logo boyutları, sayfa düzeni ve kenar boşlukları belirlenir.
- Arka plan, reportlab kullanılarak oluşturulur ve logolar bu arka plan üzerine yerleştirilir.
- Sonuçta vektörel yapısı korunmuş, baskıya uygun bir PDF dosyası üretilir.

**English:**
- The application directly accepts vector logos in PDF or SVG format.
- SVG logos are converted to PDF using svglib.
- PDF-based logos are embedded into the output PDF at the desired scale and position via PyMuPDF.
- Users define logo dimensions, page layout, and margins through the GUI.
- The background is generated with reportlab and the logos are placed on top.
- Finally, a print-ready PDF file is created, preserving vector quality.

## 🖥️ Kurulum / Installation

1️⃣ Gereksinimleri yükleyin / Install requirements:
```bash
pip install -r requirements.txt
```

2️⃣ Programı çalıştırın / Run the program:
```bash
python main.py
```

## 🚀 Kullanım / Usage

1. **Logo seçin / Select a logo:**
   - "Logo Dosyası Seç" butonuna tıklayın veya sürükleyip bırakın. / Click "Logo Dosyası Seç" or drag & drop.

2. **Boyut ve konum ayarlayın / Adjust size & position:**
   - Boyutları ve döndürme açılarını belirleyin. / Set dimensions and rotation.

3. **Sayfa düzenini yapılandırın / Configure page layout:**
   - Logo sayısı, boşluklar ve kenar boşluklarını girin. / Enter number of logos, spacing and margins.

4. **Önizleme oluşturun / Create preview:**
   - "Otomatik" veya "Manuel" butonlarıyla. / Use "Automatic" or "Manual" buttons.

5. **PDF'i kaydedin / Save PDF:**
   - "Farklı Kaydet" butonuyla. / Click "Farklı Kaydet".

## 📂 Yapı / Structure

- `main.py` — Ana uygulama / Main application
- `src/` — Modüller / Modules
  - `pdf_processor/` — PDF işleme / PDF processing
  - `file_manager/` — Dosya yönetimi / File management
  - `ui_components/` — Arayüz bileşenleri / UI components
- `requirements.txt` — Bağımlılıklar / Dependencies
- `kayitliayar.txt` — Kullanıcı ayarları / User settings
- `temp/` — Geçici dosyalar / Temporary files

## 📦 Bağımlılıklar / Dependencies

- **PyQt5** — Kullanıcı arayüzü / GUI
- **PyMuPDF** — PDF işleme / PDF processing
- **reportlab** — PDF oluşturma / PDF creation
- **svglib** — SVG'den PDF'e dönüşüm / SVG to PDF conversion
