/**
 * ChargeClaims Consortium Fraud Shield Agent (shield.js)
 * Shopify Mağazaları için Otomatik Cihaz Parmak İzi (Device Fingerprinting) ve Risk Kontrolü Ajanı
 */
(function () {
    window.ChargeClaimsShield = {
        version: "2.0.0",
        backendUrl: "https://chargeclaims.com", // Canlı SaaS Domain Adresi

        // Tarayıcı ve Donanım özelliklerinden benzersiz cihaz parmak izi (fingerprint) üretir
        getDeviceFingerprint: function () {
            try {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                ctx.textBaseline = "top";
                ctx.font = "14px 'Arial'";
                ctx.fillText("ChargeClaims-Shield-Fingerprint", 2, 2);
                const canvasData = canvas.toDataURL();

                const rawData = [
                    navigator.userAgent,
                    navigator.language,
                    screen.colorDepth,
                    screen.width + 'x' + screen.height,
                    new Date().getTimezoneOffset(),
                    navigator.hardwareConcurrency || 'unknown',
                    canvasData
                ].join('|||');

                let hash = 0;
                for (let i = 0; i < rawData.length; i++) {
                    const char = rawData.charCodeAt(i);
                    hash = ((hash << 5) - hash) + char;
                    hash |= 0;
                }
                return 'fp_' + Math.abs(hash).toString(16) + '_' + Date.now().toString(36);
            } catch (e) {
                return 'fp_fallback_' + Math.random().toString(36).substring(2);
            }
        },

        // Shopify mağazasından sipariş/ödeme aşamasında risk sorgusu yapar
        checkRisk: async function (customerData = {}) {
            const fp = this.getDeviceFingerprint();
            const merchantDomain = window.location.hostname;

            const payload = {
                merchant_domain: merchantDomain,
                device_fingerprint: fp,
                customer_email: customerData.email || null,
                customer_phone: customerData.phone || null,
                order_amount: customerData.amount || 0.0
            };

            try {
                const response = await fetch(`${this.backendUrl}/api/fraud/check`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (response.ok) {
                    const result = await response.json();
                    console.log("[ChargeClaims Shield] Risk Assessed:", result);
                    return result; 
                    // Döndüğü yapı: { decision: "ALLOW" | "REVIEW" | "BLOCK", risk_score: 85, reasons: [...] }
                }
            } catch (err) {
                console.error("[ChargeClaims Shield] Network error during risk check:", err);
            }
            return { decision: "ALLOW", risk_score: 0, reasons: ["Shield bypass on network error"] };
        },

        // Sayfa yüklendiğinde arka planda sessizce cihazı kaydeder ve hız (velocity) kontrolünü tetikler
        init: function () {
            if (document.readyState === 'complete') {
                this.checkRisk();
            } else {
                window.addEventListener('load', () => {
                    this.checkRisk();
                });
            }
        }
    };

    // Ajanı otomatik başlat
    window.ChargeClaimsShield.init();
})();