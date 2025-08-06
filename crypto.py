from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from jose import jwt
from database import update_user_keys
from auth import get_current_user
from fastapi.templating import Jinja2Templates
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv()

router = APIRouter()
templates = Jinja2Templates(directory="templates")

FERNET_KEY = os.environ.get("FERNET_KEY")
fernet = Fernet(FERNET_KEY.encode())

@router.get("/add-keys")
async def get_keys_form(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("add_keys.html", {"request": request, "user": user})

@router.post("/add-keys")
async def submit_keys(
    request: Request,
    api_key: str = Form(...),
    api_secret: str = Form(...),
    user=Depends(get_current_user),
):
    encrypted_key = fernet.encrypt(api_key.encode()).decode()
    encrypted_secret = fernet.encrypt(api_secret.encode()).decode()
    update_user_keys(user["email"], encrypted_key, encrypted_secret)
    return RedirectResponse("/", status_code=302)
