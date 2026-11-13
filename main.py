from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from email_service import send_notification_email

app = FastAPI(title="ChargeClaims Landing & API")

templates = Jinja2Templates(directory=".")

class DemoRequest(BaseModel):
    name: str
    email: str
    store_url: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/request-demo")
async def request_demo(demo: DemoRequest):
    print(f"[YENİ DEMO TALEBİ] İsim: {demo.name} | E-posta: {demo.email} | Mağaza: {demo.store_url}")
    send_notification_email(to_email=demo.email, dispute_id=f"DEMO-{demo.store_url}")
    return JSONResponse(
        status_code=200,
        content={"status": "success", "message": "Demo talebiniz alındı! En kısa sürede sizinle iletişime geçeceğiz."}
    )