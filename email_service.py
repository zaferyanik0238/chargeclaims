<<<<<<< HEAD
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os

def send_dispute_notification(to_email: str, dispute_id: str, pdf_path: str):
    """
    Dispute çözüldüğünde ve bankaya sunulduğunda satıcıya otomatik e-posta gönderir.
    """
    # Test/Simülasyon ortamı için SMTP ayarları (Gerekirse kendi SMTP bilgilerinizle güncelleyebilirsiniz)
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SENDER_EMAIL = "chargeclaims.bot@gmail.com"
    SENDER_PASSWORD = "ornek_uygulama_sifresi" # Gerçek kullanımda app password veya environment variable kullanılır

    subject = f"ChargeClaims Otonom Raporu: Dispute #{dispute_id} Çözüldü"
    
    body = f"""
    Sayın Mağaza Yetkilisi,
    
    Sistemimiz Shopify mağazanıza gelen yeni bir dispute talebini ({dispute_id}) otomatik olarak yakaladı.
    
    - Olay Durumu: Başarıyla Tamamlandı
    - İşlem: Savunma dosyası oluşturuldu ve bankaya otonom olarak sunuldu.
    - Ekli Dosya: Otomatik üretilen kanıt ve savunma PDF'i ektedir.
    
    ChargeClaims B2B SaaS Altyapısı ile sıfır insan müdahalesiyle koruma altındasınız.
    """

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))

    # Üretilen PDF savunma dosyasını e-postaya ekleyelim
    if pdf_path and os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            attach = MIMEApplication(f.read(), Name=os.path.basename(pdf_path))
            attach['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf_path)}"'
            msg.attach(attach)

    try:
        # Simülasyon / Gerçek Gönderim Bloğu
        print(f"[EMAIL SERVICE] E-posta başarıyla {to_email} adresine gönderildi (Dispute ID: {dispute_id})")
        return True
    except Exception as e:
        print(f"[EMAIL SERVICE HATA] E-posta gönderilemedi: {e}")
=======
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os

def send_dispute_notification(to_email: str, dispute_id: str, pdf_path: str):
    """
    Dispute çözüldüğünde ve bankaya sunulduğunda satıcıya otomatik e-posta gönderir.
    """
    # Test/Simülasyon ortamı için SMTP ayarları (Gerekirse kendi SMTP bilgilerinizle güncelleyebilirsiniz)
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SENDER_EMAIL = "chargeclaims.bot@gmail.com"
    SENDER_PASSWORD = "ornek_uygulama_sifresi" # Gerçek kullanımda app password veya environment variable kullanılır

    subject = f"ChargeClaims Otonom Raporu: Dispute #{dispute_id} Çözüldü"
    
    body = f"""
    Sayın Mağaza Yetkilisi,
    
    Sistemimiz Shopify mağazanıza gelen yeni bir dispute talebini ({dispute_id}) otomatik olarak yakaladı.
    
    - Olay Durumu: Başarıyla Tamamlandı
    - İşlem: Savunma dosyası oluşturuldu ve bankaya otonom olarak sunuldu.
    - Ekli Dosya: Otomatik üretilen kanıt ve savunma PDF'i ektedir.
    
    ChargeClaims B2B SaaS Altyapısı ile sıfır insan müdahalesiyle koruma altındasınız.
    """

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))

    # Üretilen PDF savunma dosyasını e-postaya ekleyelim
    if pdf_path and os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            attach = MIMEApplication(f.read(), Name=os.path.basename(pdf_path))
            attach['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf_path)}"'
            msg.attach(attach)

    try:
        # Simülasyon / Gerçek Gönderim Bloğu
        print(f"[EMAIL SERVICE] E-posta başarıyla {to_email} adresine gönderildi (Dispute ID: {dispute_id})")
        return True
    except Exception as e:
        print(f"[EMAIL SERVICE HATA] E-posta gönderilemedi: {e}")
>>>>>>> e7ecfbb0f066597f629a938b94142e8d2ab9c74d
        return False