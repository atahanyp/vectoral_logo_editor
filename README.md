# PDF Logo Editor

PDF logo düzenleme ve yerleştirme uygulaması. Bu uygulama sayesinde vektörel logolar sayfa üzerine istenilen boyut ve konumda yerleştirilebilir.

*PDF logo editing and placement application. This application allows you to place vector logos on pages with desired size and position.*

## Özellikler / Features

- PDF logoları yükleme ve önizleme / Upload and preview PDF logos
- Logo boyutlarını ayarlama / Adjust logo dimensions
- En/boy oranını kilitleme / Lock aspect ratio
- Logoları döndürme (90°) / Rotate logos (90°)
- Sayfadaki logo sayısını ve aralarındaki boşluğu ayarlama / Adjust number of logos on page and spacing between them
- Sayfa boyutlarını manuel veya otomatik ayarlama / Manual or automatic page size adjustment
- Sayfa kenar boşluklarını özelleştirme / Customize page margins
- Arka plan rengi seçimi / Select background color
- Ayarları kaydetme ve yükleme / Save and load settings

## Kurulum / Installation

1. Gereksinimleri yükleyin / Install requirements:
   ```
   pip install -r requirements.txt
   ```

2. Programı çalıştırın / Run the program:
   ```
   python main.py
   ```

## Kullanım / Usage

1. "Logo Dosyası Seç" butonuna tıklayarak veya sürükle-bırak yaparak bir PDF logo seçin / Select a PDF logo by clicking the "Logo Dosyası Seç" button or by drag and drop
2. Logo boyutlarını ayarlayın (gerekiyorsa döndürün) / Adjust logo dimensions (rotate if necessary)
3. Sayfa ayarlarını düzenleyin / Edit page settings
4. "Sayfa Boyunu Otomatik Hesaplayarak Oluştur" veya "Sayfa Boyunu Manuel Ayarlayarak Oluştur" butonları ile önizleme oluşturun / Create a preview with "Sayfa Boyunu Otomatik Hesaplayarak Oluştur" or "Sayfa Boyunu Manuel Ayarlayarak Oluştur" buttons
5. "Farklı Kaydet" butonu ile PDF'i kaydedin / Save the PDF with "Farklı Kaydet" button

## Yapı / Structure

Proje modüler bir yapıda düzenlenmiştir. Ana uygulama mantığı main.py'de, yardımcı modüller ise src/ dizini altındadır.

*The project is organized in a modular structure. The main application logic is in main.py, while helper modules are under the src/ directory.*

- `main.py` - Ana uygulama kodu / Main application code
- `src/` - Kaynak kod dizini / Source code directory
  - `pdf_processor/` - PDF işleme işlevleri / PDF processing functions
  - `file_manager/` - Dosya işleme işlevleri / File handling functions
  - `ui_components/` - Kullanıcı arayüzü bileşenleri / UI components
- `requirements.txt` - Gerekli bağımlılıklar / Required dependencies
- `kayitliayar.txt` - Kaydedilen ayarlar / Saved settings
- `temp/` - Geçici dosyalar / Temporary files

## Bağımlılıklar / Dependencies

- PyQt5: Kullanıcı arayüzü için / For the user interface
- PyMuPDF: PDF işleme için / For PDF processing
- reportlab: PDF oluşturma için / For PDF creation
- svglib: SVG işleme için / For SVG processing
