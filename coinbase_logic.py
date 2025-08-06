from coinbase.rest import RESTClient
import requests

def fetch_current_prices(api_key: str, api_secret: str) -> dict:
    client = RESTClient(api_key, api_secret)
    accounts = client.list_accounts()
    prices = {}
    for acc in accounts:
        if acc['available_balance'] and acc['available_balance']['value']:
            symbol = acc['currency']
            if symbol == 'USDC':
                continue
            try:
                product = f"{symbol}-USDC"
                ticker = client.get_product(product)
                prices[symbol] = float(ticker['price'])
            except:
                continue
    return prices


def get_coinbase_balances_usd_cad(api_key: str, api_secret: str, initial_prices: dict):
    client = RESTClient(api_key, api_secret)
    response = requests.get("https://open.er-api.com/v6/latest/USD")
    usd_to_cad = response.json()["rates"]["CAD"]

    balances = []
    accounts = client.list_accounts()
    for acc in accounts:
        currency = acc['currency']
        if acc['available_balance'] and acc['available_balance']['value']:
            amount = float(acc['available_balance']['value'])
            if currency == 'USDC':
                usd_value = amount
                cad_value = usd_value * usd_to_cad
                balances.append({
                    "symbol": currency,
                    "amount": amount,
                    "usd": usd_value,
                    "cad": cad_value,
                    "change": "0.00 %"
                })
                continue
            try:
                product = f"{currency}-USDC"
                ticker = client.get_product(product)
                current_price = float(ticker['price'])
                usd_value = current_price * amount
                cad_value = usd_value * usd_to_cad
                price_initial = initial_prices.get(currency, current_price)
                variation = ((current_price - price_initial) / price_initial) * 100
                balances.append({
                    "symbol": currency,
                    "amount": amount,
                    "usd": usd_value,
                    "cad": cad_value,
                    "change": f"{variation:.2f} %"
                })
            except:
                continue
    return balances
