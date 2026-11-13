def send_notification_email(to_email: str, dispute_id: str) -> bool:
    try:
        print(
            f"[EMAIL SERVICE] Bildirim hazırlandı: "
            f"{to_email} | Dispute ID: {dispute_id}"
        )
        return True
    except Exception as e:
        print(f"[EMAIL SERVICE HATA] {e}")
        return False