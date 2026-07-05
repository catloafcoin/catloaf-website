"""
==========================================================
CatLoaf AI Bakery
bakery_ai.py

Generate AI Bakery Verdicts
==========================================================
"""


def generate_ai_verdict(coin):

    score = coin.get("loaf_score", 0)
    change = coin.get("change24h", 0)
    volume = coin.get("volume", 0)
    market_cap = coin.get("market_cap", 0)

    # ------------------------
    # Momentum
    # ------------------------

    if change >= 50:
        momentum = "Explosive 🚀"

    elif change >= 20:
        momentum = "Strong 📈"

    elif change >= 5:
        momentum = "Building 🌱"

    else:
        momentum = "Weak 😴"

    # ------------------------
    # Risk
    # ------------------------

    if market_cap < 1_000_000:
        risk = "High ⚠️"

    elif market_cap < 10_000_000:
        risk = "Medium"

    else:
        risk = "Low"

    # ------------------------
    # Opportunity
    # ------------------------

    if score >= 90:
        opportunity = "Exceptional 🍞"

    elif score >= 80:
        opportunity = "Excellent"

    elif score >= 70:
        opportunity = "High"

    elif score >= 60:
        opportunity = "Moderate"

    else:
        opportunity = "Low"

    # ------------------------
    # Bakery Verdict
    # ------------------------

    if score >= 90:

        verdict = (
            "Fresh out of the oven. "
            "Exceptional momentum with strong market activity."
        )

    elif score >= 80:

        verdict = (
            "Healthy momentum backed by good trading activity."
        )

    elif score >= 70:

        verdict = (
            "Worth monitoring as momentum continues to build."
        )

    elif score >= 60:

        verdict = (
            "Some positive signs, but confirmation is still needed."
        )

    else:

        verdict = (
            "Currently lacks strong momentum. Monitor before considering."
        )

    return {

        "momentum": momentum,

        "risk": risk,

        "opportunity": opportunity,

        "verdict": verdict

    }