from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import sqlite3
import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import pdf_generator
import shopify_api
from email_service import send_dispute_notification

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})