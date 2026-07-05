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
    """
    Fetch live Solana ecosystem tokens from CoinGecko.
    """

    url = f"{BASE_URL}/coins/markets"

    params = {
        "vs_currency": "usd",
        "category": "solana-ecosystem",
        "order": "volume_desc",
        "per_page": 50,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "24h"
    }

    response = requests.get(

        url,

        headers=HEADERS,

        params=params,

        timeout=20

    )

    response.raise_for_status()

    data = response.json()

    launches = []

    for coin in data:

        launches.append({

            "name": coin.get("name", "Unknown"),

            "symbol": coin.get("symbol", "").upper(),

            "price": coin.get("current_price", 0),

            "change24h": coin.get("price_change_percentage_24h", 0) or 0,

            "market_cap": coin.get("market_cap", 0),

            "volume": coin.get("total_volume", 0),

            "holders": 0,

            "age_hours": 0,

            "logo": coin.get("image", "assets/logo.jpg"),

            "url": f"https://www.coingecko.com/en/coins/{coin.get('id','')}"

        })

    return launches
    # ==========================================
    # Filter promising projects
    # ==========================================

    launches = [

        coin

        for coin in launches

        if

        coin["market_cap"] > 100000

        and coin["market_cap"] < 50000000

        and coin["volume"] > 25000

        and coin["change24h"] > 0

    ]

    launches.sort(

        key=lambda x: (

            x["change24h"] * 2

            +

            (x["volume"] / 100000)

        ),

        reverse=True

    )

    launches = launches[:20]
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

        launches.append({

            "name": coin.get("name", "Unknown"),

            "symbol": coin.get("symbol", "").upper(),

            "price": coin.get("current_price", 0),

            "change24h": coin.get("price_change_percentage_24h", 0) or 0,

            "market_cap": coin.get("market_cap", 0),

            "volume": coin.get("total_volume", 0),

            "holders": 0,

            "age_hours": 0,

            "logo": coin.get("image", "assets/logo.jpg"),

            "url": f"https://www.coingecko.com/en/coins/{coin.get('id','')}"

        })

    print(f"✅ Retrieved {len(launches)} Solana projects")

    return launches