import os
from weasyprint import HTML

def generate_dispute_pdf(claim_data: dict, output_path: str = "output_pdfs/dispute_defense.pdf") -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Chargeback Dispute Defense</title>
        <style>
            body {{ font-family: Helvetica, Arial, sans-serif; color: #333; margin: 40px; }}
            h1 {{ color: #1e293b; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; }}
            .section {{ margin-top: 20px; }}
            .label {{ font-weight: bold; color: #475569; }}
        </style>
    </head>
    <body>
        <h1>Chargeback Dispute Defense Package</h1>
        <div class="section">
            <p><span class="label">Order ID:</span> {claim_data.get('order_id', 'N/A')}</p>
            <p><span class="label">Customer Email:</span> {claim_data.get('email', 'N/A')}</p>
            <p><span class="label">Dispute Amount:</span> ${claim_data.get('amount', '0.00')}</p>
            <p><span class="label">Reason:</span> {claim_data.get('reason', 'Fraudulent / Unauthorized')}</p>
            <p><span class="label">Timestamp:</span> {claim_data.get('timestamp', 'N/A')}</p>
        </div>
    </body>
    </html>
    """
    
    HTML(string=html_content).write_pdf(output_path)
    return output_path