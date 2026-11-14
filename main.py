import hashlib
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# ---------------------------------------------------------
# 1. VERİTABANI YAPILANDIRMASI (SQLite + SQLAlchemy)
# ---------------------------------------------------------
DATABASE_URL = "sqlite:///./chargeclaims.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ---------------------------------------------------------
# 2. VERİTABANI TABLOLARI (MODELLER)
# ---------------------------------------------------------
class DemoRequest(Base):
    __tablename__ = "demo_requests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    store_url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class FraudSignal(Base):
    """Ortak Ağ (Consortium) Dolandırıcılık Sinyalleri Havuzu"""
    __tablename__ = "fraud_signals"

    id = Column(Integer, primary_key=True, index=True)
    merchant_domain = Column(String, index=True, nullable=False)
    ip_address = Column(String, index=True, nullable=True)
    device_fingerprint = Column(String, index=True, nullable=True)
    email_hash = Column(String, index=True, nullable=True)
    phone_hash = Column(String, index=True, nullable=True)
    reason = Column(String, nullable=False)  # Örn: CHARGEBACK, COD_REFUSAL, VELOCITY_ABUSE
    risk_score = Column(Integer, default=85)  # 0 - 100 arası
    created_at = Column(DateTime, default=datetime.utcnow)


class CheckoutCheckLog(Base):
    """Mağazalardan gelen anlık sipariş risk sorguları ve hız (velocity) takibi"""
    __tablename__ = "checkout_check_logs"

    id = Column(Integer, primary_key=True, index=True)
    merchant_domain = Column(String, index=True, nullable=False)
    ip_address = Column(String, index=True, nullable=True)
    device_fingerprint = Column(String, index=True, nullable=True)
    email_hash = Column(String, index=True, nullable=True)
    risk_score = Column(Integer, default=0)
    decision = Column(String, nullable=False)  # ALLOW, REVIEW, BLOCK
    checked_at = Column(DateTime, default=datetime.utcnow)


# Tabloları otomatik oluştur
Base.metadata.create_all(bind=engine)


# ---------------------------------------------------------
# 3. FASTAPI UYGULAMASI VE GÜVENLİK AYARLARI
# ---------------------------------------------------------
app = FastAPI(
    title="ChargeClaims API & Consortium Fraud Shield",
    version="2.0.0"
)

# Shopify mağazalarının farklı domainlerden API'ye erişebilmesi için CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_identifier(value: Optional[str]) -> Optional[str]:
    """E-posta ve telefon gibi kişisel verileri SHA-256 ile anonimleştirir."""
    if not value:
        return None
    clean_val = value.strip().lower()
    return hashlib.sha256(clean_val.encode("utf-8")).hexdigest()


# ---------------------------------------------------------
# 4. PYDANTIC VERİ ŞEMALARI (REQUEST / RESPONSE)
# ---------------------------------------------------------
class DemoCreate(BaseModel):
    name: str
    email: str
    store_url: str


class FraudReportCreate(BaseModel):
    merchant_domain: str
    ip_address: Optional[str] = None
    device_fingerprint: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    reason: str = "CHARGEBACK"
    risk_score: int = 90


class RiskCheckRequest(BaseModel):
    merchant_domain: str
    ip_address: Optional[str] = None
    device_fingerprint: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    order_amount: Optional[float] = 0.0


# ---------------------------------------------------------
# 5. SAYFA VE AJAN SCRIPT ROTALARI
# ---------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def serve_home():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        headers = {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        }
        return HTMLResponse(content=html_content, headers=headers)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>index.html bulunamadi</h1>", status_code=404)


@app.get("/shield.js", response_class=PlainTextResponse)
async def serve_shield_script():
    """Shopify mağazalarının tema içine tek satırla ekleyeceği JavaScript ajan dosyası"""
    try:
        with open("shield.js", "r", encoding="utf-8") as f:
            js_content = f.read()
        headers = {
            "Cache-Control": "public, max-age=3600",
            "Content-Type": "application/javascript; charset=utf-8"
        }
        return PlainTextResponse(content=js_content, headers=headers)
    except FileNotFoundError:
        return PlainTextResponse(content="console.error('ChargeClaims Shield script not found.');", status_code=404, media_type="application/javascript")


@app.get("/admin", response_class=HTMLResponse)
async def serve_admin(db: Session = Depends(get_db)):
    demos = db.query(DemoRequest).order_by(DemoRequest.created_at.desc()).all()
    signals = db.query(FraudSignal).order_by(FraudSignal.created_at.desc()).limit(50).all()
    checks = db.query(CheckoutCheckLog).order_by(CheckoutCheckLog.checked_at.desc()).limit(50).all()

    demo_rows = "".join([
        f"<tr class='border-b border-slate-800'><td class='p-3'>{d.id}</td><td class='p-3 font-semibold text-white'>{d.name}</td><td class='p-3 text-indigo-400'>{d.email}</td><td class='p-3 text-emerald-400'>{d.store_url}</td><td class='p-3 text-slate-400 text-xs'>{d.created_at.strftime('%Y-%m-%d %H:%M')}</td></tr>"
        for d in demos
    ])

    signal_rows = "".join([
        f"<tr class='border-b border-slate-800'><td class='p-3 text-xs'>{s.merchant_domain}</td><td class='p-3 font-mono text-xs text-amber-400'>{s.ip_address or '-'}</td><td class='p-3 font-mono text-xs text-slate-400'>{(s.device_fingerprint[:12] + '...') if s.device_fingerprint else '-'}</td><td class='p-3'><span class='px-2 py-1 rounded bg-red-500/20 text-red-400 text-xs font-bold'>{s.reason}</span></td><td class='p-3 font-bold text-red-400'>{s.risk_score}/100</td></tr>"
        for s in signals
    ])

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>ChargeClaims - Admin & Fraud Intelligence Portal</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-950 text-slate-200 p-8 font-sans">
        <div class="max-w-6xl mx-auto space-y-10">
            <div class="flex justify-between items-center border-b border-slate-800 pb-4">
                <div>
                    <h1 class="text-2xl font-extrabold text-emerald-400">ChargeClaims Admin Portal</h1>
                    <p class="text-xs text-slate-400">Demo Leads & Consortium Fraud Shield Monitor</p>
                </div>
                <a href="/" class="bg-slate-800 hover:bg-slate-700 px-4 py-2 rounded-lg text-xs font-semibold">Back to Website</a>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div class="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
                    <div class="text-xs text-slate-400 uppercase">Total Demo Leads</div>
                    <div class="text-3xl font-extrabold text-white mt-2">{len(demos)}</div>
                </div>
                <div class="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
                    <div class="text-xs text-slate-400 uppercase">Consortium Fraud Signals</div>
                    <div class="text-3xl font-extrabold text-red-400 mt-2">{len(signals)}</div>
                </div>
                <div class="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
                    <div class="text-xs text-slate-400 uppercase">Live Risk Checks Logged</div>
                    <div class="text-3xl font-extrabold text-indigo-400 mt-2">{len(checks)}</div>
                </div>
            </div>

            <div class="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
                <div class="p-4 border-b border-slate-800 font-bold text-white">Recent Demo & Trial Requests</div>
                <table class="w-full text-left text-sm">
                    <thead class="bg-slate-950 text-slate-400 text-xs uppercase">
                        <tr><th class="p-3">ID</th><th class="p-3">Name</th><th class="p-3">Email</th><th class="p-3">Store URL</th><th class="p-3">Date</th></tr>
                    </thead>
                    <tbody>{demo_rows or "<tr><td colspan='5' class='p-4 text-center text-slate-500'>No requests yet.</td></tr>"}</tbody>
                </table>
            </div>

            <div class="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
                <div class="p-4 border-b border-slate-800 font-bold text-white flex justify-between items-center">
                    <span>Cross-Merchant Fraud Shield Signals</span>
                    <span class="text-xs text-emerald-400 font-normal">Live Consortium Database</span>
                </div>
                <table class="w-full text-left text-sm">
                    <thead class="bg-slate-950 text-slate-400 text-xs uppercase">
                        <tr><th class="p-3">Reported By</th><th class="p-3">IP Address</th><th class="p-3">Device ID</th><th class="p-3">Reason</th><th class="p-3">Risk Score</th></tr>
                    </thead>
                    <tbody>{signal_rows or "<tr><td colspan='5' class='p-4 text-center text-slate-500'>No fraud signals reported yet.</td></tr>"}</tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


# ---------------------------------------------------------
# 6. API UÇ NOKTALARI (ENDPOINTS)
# ---------------------------------------------------------
@app.post("/api/request-demo")
async def create_demo_request(payload: DemoCreate, db: Session = Depends(get_db)):
    new_demo = DemoRequest(
        name=payload.name,
        email=payload.email,
        store_url=payload.store_url
    )
    db.add(new_demo)
    db.commit()
    db.refresh(new_demo)
    return {"status": "success", "id": new_demo.id}


@app.post("/api/fraud/report")
async def report_fraud_signal(payload: FraudReportCreate, db: Session = Depends(get_db)):
    """Bir mağazada chargeback veya kapıda ödeme iadesi yapan kişiyi ortak ağa bildirir."""
    signal = FraudSignal(
        merchant_domain=payload.merchant_domain.strip().lower(),
        ip_address=payload.ip_address.strip() if payload.ip_address else None,
        device_fingerprint=payload.device_fingerprint.strip() if payload.device_fingerprint else None,
        email_hash=hash_identifier(payload.customer_email),
        phone_hash=hash_identifier(payload.customer_phone),
        reason=payload.reason.upper(),
        risk_score=payload.risk_score
    )
    db.add(signal)
    db.commit()
    db.refresh(signal)
    return {
        "status": "reported",
        "signal_id": signal.id,
        "message": "Fraud signal added to ChargeClaims Consortium Network."
    }


@app.post("/api/fraud/check")
async def check_checkout_risk(payload: RiskCheckRequest, request: Request, db: Session = Depends(get_db)):
    """
    Shopify mağazasından sipariş anında çağrılır.
    1. Ortak ağda (FraudSignal) daha önce kayıtlı bir vaka var mı kontrol eder.
    2. Son 24 saat içinde farklı mağazalarda seri deneme (Velocity Attack) var mı kontrol eder.
    """
    client_ip = payload.ip_address or (request.client.host if request.client else None)
    fp = payload.device_fingerprint.strip() if payload.device_fingerprint else None
    e_hash = hash_identifier(payload.customer_email)
    p_hash = hash_identifier(payload.customer_phone)
    merchant = payload.merchant_domain.strip().lower()

    risk_score = 0
    reasons = []

    # A) Ortak Ağ Kara Liste / Geçmiş Vaka Kontrolü
    matched_signals = []
    if client_ip:
        ip_hits = db.query(FraudSignal).filter(FraudSignal.ip_address == client_ip).all()
        matched_signals.extend(ip_hits)
    if fp:
        fp_hits = db.query(FraudSignal).filter(FraudSignal.device_fingerprint == fp).all()
        matched_signals.extend(fp_hits)
    if e_hash:
        email_hits = db.query(FraudSignal).filter(FraudSignal.email_hash == e_hash).all()
        matched_signals.extend(email_hits)
    if p_hash:
        phone_hits = db.query(FraudSignal).filter(FraudSignal.phone_hash == p_hash).all()
        matched_signals.extend(phone_hits)

    unique_signals = {s.id: s for s in matched_signals}.values()

    if unique_signals:
        max_past_score = max(s.risk_score for s in unique_signals)
        risk_score = max(risk_score, max_past_score)
        past_reasons = list(set(s.reason for s in unique_signals))
        reasons.append(f"Consortium Match ({len(unique_signals)} prior incidents: {', '.join(past_reasons)})")

    # B) Hız Kontrolü (Velocity Check - Son 24 saatte kaç farklı mağazada görüldü?)
    last_24h = datetime.utcnow() - timedelta(hours=24)
    recent_merchants = set()

    if client_ip:
        recent_ip_logs = db.query(CheckoutCheckLog).filter(
            CheckoutCheckLog.ip_address == client_ip,
            CheckoutCheckLog.checked_at >= last_24h
        ).all()
        for log in recent_ip_logs:
            recent_merchants.add(log.merchant_domain)

    if fp:
        recent_fp_logs = db.query(CheckoutCheckLog).filter(
            CheckoutCheckLog.device_fingerprint == fp,
            CheckoutCheckLog.checked_at >= last_24h
        ).all()
        for log in recent_fp_logs:
            recent_merchants.add(log.merchant_domain)

    recent_merchants.add(merchant)

    if len(recent_merchants) >= 3:
        risk_score = max(risk_score, 85)
        reasons.append(f"High Cross-Store Velocity ({len(recent_merchants)} stores in 24h)")
    elif len(recent_merchants) == 2:
        risk_score = max(risk_score, 45)
        reasons.append("Multi-Store Activity (2 stores in 24h)")

    # C) Karar Mekanizması
    if risk_score >= 75:
        decision = "BLOCK"
    elif risk_score >= 40:
        decision = "REVIEW"
    else:
        decision = "ALLOW"

    check_log = CheckoutCheckLog(
        merchant_domain=merchant,
        ip_address=client_ip,
        device_fingerprint=fp,
        email_hash=e_hash,
        risk_score=risk_score,
        decision=decision
    )
    db.add(check_log)
    db.commit()

    return {
        "decision": decision,
        "risk_score": risk_score,
        "reasons": reasons if reasons else ["Clean profile across ChargeClaims Network"],
        "network_checked": True
    }