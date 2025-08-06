# app/routes/api_test.py

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates
from coinbase.rest import RESTClient
import os
from app.database import get_db
from app.models import User
from app.auth import get_current_user
from app.utils.encryption import decrypt_api_key

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()

@router.get("/test-api", response_class=HTMLResponse)
def test_api(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.api_key_encrypted or not current_user.api_secret_encrypted:
        return templates.TemplateResponse("api_test.html", {
            "request": request,
            "status": "❌ Clés API manquantes",
            "details": "Vous devez d'abord enregistrer vos clés API dans votre compte."
        })

    try:
        api_key = decrypt_api_key(current_user.api_key_encrypted)
        api_secret = decrypt_api_key(current_user.api_secret_encrypted)

        client = RESTClient(api_key=api_key, api_secret=api_secret)
        response = client.list_accounts()

        return templates.TemplateResponse("api_test.html", {
            "request": request,
            "status": "✅ Connexion réussie",
            "details": f"{len(response.accounts)} comptes trouvés sur Coinbase."
        })

    except Exception as e:
        return templates.TemplateResponse("api_test.html", {
            "request": request,
            "status": "❌ Erreur de connexion",
            "details": str(e)
        })
