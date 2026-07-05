"""
==========================================================
CatLoaf AI Bakery
fetch_data.py

Fetch live Solana token data using CoinGecko Demo API
==========================================================
"""

import os
import requests

from typing import List, Dict

API_KEY = os.getenv("COINGECKO_API_KEY")

BASE_URL = "https://api.coingecko.com/api/v3"

HEADERS = {
    "accept": "application/json",
    "x-cg-demo-api-key": API_KEY
}


def fetch_launches() -> List[Dict]:

    url = f"{BASE_URL}/coins/markets"

    params = {
        "vs_currency": "usd",
        "category": "solana-ecosystem",
        "order": "volume_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "24h"
    }

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            params=params,
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

    except Exception as e:

        print(f"❌ CoinGecko API Error: {e}")

        return []

    launches = []

    for coin in data:

        market_cap = coin.get("market_cap") or 0
        volume = coin.get("total_volume") or 0
        change = coin.get("price_change_percentage_24h") or 0

        # Skip huge established projects
        if market_cap > 50_000_000:
            continue

        # Skip inactive projects
        if volume < 25_000:
            continue

        # Skip negative momentum
        if change <= 0:
            continue

        launches.append({

            "name": coin.get("name", "Unknown"),

            "symbol": coin.get("symbol", "").upper(),

            "price": coin.get("current_price", 0),

            "change24h": change,

            "market_cap": market_cap,

            "volume": volume,

            "holders": 0,

            "age_hours": 0,

            "logo": coin.get("image", "assets/logo.jpg"),

            "url": f"https://www.coingecko.com/en/coins/{coin.get('id','')}"

        })

    launches.sort(

        key=lambda coin: (
            coin["change24h"] * 2 +
            (coin["volume"] / 100000)
        ),

        reverse=True

    )

    launches = launches[:20]

    print(f"✅ Retrieved {len(launches)} promising projects")

    return launches