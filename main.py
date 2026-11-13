import os
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime

# --- VERİTABANI BAĞLANTISI (SQLite) ---
DATABASE_URL = "sqlite:///./chargeclaims.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Demo Talep Veritabanı Modeli
class DemoRequestModel(Base):
    __tablename__ = "demo_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    store_url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# FastAPI Uygulaması
app = FastAPI(title="ChargeClaims Landing & API")
templates = Jinja2Templates(directory=".")
security = HTTPBasic()

# Admin Kimlik Bilgileri
ADMIN_USER = "admin"
ADMIN_PASS = "chargeclaims2026"

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != ADMIN_USER or credentials.password != ADMIN_PASS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz kullanıcı adı veya şifre",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Pydantic Şeması
class DemoRequestCreate(BaseModel):
    name: str
    email: str
    store_url: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ROTALAR ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request, "index.html", {})

@app.post("/api/request-demo")
async def request_demo(demo: DemoRequestCreate, db: Session = Depends(get_db)):
    new_request = DemoRequestModel(
        name=demo.name,
        email=demo.email,
        store_url=demo.store_url
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    
    print(f"[VERİTABANINA KAYDEDİLDİ] ID: {new_request.id} | İsim: {demo.name} | E-posta: {demo.email} | Mağaza: {demo.store_url}")
    
    return JSONResponse(
        status_code=200,
        content={"status": "success", "message": "Demo talebiniz başarıyla kaydedildi!"}
    )

# Şifreli Admin Paneli (Tıklanabilir Linkler ile Güncellendi)
@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request, db: Session = Depends(get_db), username: str = Depends(verify_admin)):
    requests_list = db.query(DemoRequestModel).order_by(DemoRequestModel.created_at.desc()).all()
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>ChargeClaims - Admin Paneli</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-950 text-white min-h-screen p-8">
        <div class="max-w-6xl mx-auto">
            <div class="flex justify-between items-center mb-8 border-b border-slate-800 pb-4">
                <h1 class="text-2xl font-bold text-emerald-400">ChargeClaims Admin - Demo Talepleri</h1>
                <div class="flex items-center gap-4">
                    <span class="text-sm text-slate-400">Hoş geldin, {username}</span>
                    <a href="/" target="_blank" class="bg-slate-800 hover:bg-slate-700 px-3 py-1.5 rounded-lg text-xs transition">Siteye Git &rarr;</a>
                </div>
            </div>
            
            <div class="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="border-b border-slate-800 text-slate-400 text-sm bg-slate-950/50">
                            <th class="p-4">ID</th>
                            <th class="p-4">Ad Soyad</th>
                            <th class="p-4">E-posta</th>
                            <th class="p-4">Mağaza URL / Bağlantı</th>
                            <th class="p-4">Tarih</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-800 text-sm">
    """
    
    if not requests_list:
        html_content += """
            <tr><td colspan="5" class="p-6 text-center text-slate-500">Henüz hiç demo talebi gelmemiş.</td></tr>
        """
    else:
        for req in requests_list:
            # URL kontrolü: http ile başlamıyorsa ekleyelim ki link düzgün çalışsın
            url_link = req.store_url if req.store_url.startswith("http") else f"https://{req.store_url}"
            
            html_content += f"""
                <tr class="hover:bg-slate-800/50 transition">
                    <td class="p-4 font-mono text-slate-400">#{req.id}</td>
                    <td class="p-4 font-semibold">{req.name}</td>
                    <td class="p-4 text-indigo-400"><a href="mailto:{req.email}" class="hover:underline">{req.email}</a></td>
                    <td class="p-4 max-w-xs truncate">
                        <a href="{url_link}" target="_blank" class="text-emerald-400 hover:underline flex items-center gap-1 font-mono text-xs">
                            {req.store_url} ↗
                        </a>
                    </td>
                    <td class="p-4 text-slate-500 text-xs">{req.created_at.strftime('%Y-%m-%d %H:%M')}</td>
                </tr>
            """
            
    html_content += """
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)