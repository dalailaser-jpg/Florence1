from fastapi import FastAPI, Depends, Form, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, User
from auth import hash_password, verify_password
from coinbase_api import test_coinbase_keys, get_assets_with_prices

# --- Initialisation de l'application ---
app = FastAPI()

# --- Montage du dossier static ---
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Templates HTML ---
templates = Jinja2Templates(directory="templates")

# --- Création des tables si inexistantes ---
Base.metadata.create_all(bind=engine)

# --- Connexion DB ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Page d'accueil ---
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# --- Inscription ---
@app.post("/register", response_class=HTMLResponse)
def register(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if db.query(User).filter_by(email=email).first():
        return templates.TemplateResponse("home.html", {"request": request, "msg": "❌ Email déjà enregistré."})
    db.add(User(email=email, password=hash_password(password)))
    db.commit()
    return templates.TemplateResponse("home.html", {"request": request, "msg": "✅ Inscription réussie."})

# --- Connexion ---
@app.post("/login", response_class=HTMLResponse)
def login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=email).first()
    if not user or not verify_password(password, user.password):
        return templates.TemplateResponse("home.html", {"request": request, "msg": "❌ Email ou mot de passe incorrect."})
    if not user.api_key or not user.api_secret or not test_coinbase_keys(user.api_key, user.api_secret):
        return templates.TemplateResponse("apikey.html", {"request": request, "email": email, "msg": "🔐 Entrez vos clés API Coinbase."})
    assets = get_assets_with_prices(user.api_key, user.api_secret)
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "assets": assets,
        "email": email,
        "user_id": user.id,
        "tracked_assets": (user.tracked_assets or "").split(","),
        "profit": user.target_profit_percent,
        "active": user.active_bot
    })

# --- Sauvegarde des clés API ---
@app.post("/apikey", response_class=HTMLResponse)
def save_apikey(request: Request, email: str = Form(...), api_key: str = Form(...), api_secret: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=email).first()
    if not user or not test_coinbase_keys(api_key, api_secret):
        return templates.TemplateResponse("apikey.html", {"request": request, "email": email, "msg": "❌ API Keys invalides."})
    user.api_key = api_key
    user.api_secret = api_secret
    db.commit()
    return login(request, email, user.password, db)

# --- Enregistrement des préférences utilisateur (robot) ---
@app.post("/settings", response_class=HTMLResponse)
def update_settings(request: Request,
                    email: str = Form(...),
                    tracked_assets: list[str] = Form([]),
                    profit: float = Form(...),
                    active: bool = Form(False),
                    db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=email).first()
    user.tracked_assets = ",".join(tracked_assets)
    user.target_profit_percent = profit
    user.active_bot = active
    db.commit()
    return login(request, email, user.password, db)
