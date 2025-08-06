from coinbase.rest import RESTClient
import requests

def test_coinbase_keys(api_key: str, api_secret: str) -> bool:
    try:
        client = RESTClient(api_key=api_key, api_secret=api_secret)
        _ = client.get_accounts()
        return True
    except:
        return False

def get_usd_to_cad_rate() -> float:
    try:
        res = requests.get("https://api.exchangerate.host/latest?base=USD&symbols=CAD", timeout=5)
        rate = res.json()["rates"]["CAD"]
        return float(rate)
    except:
        return 1.35  # Valeur approximative par défaut

def get_assets_with_prices(api_key: str, api_secret: str):
    try:
        client = RESTClient(api_key=api_key, api_secret=api_secret)
        accounts = client.get_accounts().accounts
        products = {p.product_id: p for p in client.get_products().products}
        usd_to_cad = get_usd_to_cad_rate()
        assets = []

        for acc in accounts:
            try:
                balance = float(acc.available_balance["value"])
                symbol = acc.currency
                if symbol == "USDC" or balance == 0:
                    continue
                pair = f"{symbol}-USDC"
                if pair not in products:
                    continue
                ask = float(client.get_product_book(product_id=pair, limit=1).pricebook.asks[0].price)
                usd_value = balance * ask
                if usd_value < 1:
                    continue
                assets.append({
                    "currency": symbol,
                    "balance": round(balance, 6),
                    "price_usd": round(ask, 4),
                    "price_cad": round(ask * usd_to_cad, 4),
                    "usd_value": round(usd_value, 2),
                    "cad_value": round(usd_value * usd_to_cad, 2)
                })
            except:
                continue
        return assets
    except Exception as e:
        return {"error": str(e)}
