"""
PDF işleme fonksiyonları modülü
"""

import os
import fitz
import xml.etree.ElementTree as ET
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from PyQt5.QtGui import QImage, QPixmap

# Sabitler
CM_TO_PT = 72/2.54
TEMP_SVG_FILE = "temp.svg"
TEMP_PDF_FILE = "temp_logo.pdf"

class PDFProcessor:
    def __init__(self):
        """PDFProcessor sınıfını başlat"""
        # Temp dizini yoksa oluştur
        if not os.path.exists("temp"):
            os.makedirs("temp")
        
        self.witdhlog = 0
        self.heightlog = 0
        self.pgwrat = 0
        self.pghrat = 0
        self.heighta = 0
        self.pdf_path = None
        self.bg_color = "#ffffff"
    
    def get_logo_bbox(self, pdf_path):
        # global v
        # v=0
        doc = fitz.open(pdf_path)
        x_min, y_min = float('inf'), float('inf')
        x_max, y_max = float('-inf'), float('-inf')
        logo_found = False
        
        for page in doc:
            drawings = page.get_drawings()
            
            for item in drawings:
                # item bir sözlük ise "rect" anahtarı ile erişim sağlıyoruz
                if isinstance(item, dict) and "rect" in item:
                    bbox = item["rect"]
                    if not bbox.is_empty:  # Boş olmayan bir bbox kontrolü
                        # logo_found = True
                        x_min = min(x_min, bbox.x0)
                        y_min = min(y_min, bbox.y0)
                        x_max = max(x_max, bbox.x1)
                        y_max = max(y_max, bbox.y1)
                # v += 1
        self.witdhlog = (x_max - x_min)/72 * 2.54
        self.heightlog = (y_max - y_min)/72 * 2.54
        print(f"Logo Boyutu: {self.witdhlog:.2f}cm x {self.heightlog:.2f}cm")
        
        doc.close()
        
        return self.witdhlog, self.heightlog

    def process_svg(self, svg_content, logo_width_cm, logo_height_cm):
        """SVG içeriğini işle"""
        root = ET.fromstring(svg_content)
        ns = {'svg': 'http://www.w3.org/2000/svg'}
        
        # Arkaplanı temizle
        for rect in root.findall('.//svg:rect', ns):
            if rect.get('width') == "100%" or rect.get('fill') == "#ffffff":
                root.remove(rect)
        
        # SVG boyutlarını ayarla
        root.set('width', f'{logo_width_cm}cm')
        root.set('height', f'{logo_height_cm}cm')
        
        return ET.tostring(root, encoding='unicode')

    def convert_svg_to_pdf(self, svg_content, logo_width_pt, logo_height_pt):
        """SVG'yi PDF'e dönüştür"""
        # SVG'yi kaydet
        with open(TEMP_SVG_FILE, "w") as f:
            f.write(svg_content)
        
        # PDF'e dönüştür
        drawing = svg2rlg(TEMP_SVG_FILE)
        drawing.width = logo_width_pt
        drawing.height = logo_height_pt
        renderPDF.drawToFile(drawing, TEMP_PDF_FILE)
        
        return TEMP_PDF_FILE

    def rotate_pdf(self, pdf_path, angle):
        """PDF'i döndür ve temp dosyasını geri döndür"""
        temp_rotated_path = "temp_rotated_90.pdf"
        
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

    def add_transparent_logos(
        self,
        pdf_path,
        output_path,
        logo_width_cm=10,
        logo_height_cm=10,
        spacing_cm=3,
        spacingy_cm=3,
        page_width_cm=58,
        page_height_cm=60,
        pagexcm=2,
        pagexrcm=2,
        pageycm=2,
        total_logo=12,
        arkaplan=False,
        bg_color="#ffffff"
    ):
        # CM'yi Point'e çevirme (1 cm = CM_TO_PT pt)
        page_width_pt = page_width_cm * CM_TO_PT
        page_height_pt = page_height_cm * CM_TO_PT
        logo_width_pt = logo_width_cm * CM_TO_PT  # Kullanıcının istediği genişlik
        logo_height_pt = logo_height_cm * CM_TO_PT  # Kullanıcının istediği yükseklik
        spacing_pt = spacing_cm * CM_TO_PT
        spacingy_pt = spacingy_cm * CM_TO_PT
        page_margin_x_pt = pagexcm * CM_TO_PT
        page_margin_xr_pt = pagexrcm * CM_TO_PT
        page_margin_y_pt = pageycm * CM_TO_PT

        # SVG'yi arkaplansız olarak çekme ve BOYUTLANDIRMA
        doc = fitz.open(pdf_path)
        page = doc[0]
        pgwidth, pgheight = page.mediabox.width, page.mediabox.height
        pgwidth = (pgwidth / 72) * 2.54 
        pgheight = (pgheight / 72) * 2.54 
        self.get_logo_bbox(pdf_path=pdf_path)
        self.pgwrat = pgwidth / self.witdhlog
        self.pghrat = pgheight / self.heightlog
        svg_content = page.get_svg_image()

        # SVG'yi parse et ve boyutları değiştir
        root = ET.fromstring(svg_content)
        ns = {'svg': 'http://www.w3.org/2000/svg'}
        
        # 1. Orijinal SVG boyutunu al (varsayılan olarak 100% veya px)
        original_width = root.get('width', '100%')
        original_height = root.get('height', '100%')
        
        # 2. Arkaplanı temizle
        for rect in root.findall('.//svg:rect', ns):
            if rect.get('width') == "100%" or rect.get('fill') == "#ffffff":
                root.remove(rect)
        logo_width_cm = self.pgwrat * logo_width_cm
        logo_height_cm = self.pghrat * logo_height_cm
        logo_height_pt = self.pghrat * logo_height_pt
        logo_width_pt = self.pgwrat * logo_width_pt
        
        # 3. SVG'nin genişlik ve yüksekliğini KULLANICI GİRİŞİNE göre ayarla
        root.set('width', f'{logo_width_cm}cm')  # Önemli: SVG'yi cm cinsinden yeniden boyutlandır
        root.set('height', f'{logo_height_cm}cm')
        # root.set('viewBox', f'0 0 {original_width} {original_height}')  # Orijinal içeriği koru
        
        cleaned_svg = ET.tostring(root, encoding='unicode')        # Geçici SVG dosyasını kaydetme
        temp_svg = "temp_logo.svg"
        with open(temp_svg, "w") as f:
            f.write(cleaned_svg)

        # SVG'yi PDF'ye dönüştürürken BOYUTLARI ZORLA
        temp_pdf = "temp_logo.pdf"
        drawing = svg2rlg(temp_svg)
        
        # PDF sayfa boyutunu logo boyutlarına ayarla
        drawing.width = logo_width_pt
        drawing.height = logo_height_pt
        renderPDF.drawToFile(drawing, temp_pdf)

        # Yeni PDF oluşturma
        new_doc = fitz.open()
        
        new_page = new_doc.new_page(width=page_width_pt, height=page_height_pt)
        if arkaplan:
            print(self.hex_to_rgb(bg_color))
            background_color = self.hex_to_rgb(bg_color)
            new_page.draw_rect(new_page.rect, color=None, fill=background_color, overlay=False)

        # Hesaplamalar
        logos_per_row = int(
            (page_width_pt - page_margin_x_pt - page_margin_xr_pt + spacing_pt)
            / (logo_width_pt + spacing_pt)
        )
        x_offset = page_margin_x_pt
        y_offset = page_margin_y_pt
        logo_count = 0

        # Logo yerleştirme
        with fitz.open(temp_pdf) as logo_pdf:
            logo_page = logo_pdf[0]
            
            while logo_count < total_logo:
                rect = fitz.Rect(
                    x_offset,
                    y_offset,
                    x_offset + logo_width_pt,
                    y_offset + logo_height_pt,
                )
                # PDF'yi ÖLÇEKLENDİRMEDEN yerleştir (artık boyutlar eşleşiyor)
                new_page.show_pdf_page(rect, logo_pdf, 0)
                
                logo_count += 1
                x_offset += logo_width_pt + spacing_pt
                
                if logo_count % logos_per_row == 0:
                    x_offset = page_margin_x_pt
                    y_offset += logo_height_pt + spacingy_pt
                
                if y_offset + logo_height_pt > page_height_pt - page_margin_y_pt:
                    break

        new_doc.save(output_path)
        print(f"✅ Transparan logolu PDF kaydedildi: {output_path}")
        
        # Temizlik
        # os.remove(temp_svg)
        return page_height_pt
    
    def hex_to_rgb(self, value):
        """Hex rengi RGB değerlerine dönüştür (0-1 aralığında)"""
        value = value.lstrip('#')
        lv = len(value)
        return tuple(int(value[i:i + lv // 3], 16)/255 for i in range(0, lv, lv // 3))

    def calculate_transparent_logos(
        self,
        pdf_path,
        output_path,
        logo_width_cm=10,
        logo_height_cm=10,
        spacing_cm=3,
        spacingy_cm=3,
        page_width_cm=58,
        pagexcm=2,
        pagexrcm=2,
        pageycm=2,
        total_logo=12,
    ):
        # CM'yi Point'e çevirme (1 cm = CM_TO_PT pt)
        page_width_pt = page_width_cm * CM_TO_PT
        logo_width_pt = logo_width_cm * CM_TO_PT  # Kullanıcıdan alınan logo genişliği
        logo_height_pt = logo_height_cm * CM_TO_PT  # Kullanıcıdan alınan logo yüksekliği
        spacing_pt = spacing_cm * CM_TO_PT
        spacingy_pt = spacingy_cm * CM_TO_PT
        page_margin_x_pt = pagexcm * CM_TO_PT
        page_margin_xr_pt = pagexrcm * CM_TO_PT
        page_margin_y_pt = pageycm * CM_TO_PT

        # SVG'yi işleme ve BOYUTLANDIRMA
        doc = fitz.open(pdf_path)
        page = doc[0]
        pgwidth, pgheight = page.mediabox.width, page.mediabox.height
        pgwidth = (pgwidth / 72) * 2.54 
        pgheight = (pgheight / 72) * 2.54 
        self.get_logo_bbox(pdf_path=pdf_path)
        self.pgwrat = pgwidth / self.witdhlog
        self.pghrat = pgheight / self.heightlog
        svg_content = page.get_svg_image()

        # SVG'yi parse et ve boyutları ayarla
        root = ET.fromstring(svg_content)
        ns = {'svg': 'http://www.w3.org/2000/svg'}
        
        # 1. Arkaplanı temizle
        for rect in root.findall('.//svg:rect', ns):
            if rect.get('width') == "100%" or rect.get('fill') == "#ffffff":
                root.remove(rect)
        logo_width_cm2 = self.pgwrat * logo_width_cm
        logo_height_cm2 = self.pghrat * logo_height_cm
        logo_height_pt2 = self.pghrat * logo_height_pt
        logo_width_pt2 = self.pgwrat * logo_width_pt
        # 2. SVG boyutlarını KULLANICI GİRİŞİNE göre zorla (kritik düzeltme!)
        root.set('width', f'{logo_width_cm}cm')
        root.set('height', f'{logo_height_cm}cm')
        cleaned_svg = ET.tostring(root, encoding='unicode')

        # Geçici SVG dosyasını kaydetme
        temp_svg = "temp_logo.svg"
        with open(temp_svg, "w") as f:
            f.write(cleaned_svg)

        # SVG'yi PDF'ye dönüştürürken BOYUT ZORLAMA (kritik düzeltme!)
        temp_pdf = "temp_logo.pdf"
        drawing = svg2rlg(temp_svg)
        drawing.width = logo_width_pt  # PDF boyutunu kullanıcı girdisine ayarla
        drawing.height = logo_height_pt
        renderPDF.drawToFile(drawing, temp_pdf)
        print(page_width_pt)
        
        # Dinamik sayfa yüksekliği hesaplama
        print(
            (page_width_pt - page_margin_x_pt - page_margin_xr_pt + spacing_pt)
            / (logo_width_pt + spacing_pt)
        )
        logos_per_row = int(
            (page_width_pt - page_margin_x_pt - page_margin_xr_pt + spacing_pt)
            / (logo_width_pt + spacing_pt)
        )
        y = int(total_logo / logos_per_row) + 1
        page_height_pt = page_margin_y_pt + y * logo_height_pt + (y - 1) * spacingy_pt + 50
        print(page_height_pt/CM_TO_PT)
        self.heighta = page_height_pt
        
        # Yeni PDF oluşturma
        new_doc = fitz.open()
        new_page = new_doc.new_page(width=page_width_pt, height=page_height_pt)

        # Logo yerleştirme
        x_offset = page_margin_x_pt
        y_offset = page_margin_y_pt
        logo_count = 0

        with fitz.open(temp_pdf) as logo_pdf:
            while logo_count < total_logo:
                rect = fitz.Rect(
                    x_offset,
                    y_offset,
                    x_offset + logo_width_pt,
                    y_offset + logo_height_pt,
                )
                new_page.show_pdf_page(rect, logo_pdf, 0)

                logo_count += 1
                x_offset += logo_width_pt + spacing_pt

                if logo_count % logos_per_row == 0:
                    x_offset = page_margin_x_pt
                    y_offset += logo_height_pt + spacingy_pt

                if y_offset + logo_height_pt > page_height_pt - page_margin_y_pt:
                    break

        new_doc.save(output_path)
        print(f"✅ Transparan logolu PDF kaydedildi: {output_path}")
        
        # Temizlik (düzeltildi)
        # os.remove(temp_svg)
        # os.remove(temp_pdf)  # Geçici PDF'yi de sil
        
        return page_height_pt
