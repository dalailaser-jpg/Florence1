from coinbase.rest import RESTClient

# Remplace par tes vraies clés Coinbase API
API_KEY = "organizations/c8371f73-7c6e-4858-881d-0beeccb4fb95/apiKeys/60ccbab3-cb54-4d51-9e24-5e1070b901b5"
API_SECRET = "-----BEGIN EC PRIVATE KEY-----\nMHcCAQEEILQyR1DdVFwTzQ1/Qrx/E03CAWAkhxu4LyvRoAR3dWHQoAoGCCqGSM49\nAwEHoUQDQgAEzzkLuHj2IRcILOVZ2gy30GLLJAjoVoPqaHLxHhJq8lTC5qIqYhxp\nUgpGAGX66GZvuuKjQAFwDyJW98DNfArznw==\n-----END EC PRIVATE KEY-----\n"

client = RESTClient(api_key=API_KEY, api_secret=API_SECRET)

try:
    response = client.get_accounts()
    print("✅ Connexion réussie. Comptes disponibles :")
    for account in response.accounts:
        currency = account.currency
        balance = account.available_balance["value"]  # ← correction ici
        print(f"- {currency}: {balance}")
except Exception as e:
    print("❌ Erreur :")
    print(e)
