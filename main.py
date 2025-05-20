from fastapi import FastAPI, HTTPException, Query
import httpx

app = FastAPI(title="Crypto Info API")

COINGECKO_API = "https://api.coingecko.com/api/v3"


@app.get("/crypto")
async def get_crypto_stats(query: str = Query(..., description="Name or symbol of cryptocurrency")):
    async with httpx.AsyncClient() as client:
        coins_resp = await client.get(f"{COINGECKO_API}/coins/list")
        if coins_resp.status_code != 200:
            raise HTTPException(status_code=502, detail="Failed to fetch crypto information.")
        coins = coins_resp.json()

        query_lower = query.lower()
        match = next((coin for coin in coins if coin["id"] == query_lower or
                      coin["symbol"] == query_lower or coin["name"].lower() == query_lower), None)

        if not match:
            raise HTTPException(status_code=404, detail="Cryptocurrency not found.")

        coin_id = match["id"]

        market_resp = await client.get(f"{COINGECKO_API}/coins/markets", params={
            "vs_currency": "usd",
            "ids": coin_id
        })
        if market_resp.status_code != 200:
            raise HTTPException(status_code=502, detail="Failed to fetch market data.")

        data = market_resp.json()
        if not data:
            raise HTTPException(status_code=404, detail="Market data not available.")

        coin_data = data[0]
        return {
            "name": coin_data["name"],
            "symbol": coin_data["symbol"],
            "current_price": coin_data["current_price"],
            "price_change_percentage_24h": coin_data["price_change_percentage_24h"],
            "volume_24h": coin_data["total_volume"],
            "market_cap": coin_data["market_cap"],
            "last_updated": coin_data["last_updated"]
        }

# Go to http://127.0.0.1:8000/docs to test
