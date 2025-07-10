"""
Dosya yönetimi işlevleri modülü
"""

import os
import fitz
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt


class FileManager:
    def __init__(self):
        """Dosya yöneticisi sınıfını başlat"""
        self.settings_file = "kayitliayar.txt"
        
        # Temp klasörünü kontrol et
        if not os.path.exists("temp"):
            os.makedirs("temp")
    
    def useprevset(self):
        """Kayıtlı ayarları yükle"""
        settings = []
        try:
            # Ayar dosyası var mı kontrol et
            if not os.path.exists(self.settings_file):
                # Varsayılan değerlerle dosyayı oluştur
                self.setkaydet(["58", " ", "0.1", "0.1", "0.1"])
            
            # Dosyadan ayarları oku
            with open(self.settings_file, "r", encoding="utf-8") as f:
                for line in f:
                    settings.append(line.strip())
        except Exception as e:
            print(f"Ayar yükleme hatası: {str(e)}")
            # Varsayılan değerler
            settings = ["58", " ", "0.1", "0.1", "0.1"]
        
        return settings
    
    def setkaydet(self, settings):
        """Ayarları kaydet"""
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                for setting in settings:
                    f.write(f"{setting}\n")
            print(f"Ayarlar {self.settings_file} dosyasına kaydedildi.")
        except Exception as e:
            print(f"Ayar kaydetme hatası: {str(e)}")
    
    def process_pdf_file(self, pdf_path, pdf_processor):
        """PDF dosyasını işle ve gerekirse kırp"""
        temp_pdf = os.path.join("temp", "temp_logo.pdf")
        
        # Dosyayı kopyala
        with open(pdf_path, "rb") as src_file:
            pdf_content = src_file.read()
            
        with open(temp_pdf, "wb") as dst_file:
            dst_file.write(pdf_content)
        
        # Logo boyutlarını hesapla
        width_cm, height_cm = pdf_processor.get_logo_bbox(temp_pdf)
        
        return temp_pdf, width_cm, height_cm
    
    def create_preview_image(self, pdf_path, dpi=300):
        """PDF'ten önizleme görseli oluştur"""
        try:
            doc = fitz.open(pdf_path)
            if doc.page_count > 0:
                page = doc[0]
                pix = page.get_pixmap(dpi=dpi)
                
                # PyMuPDF pixmap'i Qt QImage'e dönüştür
                img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(img)
                
                doc.close()
                return pixmap
        except Exception as e:
            print(f"Önizleme oluşturma hatası: {str(e)}")
        
        return None
    
    def rotate_pdf(self, pdf_path, angle):
        """PDF'i döndür ve temp dosyasını geri döndür"""
        temp_rotated_path = os.path.join("temp", "temp_rotated_90.pdf")
        
        try:
            # Orijinal dosyayı kopyala
            doc = fitz.open(pdf_path)
            page = doc[0]
            
            # Yeni döndürülmüş PDF oluştur
            rotated_doc = fitz.open()
            rotated_page = rotated_doc.new_page(width=page.rect.height, height=page.rect.width)
            
            # Döndürme matrisi oluştur
            matrix = fitz.Matrix(0, -1, 1, 0, 0, page.rect.width)  # 90 derece saat yönünde döndürme
            
            # Orijinal sayfayı döndürülmüş sayfaya çiz
            rotated_page.show_pdf_page(rotated_page.rect, doc, 0, matrix=matrix)
            
            # Yeni dosyayı kaydet
            rotated_doc.save(temp_rotated_path)
            rotated_doc.close()
            doc.close()
            
            return temp_rotated_path
        except Exception as e:
            print(f"PDF döndürme hatası: {str(e)}")
            return pdf_path
