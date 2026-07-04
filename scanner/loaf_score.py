"""
==========================================================
CatLoaf AI Bakery
loaf_score.py

Loaf Score Algorithm
==========================================================
"""


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def calculate_loaf_score(coin):
    """
    Calculate a CatLoaf Loaf Score (0-100)

    Current weights:

    📈 Momentum      30%
    💰 Volume        25%
    👥 Holders       20%
    ⚡ Market Cap    15%
    🕒 Freshness     10%

    """

    volume = coin.get("volume", 0)
    holders = coin.get("holders", 0)
    market_cap = coin.get("market_cap", 0)
    change = coin.get("change24h", 0)
    age = coin.get("age_hours", 24)

    # -----------------------------
    # Momentum
    # -----------------------------

    momentum_score = clamp(change, 0, 100)

    # -----------------------------
    # Volume
    # -----------------------------

    volume_score = clamp(volume / 10000, 0, 100)

    # -----------------------------
    # Holders
    # -----------------------------

    holder_score = clamp(holders / 20, 0, 100)

    # -----------------------------
    # Market Cap
    # Lower caps score higher
    # (better discovery potential)
    # -----------------------------

    if market_cap <= 0:

        market_score = 0

    elif market_cap <= 500000:

        market_score = 100

    elif market_cap <= 1000000:

        market_score = 80

    elif market_cap <= 3000000:

        market_score = 60

    elif market_cap <= 10000000:

        market_score = 40

    else:

        market_score = 20

    # -----------------------------
    # Freshness
    # -----------------------------

    freshness_score = clamp(
        100 - (age * 4),
        0,
        100
    )

    # -----------------------------
    # Final Loaf Score
    # -----------------------------

    loaf_score = (

        momentum_score * 0.30 +

        volume_score * 0.25 +

        holder_score * 0.20 +

        market_score * 0.15 +

        freshness_score * 0.10

    )

    return round(loaf_score, 1)