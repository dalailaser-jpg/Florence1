import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from database import SessionLocal
from models import APIKey

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupérer la clé Fernet
SECRET_KEY = os.getenv("FERNET_SECRET")
if not SECRET_KEY:
    raise ValueError("FERNET_SECRET est manquant dans le fichier .env")

fernet = Fernet(SECRET_KEY.encode())

def save_api_keys(user_id: int, api_key: str, api_secret: str):
    db = SessionLocal()
    encrypted_key = fernet.encrypt(api_key.encode()).decode()
    encrypted_secret = fernet.encrypt(api_secret.encode()).decode()
    existing = db.query(APIKey).filter(APIKey.user_id == user_id).first()
    if existing:
        existing.api_key_encrypted = encrypted_key
        existing.api_secret_encrypted = encrypted_secret
    else:
        new = APIKey(
            api_key_encrypted=encrypted_key,
            api_secret_encrypted=encrypted_secret,
            user_id=user_id
        )
        db.add(new)
    db.commit()

def get_api_keys(user_id: int):
    db = SessionLocal()
    entry = db.query(APIKey).filter(APIKey.user_id == user_id).first()
    if entry:
        return {
            "api_key": fernet.decrypt(entry.api_key_encrypted.encode()).decode(),
            "api_secret": fernet.decrypt(entry.api_secret_encrypted.encode()).decode()
        }
    return None
