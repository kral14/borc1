import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QMessageBox, QGridLayout, QSpacerItem, QSizePolicy
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, QSize

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern Oturum Açma Ekranı")
        self.setFixedSize(400, 350) # Pencere boyutunu sabitleyelim
        self.setWindowIcon(QIcon(":/icons/lock.png")) # İsteğe bağlı: Bir ikon ekleyebilirsiniz

        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        # Ana düzen (grid layout)
        main_layout = QGridLayout()
        self.setLayout(main_layout)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter) # İçeriği ortala

        # Başlık
        title_label = QLabel("Hoş Geldiniz!")
        title_label.setObjectName("titleLabel") # QSS ile hedeflemek için
        main_layout.addWidget(title_label, 0, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter) # 0. satır, 0. sütun, 1 satır kapla, 2 sütun kapla

        # Kullanıcı Adı Girişi
        username_label = QLabel("Kullanıcı Adı:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Kullanıcı adınızı girin")
        self.username_input.setMinimumHeight(35) # Yüksekliği artır

        main_layout.addWidget(username_label, 1, 0, alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(self.username_input, 1, 1)

        # Şifre Girişi
        password_label = QLabel("Şifre:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Şifrenizi girin")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password) # Şifreyi gizle
        self.password_input.setMinimumHeight(35) # Yüksekliği artır

        main_layout.addWidget(password_label, 2, 0, alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(self.password_input, 2, 1)

        # Oturum Açma Butonu
        login_button = QPushButton("Giriş Yap")
        login_button.setObjectName("loginButton") # QSS ile hedeflemek için
        login_button.setMinimumHeight(45) # Yüksekliği artır
        login_button.clicked.connect(self.authenticate_user)
        main_layout.addWidget(login_button, 3, 0, 1, 2) # 3. satır, 0. sütun, 1 satır kapla, 2 sütun kapla

        # Şifremi Unuttum Butonu (Link gibi görünecek)
        forgot_password_button = QPushButton("Şifremi Unuttum?")
        forgot_password_button.setObjectName("forgotPasswordButton") # QSS ile hedeflemek için
        forgot_password_button.clicked.connect(self.show_forgot_password)
        main_layout.addWidget(forgot_password_button, 4, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)

        # Boşluklar ekleyelim (Layout içinde widget'lar arası boşluk)
        main_layout.setVerticalSpacing(15) # Dikey boşluk
        main_layout.setHorizontalSpacing(10) # Yatay boşluk

        # Kenarlara boşluk eklemek için Spacer'lar
        main_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding), 5, 0, 1, 2)


    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #e0f2f7; /* Açık mavi arka plan */
                font-family: 'Segoe UI', sans-serif;
                color: #333;
            }

            /* Başlık etiketi stilleri */
            #titleLabel {
                font-size: 28px;
                font-weight: bold;
                color: #2c3e50; /* Koyu mavi başlık */
                margin-bottom: 20px;
                text-align: center; /* Metni ortala */
            }

            /* Genel etiket stilleri */
            QLabel {
                font-size: 14px;
                font-weight: 500;
                color: #555;
            }

            /* Giriş kutusu stilleri */
            QLineEdit {
                border: 2px solid #a7d9f7; /* Açık mavi kenarlık */
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 15px;
                background-color: #f7fcfc; /* Hafif beyaz arka plan */
                color: #333;
                selection-background-color: #add8e6; /* Seçili metin arka planı */
            }
            QLineEdit:focus {
                border: 2px solid #3498db; /* Odaklandığında daha koyu mavi */
                background-color: #ffffff;
            }

            /* Giriş butonu stilleri */
            #loginButton {
                background-color: #3498db; /* Mavi buton */
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 25px;
                font-size: 18px;
                font-weight: bold;
                margin-top: 15px;
                letter-spacing: 0.5px; /* Harf aralığı */
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2); /* Hafif gölge */
            }
            #loginButton:hover {
                background-color: #2980b9; /* Hover'da daha koyu */
                transform: scale(1.02); /* Hafif büyütme efekti (QSS'de tam olarak desteklenmez, ancak bazı temel dönüşümler mümkündür) */
            }
            #loginButton:pressed {
                background-color: #1a5276; /* Tıklandığında en koyu */
                box-shadow: inset 1px 1px 3px rgba(0, 0, 0, 0.3); /* İç gölge */
            }

            /* Şifremi Unuttum butonu stilleri (link gibi) */
            #forgotPasswordButton {
                background: transparent; /* Arka plan yok */
                color: #3498db; /* Mavi metin */
                border: none;
                text-decoration: underline; /* Altı çizili */
                font-size: 14px;
                margin-top: 10px;
                padding: 5px; /* Tıklama alanı için padding */
            }
            #forgotPasswordButton:hover {
                color: #2980b9;
            }
            #forgotPasswordButton:pressed {
                color: #1a5276;
            }

            /* Ek Özelleştirmeler (Örnek) */
            /* Bir QWidget içindeki tüm QPushButton'lar */
            QWidget QPushButton {
                margin: 5px; /* Butonlar arası dış boşluk */
            }

            /* Belirli bir QLabel'a özel stil (örneğin hata mesajı için) */
            QLabel#errorMessage {
                color: red;
                font-weight: bold;
                font-size: 13px;
            }
        """)
    def authenticate_user(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if username == "admin" and password == "123":
            QMessageBox.information(self, "Başarılı", "Giriş başarılı!")
            # Burada ana uygulama penceresini açabilirsiniz.
        else:
            QMessageBox.warning(self, "Hata", "Kullanıcı adı veya şifre yanlış!")

    def show_forgot_password(self):
        QMessageBox.information(self, "Bilgi", "Şifre sıfırlama ekranına yönlendiriliyorsunuz...")
        # Burada şifre sıfırlama ekranını açabilirsiniz.

if __name__ == "__main__":
    # İkon dosyasını Resource System'e eklemek için:
    # 1. 'icons' adında bir klasör oluşturun.
    # 2. 'lock.png' gibi bir ikon dosyasını bu klasöre koyun.
    # 3. Bir .qrc dosyası oluşturun (örneğin 'resources.qrc'):
    #    <RCC>
    #      <qresource prefix="/icons">
    #        <file>lock.png</file>
    #      </qresource>
    #    </RCC>
    # 4. Terminalde bu komutu çalıştırın:
    #    pyrcc6 resources.qrc -o resources_rc.py
    # 5. Bu dosyayı import edin: import resources_rc
    # Eğer bu adımları yapmazsanız, setWindowIcon satırını yorum satırı yapın veya doğrudan bir dosya yolu verin.

    # Eğer ikon kullanmayacaksanız, aşağıdaki satırı eklemenize gerek yok.
    # import resources_rc # Eğer bir kaynak dosyası oluşturduysanız

    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())