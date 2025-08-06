import os
from dotenv import load_dotenv
from coinbase.rest import RESTClient

load_dotenv()

api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")

client = RESTClient(api_key=api_key, api_secret=api_secret)

try:
    profile = client.get_current_user()
    print("✅ Connexion réussie :")
    print(profile)
except Exception as e:
    print("❌ Erreur de connexion :", str(e))
