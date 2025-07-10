"""
Ana PDF Editor uygulaması - Modüler Yapı
"""

import os
import sys
import traceback
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog,
    QWidget, QFormLayout, QScrollArea, QGroupBox, QColorDialog
)
from PyQt5.QtGui import QPixmap, QImage, QTransform, QPainter
from PyQt5.QtCore import Qt
import fitz

# Import our modules
from src.ui_components.custom_widgets import CustomLineEdit
from src.pdf_processor.pdf_processor import PDFProcessor
from src.file_manager.file_manager import FileManager

CM_TO_PT = 72/2.54


class PDFEditorApp(QWidget):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Logo Editor")
        self.setGeometry(100, 100, 1200, 800)
        self.setAcceptDrops(True)  # Ana pencereye sürükle-bırak özelliği ekle

        # Bileşenleri başlat
        self.pdf_processor = PDFProcessor()
        self.file_manager = FileManager()
        
        # Yeni özellikler için değişkenler
        self.aspect_ratio_locked = True  # Başlangıçta ölçek kilitli
        self.logo_aspect_ratio = None    # Logo en/boy oranı (yüklenince hesaplanacak)
        self.fixed_aspect_ratio = None   # Sabit ölçek oranı
        self.pdf_path = None
        self.logo_path = None
        self.bg_color = "#ffffff"   #"#B9E7BA"
        self.pdf_processor.bg_color = self.bg_color  # PDFProcessor'a rengi aktar
        self.rotation_angle = 0  # Döndürme açısını takip etmek için
        self.heighta = 0
        self.inputlogowidth = 0
        self.inputlogoheight = 0
        
        # Zoom faktörü ve sınırları
        self.zoom_factor = 1.0  # Başlangıç değeri 1.0'a düşürüldü
        self.zoom_min = 0.5     # Minimum zoom 0.5'e düşürüldü
        self.zoom_max = 16.0    # Maximum zoom 16.0

        self.init_ui()

    def init_ui(self):
        """Arayüzü oluşturma"""
        
        main_layout = QHBoxLayout()

        # Sol Panel: Kontroller
        self.control_panel = QVBoxLayout()

        # 📌 Sayfa Ayarları Bölümü
        self.page_settings_group = QGroupBox("Sayfa Ayarları")
        page_settings_layout = QFormLayout()

        self.page_width_input = CustomLineEdit(self)  # QLineEdit yerine CustomLineEdit
        self.page_height_input = CustomLineEdit(self)
        self.page_left_margin_input = CustomLineEdit(self)
        self.page_right_margin_input = CustomLineEdit(self)
        self.page_top_margin_input = CustomLineEdit(self)

        try:
            # Önceki ayarları yükle
            settings = self.file_manager.useprevset()
            if len(settings) >= 5:
                self.page_width_input.setText(settings[0])
                self.page_height_input.setText(settings[1])
                self.page_left_margin_input.setText(settings[2])
                self.page_right_margin_input.setText(settings[3])
                self.page_top_margin_input.setText(settings[4])
            else:
                raise ValueError("Yeterli veri bulunamadı.")
        except Exception as e:  # Herhangi bir hata oluşursa
            self.page_width_input.setText("58")  # Varsayılan değer
            self.page_height_input.setText(" ")   # Boş bırakıldı
            self.page_left_margin_input.setText("0.1")
            self.page_right_margin_input.setText("0.1")
            self.page_top_margin_input.setText("0.1")

        page_settings_layout.addRow("Sayfa Genişliği (cm):", self.page_width_input)
        page_settings_layout.addRow("Sayfa Yüksekliği (cm):", self.page_height_input)
        page_settings_layout.addRow("Soldan Yatay Boşluk (cm):", self.page_left_margin_input)
        page_settings_layout.addRow("Sağdan Yatay Boşluk (cm):", self.page_right_margin_input)
        page_settings_layout.addRow("Üstten Dikey Boşluk (cm):", self.page_top_margin_input)

        # 📌 Sayfa Boyunu Otomatik Hesaplama Butonu
        self.setkayt_button = QPushButton("Sayfa Ayarlarını Kaydet")  # Yeni buton
        self.setkayt_button.clicked.connect(self.setkaydet)
        self.color_button = QPushButton("Arka Plan Rengini Seç")
        self.color_button.clicked.connect(self.select_color)
        self.color_button.setStyleSheet(f"background-color: {self.bg_color}; padding: 5px;")

        button_row_layout = QHBoxLayout()
        button_row_layout.addWidget(self.setkayt_button)  # Sol tarafta yeni buton
        button_row_layout.addWidget(self.color_button)  # Sağ tarafta mevcut buton

        # Bu düzeni page_settings_layout'a ekleyin
        page_settings_layout.addRow(button_row_layout)
        
        self.page_settings_group.setLayout(page_settings_layout)

        # 📌 Logo Ayarları Bölümü
        self.logo_settings_group = QGroupBox("Logo Ayarları")
        logo_settings_layout = QVBoxLayout()
        logo_form_layout = QFormLayout()

        self.total_logo_input = CustomLineEdit(self)
        self.spacing_input = CustomLineEdit(self)
        self.spacingy_input = CustomLineEdit(self)
        self.logo_width_input = CustomLineEdit(self)
        self.logo_height_input = CustomLineEdit(self)

        # 📌 Varsayılan Değerler
        self.total_logo_input.setText("10")
        self.spacing_input.setText("1")
        self.spacingy_input.setText("1")
        self.logo_width_input.setText("10")
        self.logo_height_input.setText("10")

        # 📌 Ölçek Kilidi Butonu
        self.lock_scale_button = QPushButton("Ölçek Kilidi: Açık 🔒")
        self.lock_scale_button.setCheckable(True)
        self.lock_scale_button.setChecked(True)  # Başlangıçta kilitli
        self.lock_scale_button.clicked.connect(self.toggle_aspect_ratio_lock)
        
        # 📌 Döndürme Butonu Ekleme
        self.rotate_button = QPushButton("Logoyu 90° Döndür")
        self.rotate_button.clicked.connect(self.rotate_logo)

        # 📌 Kullanıcı girişlerini Enter veya focus kaybında güncelle
        self.logo_width_input.returnPressed.connect(lambda: self.update_logo_dimensions(self.logo_width_input))
        self.logo_height_input.returnPressed.connect(lambda: self.update_logo_dimensions(self.logo_height_input))

        logo_form_layout.addRow("Toplam Logo Sayısı:", self.total_logo_input)
        logo_form_layout.addRow("Logolar Arası Yatay Boşluk (cm):", self.spacing_input)
        logo_form_layout.addRow("Logolar Arası Dikey Boşluk (cm):", self.spacingy_input)
        logo_form_layout.addRow("Logonun Genişliği (cm):", self.logo_width_input)
        logo_form_layout.addRow("Logonun Yüksekliği (cm):", self.logo_height_input)
        logo_form_layout.addRow("", self.lock_scale_button)
        logo_form_layout.addRow("", self.rotate_button)  # Döndürme butonu eklendi

        # 📌 Logo Seçimi
        self.logo_file_button = QPushButton("Logo Dosyası Seç")
        self.logo_file_button.clicked.connect(self.select_pdf)
        self.logo_preview_label = QLabel("Seçilen Logo Önizlemesi")
        self.logo_preview_label.setStyleSheet("border: 1px solid black;")
        self.logo_preview_label.setFixedSize(100, 100)  # Küçük kare boyut
        self.logo_preview_label.setAcceptDrops(True)  # Sürükle-bırak özelliği ekle
        self.logo_preview_label.dragEnterEvent = self.dragEnterEvent
        self.logo_preview_label.dropEvent = self.dropEvent
        self.save_as_button = QPushButton("Farklı Kaydet")
        self.save_as_button.clicked.connect(self.save_as_pdf)  # ✅ Yeni fonksiyona bağla   

        logo_file_layout = QVBoxLayout()
        logo_file_layout.addWidget(self.logo_file_button)
        logo_file_layout.addWidget(self.logo_preview_label)
        

        # 📌 Logo Ayarlarını Düzenle
        logo_settings_layout.addLayout(logo_form_layout)
        logo_settings_layout.addLayout(logo_file_layout)
        self.logo_settings_group.setLayout(logo_settings_layout)

        # 📌 Değişiklikleri Uygula Butonu
        self.auto_height_button = QPushButton("Sayfa Boyunu Otomatik Hesaplayarak Oluştur")
        self.auto_height_button.clicked.connect(self.calculate_page_height)

        self.man_height_button = QPushButton("Sayfa Boyunu Manuel Ayarlayarak Oluştur")
        self.man_height_button.clicked.connect(self.apply_changes)
        
        # 📌 Sol Panel Elemanları
        self.control_panel.addWidget(self.page_settings_group)
        self.control_panel.addWidget(self.logo_settings_group)
        self.control_panel.addWidget(self.auto_height_button)
        self.control_panel.addWidget(self.man_height_button)
        self.control_panel.addWidget(self.save_as_button)

        # 📌 Sağ Panel: PDF Önizleme - main6.py'deki gibi
        self.pdf_preview_scroll = QScrollArea()
        self.pdf_preview_label = QLabel("PDF önizlemesi burada görünecek.")
        self.pdf_preview_label.setStyleSheet("border: 1px solid black;")
        self.pdf_preview_label.setScaledContents(False)  # Oranı koruyacağız
        self.pdf_preview_scroll.setWidget(self.pdf_preview_label)
        self.pdf_preview_scroll.setWidgetResizable(True)

        # 📌 Ana Düzeni Yerleştir
        main_layout.addLayout(self.control_panel, 1)  # Kontrol paneline 1 birim alan
        main_layout.addWidget(self.pdf_preview_scroll, 3)  # PDF önizlemesine 3 birim alan

        self.setLayout(main_layout)

    def setkaydet(self):
        """Ayarları kaydet"""
        settings = [
            self.page_width_input.text(),
            self.page_height_input.text(),
            self.page_left_margin_input.text(),
            self.page_right_margin_input.text(),
            self.page_top_margin_input.text()
        ]
        self.file_manager.setkaydet(settings)

    def select_color(self):
        """Renk seçici aç"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.bg_color = color.name()  # Hexadecimal formatta rengi alır
            self.pdf_processor.bg_color = self.bg_color  # PDFProcessor'da bg_color'ı güncelle
            self.color_button.setStyleSheet(f"background-color: {self.bg_color}; padding: 5px;")
            print(f"Seçilen Renk: {self.bg_color}")

            if not self.pdf_path:
                return
                
            current_dir = os.getcwd()
            output2_path = os.path.join(current_dir, "output2_preview.pdf")
            self.pdf_processor.add_transparent_logos(
                pdf_path=self.pdf_path,
                output_path=output2_path,
                logo_width_cm=float(self.logo_width_input.text()),
                logo_height_cm=float(self.logo_height_input.text()),
                spacing_cm=float(self.spacing_input.text()),
                spacingy_cm=float(self.spacingy_input.text()),
                page_width_cm=float(self.page_width_input.text()),
                page_height_cm=float(self.page_height_input.text()),
                pagexcm=float(self.page_left_margin_input.text()),
                pagexrcm=float(self.page_right_margin_input.text()),
                pageycm=float(self.page_top_margin_input.text()),
                total_logo=int(self.total_logo_input.text()),
                arkaplan=True,
                bg_color=self.bg_color
            )
            self.load_pdf_preview(output2_path)

    def save_as_pdf(self):
        """PDF olarak kaydet"""
        if not self.pdf_path:
            self.logo_preview_label.setText("Önce bir PDF dosyası seçin!")
            return
        
        # 📂 Kullanıcıdan Kaydetme Konumunu Al
        save_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Farklı Kaydet", 
            "output.pdf",  # Varsayılan dosya adı
            "PDF Files (*.pdf);;All Files (*)"
        )

        # 📌 Eğer kullanıcı bir yol seçtiyse, PDF'yi buraya kaydet
        if save_path:
            if not self.page_height_input.text():
                self.pdf_processor.calculate_transparent_logos(
                    pdf_path=self.pdf_path,
                    output_path=save_path,
                    logo_width_cm=float(self.logo_width_input.text()),
                    logo_height_cm=float(self.logo_height_input.text()),
                    spacing_cm=float(self.spacing_input.text()),
                    spacingy_cm=float(self.spacingy_input.text()),
                    page_width_cm=float(self.page_width_input.text()),
                    pagexcm=float(self.page_left_margin_input.text()),
                    pagexrcm=float(self.page_right_margin_input.text()),
                    pageycm=float(self.page_top_margin_input.text()),
                    total_logo=int(self.total_logo_input.text()),
                )
            else:
                self.pdf_processor.add_transparent_logos(
                    pdf_path=self.pdf_path,
                    output_path=save_path,
                    logo_width_cm=float(self.logo_width_input.text()),
                    logo_height_cm=float(self.logo_height_input.text()),
                    spacing_cm=float(self.spacing_input.text()),
                    spacingy_cm=float(self.spacingy_input.text()),
                    page_width_cm=float(self.page_width_input.text()),
                    page_height_cm=float(self.page_height_input.text()),
                    pagexcm=float(self.page_left_margin_input.text()),
                    pagexrcm=float(self.page_right_margin_input.text()),
                    pageycm=float(self.page_top_margin_input.text()),
                    total_logo=int(self.total_logo_input.text()),
                    arkaplan=True,
                    bg_color=self.bg_color
                )
            
            # Ayarları kaydet
            self.setkaydet()
            print(f"PDF kaydedildi: {save_path}")

    def apply_changes(self):
        """Manuel sayfa boyunu kullanarak PDF oluştur"""
        if not self.pdf_path:
            self.pdf_preview_label.setText("Lütfen önce bir PDF dosyası seçin!")
            return
            
        current_dir = os.getcwd()
        output1_path = os.path.join(current_dir, "output_preview.pdf")
        self.pdf_processor.add_transparent_logos(
            pdf_path=self.pdf_path,
            output_path=output1_path,
            logo_width_cm=float(self.logo_width_input.text()),
            logo_height_cm=float(self.logo_height_input.text()),
            spacing_cm=float(self.spacing_input.text()),
            spacingy_cm=float(self.spacingy_input.text()),
            page_width_cm=float(self.page_width_input.text()),
            page_height_cm=float(self.page_height_input.text()),
            pagexcm=float(self.page_left_margin_input.text()),
            pagexrcm=float(self.page_right_margin_input.text()),
            pageycm=float(self.page_top_margin_input.text()),
            total_logo=int(self.total_logo_input.text()),
        )
        self.load_pdf_preview(output1_path)

    def calculate_page_height(self):
        """Sayfa yüksekliğini otomatik hesapla"""
        if not self.pdf_path:
            self.pdf_preview_label.setText("Lütfen önce bir PDF dosyası seçin!")
            return
            
        current_dir = os.getcwd()
        output1_path = os.path.join(current_dir, "output_preview.pdf")
        
        page_height_pt = self.pdf_processor.calculate_transparent_logos(
            pdf_path=self.pdf_path,
            output_path=output1_path,
            logo_width_cm=float(self.logo_width_input.text()),
            logo_height_cm=float(self.logo_height_input.text()),
            spacing_cm=float(self.spacing_input.text()),
            spacingy_cm=float(self.spacingy_input.text()),
            page_width_cm=float(self.page_width_input.text()),
            pagexcm=float(self.page_left_margin_input.text()),
            pagexrcm=float(self.page_right_margin_input.text()),
            pageycm=float(self.page_top_margin_input.text()),
            total_logo=int(self.total_logo_input.text()),
        )
        
        self.heighta = page_height_pt
        self.page_height_input.setText(f"{page_height_pt / CM_TO_PT:.2f}")
        self.load_pdf_preview2(output1_path)
        print("Sayfa boyu hesaplama fonksiyonu tetiklendi.")

    def update_logo_dimensions(self, source_input):
        """Kullanıcı Enter tuşuna basınca veya kutudan çıkınca en/boy oranına göre günceller"""
        if self.aspect_ratio_locked:
            try:
                if source_input == self.logo_width_input:
                    self.update_logo_height()
                elif source_input == self.logo_height_input:
                    self.update_logo_width()
            except ValueError:
                pass

    def toggle_aspect_ratio_lock(self):
        """Ölçek kilidini aç/kapat ve o anki oranı baz al."""
        if not self.aspect_ratio_locked:
            try:
                self.inputlogowidth = float(self.logo_width_input.text())
                self.inputlogoheight = float(self.logo_height_input.text())

                if self.inputlogowidth > 0 and self.inputlogoheight > 0:
                    self.fixed_aspect_ratio = self.inputlogowidth / self.inputlogoheight
                else:
                    self.fixed_aspect_ratio = self.logo_aspect_ratio if self.logo_aspect_ratio else 1.0
            except ValueError:
                self.fixed_aspect_ratio = self.logo_aspect_ratio if self.logo_aspect_ratio else 1.0

        self.aspect_ratio_locked = not self.aspect_ratio_locked

        if self.aspect_ratio_locked:
            self.lock_scale_button.setText("Ölçek Kilidi: Açık 🔒")
            if self.focusWidget() == self.logo_width_input:
                self.update_logo_dimensions(self.logo_width_input)
            elif self.focusWidget() == self.logo_height_input:
                self.update_logo_dimensions(self.logo_height_input)
            else:
                self.update_logo_dimensions(self.logo_width_input)
        else:
            self.lock_scale_button.setText("Ölçek Kilidi: Kapalı 🔓")

    def update_logo_height(self):
        """En girişine göre boyu otomatik hesapla"""
        if self.aspect_ratio_locked:
            try:
                self.inputlogowidth = float(self.logo_width_input.text())
                self.inputlogoheight = self.inputlogowidth / self.fixed_aspect_ratio
                self.logo_height_input.setText(f"{self.inputlogoheight:.2f}")
            except ValueError:
                self.logo_height_input.setText("Hata!")

    def update_logo_width(self):
        """Boy girişine göre eni otomatik hesapla"""
        if self.aspect_ratio_locked:
            try:
                self.inputlogoheight = float(self.logo_height_input.text())
                self.inputlogowidth = self.inputlogoheight * self.fixed_aspect_ratio
                self.logo_width_input.setText(f"{self.inputlogowidth:.2f}")
            except ValueError:
                self.logo_width_input.setText("Hata!")

    def dragEnterEvent(self, event):
        """Sürükleme olayını kontrol et"""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith('.pdf'):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event):
        """Dosya bırakıldığında çalışacak fonksiyon"""
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        if files:
            self.pdf_path = files[0]
            self.rotation_angle = 0
            self.process_pdf_file(self.pdf_path)

    def select_pdf(self):
        """PDF dosyası seç"""
        options = QFileDialog.Options()
        self.pdf_path, _ = QFileDialog.getOpenFileName(
            self, "PDF Dosyası Seç", "", "PDF Files (*.pdf);;All Files (*)", options=options
        )
        if self.pdf_path:
            self.rotation_angle = 0
            self.process_pdf_file(self.pdf_path)

    def process_pdf_file(self, pdf_path):
        """PDF dosyasını işle"""
        try:
            # PDF'i işle ve kırp
            processed_pdf, width, height = self.file_manager.process_pdf_file(pdf_path, self.pdf_processor)
            
            self.pdf_path = processed_pdf
            # pdf_processor'a da pdf_path'i ayarla
            self.pdf_processor.pdf_path = processed_pdf
            
            # Oranı hesapla ve kaydet
            self.logo_aspect_ratio = width / height
            self.fixed_aspect_ratio = self.logo_aspect_ratio
            
            # Form alanlarını güncelle
            self.logo_width_input.setText(f"{width:.2f}")
            self.logo_height_input.setText(f"{height:.2f}")
            
            # Önizleme oluştur
            pixmap = self.file_manager.create_preview_image(self.pdf_path, dpi=96)
            if pixmap:
                self.logo_preview_label.setPixmap(pixmap.scaled(100, 100))
            
        except Exception as e:
            print(f"PDF işleme hatası: {str(e)}")
            traceback.print_exc()

    def rotate_logo(self):
        """Logoyu 90 derece döndür"""
        if not self.pdf_path:
            print("Lütfen önce bir PDF yükleyin!")
            return

        try:
            # Rotasyon açısını güncelle
            self.rotation_angle = (self.rotation_angle + 90) % 360
            
            # PDF'i döndür
            rotated_pdf = self.file_manager.rotate_pdf(self.pdf_path, self.rotation_angle)
            
            if rotated_pdf:
                self.pdf_path = rotated_pdf
                
                # Mevcut değerleri al
                current_width = float(self.logo_width_input.text())
                current_height = float(self.logo_height_input.text())
                
                # Rotasyon açısına göre boyutları güncelle
                if self.rotation_angle in [90, 270]:
                    new_width = current_height
                    new_height = current_width
                else:
                    new_width = current_width
                    new_height = current_height
                
                # Form alanlarını güncelle
                self.logo_width_input.setText(f"{new_width:.2f}")
                self.logo_height_input.setText(f"{new_height:.2f}")
                
                # Logo oranını güncelle
                self.logo_aspect_ratio = new_width / new_height
                self.fixed_aspect_ratio = self.logo_aspect_ratio
                
                # Önizlemeyi güncelle
                pixmap = self.file_manager.create_preview_image(self.pdf_path, dpi=300)
                if pixmap:
                    self.logo_preview_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                
                print(f"Logo başarıyla {self.rotation_angle}° döndürüldü")
                
        except Exception as e:
            print(f"Döndürme hatası: {str(e)}")
            traceback.print_exc()

    def load_pdf_preview(self, pdf_path):
        """PDF önizlemesi yükle"""
        # Kullanıcının belirlediği sayfa genişliği ve yüksekliği (cm)
        try:
            user_width_cm = float(self.page_width_input.text())
            user_height_cm = float(self.page_height_input.text())
        except ValueError:
            self.pdf_preview_label.setText("Geçerli bir genişlik ve yükseklik girin!")
            return

        # PDF'i aç ve ilk sayfayı yükle
        doc = fitz.open(pdf_path)
        page = doc[0]
        pix = page.get_pixmap(dpi=96)  # 96 DPI önizleme için uygundur

        # Kullanıcı girdilerini piksel cinsine dönüştür
        target_width_px = int(user_width_cm * 37.795)  # 1 cm = 37.795 px
        target_height_px = int(user_height_cm * 37.795)

        # QImage ve QPixmap'e dönüştür
        qt_img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_img)

        # Pixmap'i ölçekle ve etikete uygula
        self.pdf_preview_label.setPixmap(pixmap.scaled(target_width_px, target_height_px))
        doc.close()

    def load_pdf_preview2(self, pdf_path):
        """PDF önizlemesi yükle (dinamik yükseklik)"""
        # Kullanıcının belirlediği sayfa genişliği ve yüksekliği (cm)
        try:
            user_width_cm = float(self.page_width_input.text())
            user_height_cm = self.heighta
        except ValueError:
            self.pdf_preview_label.setText("Geçerli bir genişlik girin!")
            return
            
        # PDF'i aç ve ilk sayfayı yükle
        doc = fitz.open(pdf_path)
        page = doc[0]
        pix = page.get_pixmap(dpi=96)  # 96 DPI önizleme için uygundur

        # Kullanıcı girdilerini piksel cinsine dönüştür
        target_width_px = int(user_width_cm * 37.795)  # 1 cm = 37.795 px
        target_height_px = int(user_height_cm)

        # QImage ve QPixmap'e dönüştür
        qt_img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_img)

        # Pixmap'i ölçekle ve etikete uygula
        self.pdf_preview_label.setPixmap(pixmap.scaled(target_width_px, target_height_px))
        doc.close()


def main():
    app = QApplication(sys.argv)
    window = PDFEditorApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
