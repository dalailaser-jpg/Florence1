from coinbase.rest import RESTClient as CoinbaseAdvancedTradeClient

def get_coinbase_accounts(api_key: str, api_secret: str):
    try:
        client = CoinbaseAdvancedTradeClient(api_key=api_key, api_secret=api_secret)
        response = client.list_accounts()
        accounts = []

        for account in response.get("accounts", []):
            accounts.append({
                "name": account.get("name", ""),
                "currency": account.get("currency", ""),
                "available_balance": account.get("available_balance", {}).get("value", "0.00")
            })

        return accounts
    except Exception as e:
        print("Erreur API Coinbase :", str(e))
        return None
