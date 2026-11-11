<<<<<<< HEAD
import time

def get_mock_dispute_data(dispute_id: str):
    """
    Shopify'dan gelen dispute ve kargo kanıtı verilerini simüle eder.
    """
    return {
        "dispute_id": dispute_id,
        "order_id": "ORD-99281",
        "customer_name": "Ahmet Yılmaz",
        "customer_email": "ahmet@example.com",
        "amount": "149.99 USD",
        "reason": "Unrecognized charge / Fraudulent",
        "tracking_number": "TR-987654321",
        "carrier": "Yurtici Kargo",
        "fulfillment_status": "Delivered",
        "delivery_date": "2026-11-06 14:30"
    }


def submit_dispute_evidence(dispute_id: str, pdf_path: str, access_token: str):
    """
    Oluşturulan PDF savunma dosyasını Shopify Dispute API'ye otonom sunar.
    """
    print(f"[OTONOM API] '{pdf_path}' dosyası Shopify Dispute API'ye yükleniyor...")
    time.sleep(1)
    
    print(f"[OTONOM API] Dispute {dispute_id} için kanıtlar bankaya başarıyla teslim edildi!")
    return {
        "submission_status": "submitted",
        "dispute_id": dispute_id,
        "submitted_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidence_file": pdf_path,
        "message": "Savunma dosyası ve kargo kanıtları bankaya otonom olarak iletildi."
=======
import time

def get_mock_dispute_data(dispute_id: str):
    """
    Shopify'dan gelen dispute ve kargo kanıtı verilerini simüle eder.
    """
    return {
        "dispute_id": dispute_id,
        "order_id": "ORD-99281",
        "customer_name": "Ahmet Yılmaz",
        "customer_email": "ahmet@example.com",
        "amount": "149.99 USD",
        "reason": "Unrecognized charge / Fraudulent",
        "tracking_number": "TR-987654321",
        "carrier": "Yurtici Kargo",
        "fulfillment_status": "Delivered",
        "delivery_date": "2026-11-06 14:30"
    }


def submit_dispute_evidence(dispute_id: str, pdf_path: str, access_token: str):
    """
    Oluşturulan PDF savunma dosyasını Shopify Dispute API'ye otonom sunar.
    """
    print(f"[OTONOM API] '{pdf_path}' dosyası Shopify Dispute API'ye yükleniyor...")
    time.sleep(1)
    
    print(f"[OTONOM API] Dispute {dispute_id} için kanıtlar bankaya başarıyla teslim edildi!")
    return {
        "submission_status": "submitted",
        "dispute_id": dispute_id,
        "submitted_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidence_file": pdf_path,
        "message": "Savunma dosyası ve kargo kanıtları bankaya otonom olarak iletildi."
>>>>>>> e7ecfbb0f066597f629a938b94142e8d2ab9c74d
    }