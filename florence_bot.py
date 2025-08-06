# florence_bot.py
import time
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import User
from coinbase.rest import RESTClient
from coinbase_api import get_assets_with_prices

CHECK_INTERVAL = 15  # en secondes

def get_client(user: User):
    return RESTClient(api_key=user.api_key, api_secret=user.api_secret)

def sell_asset(client: RESTClient, currency: str, amount: float):
    try:
        product_id = f"{currency}-USDC"
        print(f"[📉] Vente de {amount} {currency} via {product_id}")
        response = client.create_order(
            product_id=product_id,
            side="SELL",
            client_order_id=None,
            order_configuration={
                "market_market_ioc": {
                    "base_size": str(round(amount, 8))
                }
            }
        )
        if response.success:
            print(f"✅ {currency} vendu avec succès.")
        else:
            print(f"❌ Échec vente {currency} : {response.__dict__}")
    except Exception as e:
        print(f"❌ Erreur API lors de la vente de {currency} : {e}")

def bot_loop():
    print("🚀 Démarrage du robot Florence1...\n")
    while True:
        db: Session = SessionLocal()
        users = db.query(User).filter_by(active_bot=True).all()

        for user in users:
            print(f"👤 Vérification pour {user.email}...")
            try:
                client = get_client(user)
                tracked = (user.tracked_assets or "").split(",")
                target = user.target_profit_percent or 10.0

                assets = get_assets_with_prices(user.api_key, user.api_secret)
                for asset in assets:
                    if asset["currency"] not in tracked:
                        continue
                    buy_price = None  # À implémenter : historique des prix d'achat
                    current_price = asset["price_usd"]
                    # Simulons qu'on a acheté à 90% du prix actuel :
                    buy_price = current_price / (1 + target / 100.0)

                    gain = ((current_price - buy_price) / buy_price) * 100
                    print(f"{asset['currency']}: {gain:.2f}% de gain simulé")

                    if gain >= target:
                        sell_asset(client, asset["currency"], asset["balance"])

            except Exception as e:
                print(f"⚠️ Erreur pour {user.email} : {e}")

        db.close()
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    bot_loop()