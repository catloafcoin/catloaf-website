"""
==========================================================
CatLoaf AI Bakery
loaf_score.py

AI Bakery Loaf Score
==========================================================
"""


def calculate_loaf_score(coin):

    score = 0

    change = float(coin.get("change24h", 0))
    volume = float(coin.get("volume", 0))
    market_cap = float(coin.get("market_cap", 0))

    # Momentum
    if change > 100:
        score += 40
    elif change > 50:
        score += 30
    elif change > 20:
        score += 20
    elif change > 5:
        score += 10

    # Trading Activity
    if volume > 5_000_000:
        score += 30
    elif volume > 1_000_000:
        score += 20
    elif volume > 100_000:
        score += 10

    # Prefer smaller projects
    if market_cap < 10_000_000:
        score += 30
    elif market_cap < 50_000_000:
        score += 20
    elif market_cap < 100_000_000:
        score += 10

    return min(score, 100)