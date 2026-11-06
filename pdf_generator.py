import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_defense_pdf(dispute_data: dict) -> str:
    # Klasör yoksa oluştur
    output_dir = "output_pdfs"
    os.makedirs(output_dir, exist_ok=True)
    
    dispute_id = dispute_data.get("dispute_id", "disp_unknown")
    pdf_path = os.path.join(output_dir, f"defense_{dispute_id}.pdf")
    
    # Güvenli veri çekme (.get kullanarak KeyError riskini tamamen sıfırlıyoruz)
    order_id = dispute_data.get("order_id", "N/A")
    amount = dispute_data.get("amount", "$0.00")
    reason = dispute_data.get("reason", "Unknown")
    customer_name = dispute_data.get("customer_name", dispute_data.get("customer", "Müşteri"))
    carrier = dispute_data.get("carrier", "Kargo Firması")
    fulfillment_status = dispute_data.get("fulfillment_status", "Delivered")
    delivery_date = dispute_data.get("delivery_date", "N/A")

    # PDF Oluşturma
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    
    # Başlık
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "ChargeClaims - Otonom Savunma Dosyası")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Dispute ID: {dispute_id}")
    c.drawString(50, height - 100, f"Sipariş Numarası (Order ID): {order_id}")
    c.drawString(50, height - 120, f"Tutar: {amount}")
    c.drawString(50, height - 140, f"İtiraz Sebebi: {reason}")
    
    # Çizgi
    c.setLineWidth(1)
    c.line(50, height - 160, width - 50, height - 160)
    
    # Teslimat ve Kargo Kanıtları
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 190, "Kargo ve Teslimat Kanıtları")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 220, f"Müşteri Adı: {customer_name}")
    c.drawString(50, height - 240, f"Kargo Firması: {carrier}")
    c.drawString(50, height - 260, f"Teslimat Durumu: {fulfillment_status}")
    c.drawString(50, height - 280, f"Teslimat Tarihi: {delivery_date}")
    
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, height - 330, "Bu belge ChargeClaims otonom sistemi tarafından bankaya sunulmak üzere üretilmiştir.")
    
    c.save()
    return pdf_path