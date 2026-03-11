import random
from datetime import datetime, timedelta
from typing import List

COMMODITIES = ["mil", "sorgho", "arachide", "maïs", "riz", "niébé", "coton", "manioc"]
MARKETS = {
    "Dakar": {"lat": 14.72, "lon": -17.47, "region": "Dakar"},
    "Thiès": {"lat": 14.79, "lon": -16.93, "region": "Thiès"},
    "Kaolack": {"lat": 14.15, "lon": -16.08, "region": "Kaolack"},
    "Ziguinchor": {"lat": 12.56, "lon": -16.27, "region": "Ziguinchor"},
    "Saint-Louis": {"lat": 16.02, "lon": -16.49, "region": "Saint-Louis"},
    "Tambacounda": {"lat": 13.77, "lon": -13.67, "region": "Tambacounda"},
    "Touba": {"lat": 14.85, "lon": -15.88, "region": "Diourbel"},
    "Louga": {"lat": 15.62, "lon": -16.22, "region": "Louga"},
}

BASE_PRICES = {
    "mil": 175,
    "sorgho": 160,
    "arachide": 320,
    "maïs": 185,
    "riz": 420,
    "niébé": 510,
    "coton": 265,
    "manioc": 90,
}


def get_current_prices(commodity: str = None, region: str = None) -> List[dict]:
    results = []
    commodities = [commodity] if commodity else COMMODITIES
    markets = {k: v for k, v in MARKETS.items() if not region or v["region"] == region}

    for market_name, market_info in markets.items():
        for c in commodities:
            base = BASE_PRICES.get(c, 200)
            seasonal_factor = 1 + 0.15 * random.uniform(-1, 1)
            regional_factor = 1 + 0.08 * random.uniform(-1, 1)
            price = round(base * seasonal_factor * regional_factor, 0)
            results.append({
                "commodity": c,
                "market_name": market_name,
                "region": market_info["region"],
                "price_per_kg": price,
                "currency": "XOF",
                "unit": "kg",
                "price_per_tonne": price * 1000,
                "recorded_at": datetime.utcnow().isoformat(),
            })
    return results


def get_price_history(commodity: str, region: str = None, days: int = 30) -> List[dict]:
    base = BASE_PRICES.get(commodity, 200)
    history = []
    price = base
    for i in range(days, 0, -1):
        date = datetime.utcnow() - timedelta(days=i)
        change = random.uniform(-0.03, 0.04)
        price = round(price * (1 + change), 0)
        price = max(base * 0.7, min(base * 1.5, price))
        history.append({
            "date": date.strftime("%Y-%m-%d"),
            "price_per_kg": price,
            "commodity": commodity,
            "region": region or "Sénégal",
        })
    return history


def get_market_trends(commodity: str) -> dict:
    base = BASE_PRICES.get(commodity, 200)
    current = base * (1 + random.uniform(-0.1, 0.15))
    month_ago = base * (1 + random.uniform(-0.15, 0.1))
    change_pct = round((current - month_ago) / month_ago * 100, 2)

    demand = random.choice(["low", "normal", "normal", "high"])
    supply = random.choice(["low", "normal", "normal", "high"])

    forecast_7d = current * (1 + random.uniform(-0.05, 0.08))
    forecast_30d = current * (1 + random.uniform(-0.1, 0.15))

    if demand == "high" and supply == "low":
        analysis = f"Forte demande et faible offre de {commodity} — prix à la hausse prévus."
    elif demand == "low" and supply == "high":
        analysis = f"Surproduction de {commodity} — pression baissière sur les prix."
    else:
        analysis = f"Marché du {commodity} équilibré — prix stables à court terme."

    return {
        "commodity": commodity,
        "avg_price": round(current, 0),
        "min_price": round(current * 0.85, 0),
        "max_price": round(current * 1.15, 0),
        "price_change_pct": change_pct,
        "demand_level": demand,
        "supply_level": supply,
        "forecast_7d": round(forecast_7d, 0),
        "forecast_30d": round(forecast_30d, 0),
        "analysis": analysis,
        "best_selling_markets": _get_best_markets(commodity),
    }


def _get_best_markets(commodity: str) -> List[dict]:
    base = BASE_PRICES.get(commodity, 200)
    markets = list(MARKETS.keys())
    random.shuffle(markets)
    return [
        {
            "market": m,
            "region": MARKETS[m]["region"],
            "price_per_kg": round(base * (1 + random.uniform(0.05, 0.25)), 0),
        }
        for m in markets[:3]
    ]


def get_trade_opportunities() -> List[dict]:
    opportunities = []
    for commodity in COMMODITIES:
        base = BASE_PRICES[commodity]
        source_price = round(base * random.uniform(0.8, 0.95), 0)
        dest_price = round(base * random.uniform(1.05, 1.35), 0)
        margin = round((dest_price - source_price) / source_price * 100, 1)
        if margin > 10:
            markets = list(MARKETS.keys())
            src, dst = random.sample(markets, 2)
            opportunities.append({
                "commodity": commodity,
                "source_region": MARKETS[src]["region"],
                "destination_region": MARKETS[dst]["region"],
                "source_price": source_price,
                "destination_price": dest_price,
                "margin_pct": margin,
                "estimated_volume_tons": round(random.uniform(5, 100), 1),
                "opportunity_score": min(100, round(margin * 3, 1)),
            })
    return sorted(opportunities, key=lambda x: x["opportunity_score"], reverse=True)
