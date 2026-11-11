from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import os

app = FastAPI()

# Templates dizininin doğru yolda olduğundan emin oluyoruz
templates = Jinja2Templates(directory="templates")

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})