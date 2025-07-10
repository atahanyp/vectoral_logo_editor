"""
Kullanıcı arayüzü bileşenleri için özel widget sınıfları
"""

from PyQt5.QtWidgets import QLineEdit


class CustomLineEdit(QLineEdit):
    """Özel QLineEdit: Enter tuşuna basıldığında veya focus kaybedildiğinde işlem yapar."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.returnPressed.connect(self.handle_confirm)  # Enter tuşuna basıldığında

    def focusOutEvent(self, event):
        """Kullanıcı başka bir kutuya geçince çağrılır"""
        self.handle_confirm()
        super().focusOutEvent(event)  # Normal davranışı devam ettir

    def handle_confirm(self):
        """Enter veya focusOut olduğunda ana fonksiyon çağrılacak"""
        main_window = self.window()  # `window()` kullanarak ana pencereyi al
        if hasattr(main_window, "update_logo_dimensions"):
            main_window.update_logo_dimensions(self)
