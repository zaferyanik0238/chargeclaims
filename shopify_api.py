import os
import requests

SHOPIFY_API_VERSION = "2024-01"

def verify_shopify_webhook(data: bytes, hmac_header: str) -> bool:
    """
    Verify incoming Shopify webhook signature for security.
    """
    # Placeholder for webhook verification logic
    return True

def get_order_details(shop_url: str, access_token: str, order_id: str) -> dict:
    """
    Fetch order details from Shopify API for dispute automation.
    """
    url = f"https://{shop_url}/admin/api/{SHOPIFY_API_VERSION}/orders/{order_id}.json"
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get("order", {})
    except Exception as e:
        print(f"Error fetching order from Shopify: {e}")
        
    return {}