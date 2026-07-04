"""
==========================================================
CatLoaf AI Bakery
scanner.py

Main Scanner Controller
==========================================================
"""

import json
from pathlib import Path

from fetch_data import fetch_launches
from loaf_score import calculate_loaf_score


OUTPUT_FILE = Path(__file__).parent / "scanner.json"

TOP_COINS = 5


def build_scanner():

    print("🍞 Starting CatLoaf Scanner...")

    launches = fetch_launches()

    ranked = []

    for coin in launches:

        coin["loaf_score"] = calculate_loaf_score(coin)

        ranked.append(coin)

    ranked.sort(
        key=lambda x: x["loaf_score"],
        reverse=True
    )

    top = ranked[:TOP_COINS]

    OUTPUT_FILE.write_text(
        json.dumps(top, indent=4)
    )

    print(f"✅ Saved {len(top)} projects")
    print(f"📄 {OUTPUT_FILE}")


if __name__ == "__main__":

    build_scanner()