"""
==========================================================
CatLoaf AI Bakery
fetch_data.py

Temporary data source
Replace with live Pump.fun API later
==========================================================
"""

from typing import List, Dict


def fetch_launches() -> List[Dict]:

    launches = [

        {
            "name": "Loafy",
            "symbol": "LOAF",
            "price": 0.000021,
            "change24h": 48.6,
            "market_cap": 425000,
            "volume": 186000,
            "holders": 842,
            "age_hours": 4,
            "logo": "assets/logo.jpg",
            "url": "https://pump.fun"
        },

        {
            "name": "CatMint",
            "symbol": "MINT",
            "price": 0.000012,
            "change24h": 33.2,
            "market_cap": 780000,
            "volume": 241000,
            "holders": 1250,
            "age_hours": 8,
            "logo": "assets/logo.jpg",
            "url": "https://pump.fun"
        },

        {
            "name": "BreadDog",
            "symbol": "BDOG",
            "price": 0.000083,
            "change24h": 21.5,
            "market_cap": 1300000,
            "volume": 315000,
            "holders": 1815,
            "age_hours": 15,
            "logo": "assets/logo.jpg",
            "url": "https://pump.fun"
        },

        {
            "name": "KittyAI",
            "symbol": "KAI",
            "price": 0.000031,
            "change24h": 72.8,
            "market_cap": 380000,
            "volume": 420000,
            "holders": 973,
            "age_hours": 2,
            "logo": "assets/logo.jpg",
            "url": "https://pump.fun"
        },

        {
            "name": "ToastCoin",
            "symbol": "TOAST",
            "price": 0.000015,
            "change24h": 15.9,
            "market_cap": 2400000,
            "volume": 92000,
            "holders": 562,
            "age_hours": 20,
            "logo": "assets/logo.jpg",
            "url": "https://pump.fun"
        }

    ]

    return launches