"""
==========================================================
CatLoaf AI Bakery
AI Loaf Score Engine
==========================================================
"""


def calculate_loaf_score(coin):

    score = 50

    change = float(coin.get("change24h", 0))
    volume = float(coin.get("volume", 0))
    market_cap = float(coin.get("market_cap", 0))

    # Momentum
    if change >= 100:
        score += 25
    elif change >= 50:
        score += 18
    elif change >= 20:
        score += 12
    elif change >= 10:
        score += 6

    # Volume
    if volume >= 5_000_000:
        score += 20
    elif volume >= 1_000_000:
        score += 15
    elif volume >= 250_000:
        score += 10

    # Smaller caps receive a bonus
    if 1_000_000 <= market_cap <= 25_000_000:
        score += 15
    elif market_cap < 1_000_000:
        score += 8

    return min(100, round(score))