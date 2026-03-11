import random
from datetime import datetime, timedelta
from typing import List

# ─── Cultures principales de Guinée ────────────────────────────────────────────
# Basse-Guinée  : riz paddy, manioc, banane plantain, huile de palme, ananas
# Moyenne-Guinée: fonio, maïs, pomme de terre, bétail
# Haute-Guinée  : maïs, riz, arachide, sorgho, coton, mangue
# Guinée Forest.: riz, café Robusta, cacao, palmier, igname
COMMODITIES = ["riz", "manioc", "fonio", "maïs", "arachide", "banane_plantain", "café", "huile_de_palme"]

# ─── Marchés principaux de Guinée (12 marchés, 4 régions naturelles) ───────────
MARKETS = {
    "Conakry (Madina)":    {"lat":  9.55, "lon": -13.68, "region": "Basse-Guinée"},
    "Conakry (Cosa)":      {"lat":  9.56, "lon": -13.66, "region": "Basse-Guinée"},
    "Kindia":               {"lat": 10.05, "lon": -12.87, "region": "Basse-Guinée"},
    "Boké":                 {"lat": 10.93, "lon": -14.30, "region": "Basse-Guinée"},
    "Labé":                 {"lat": 11.32, "lon": -12.29, "region": "Moyenne-Guinée"},
    "Mamou":                {"lat": 10.38, "lon": -12.08, "region": "Moyenne-Guinée"},
    "Kankan":               {"lat": 10.39, "lon":  -9.31, "region": "Haute-Guinée"},
    "Faranah":              {"lat": 10.04, "lon": -10.74, "region": "Haute-Guinée"},
    "Siguiri":              {"lat": 11.42, "lon":  -9.17, "region": "Haute-Guinée"},
    "N'Zérékoré":          {"lat":  7.75, "lon":  -8.82, "region": "Guinée Forestière"},
    "Guéckédou":           {"lat":  8.55, "lon": -10.13, "region": "Guinée Forestière"},
    "Macenta":              {"lat":  8.55, "lon":  -9.47, "region": "Guinée Forestière"},
}

# ─── Prix de base en Franc Guinéen (GNF) / kg ──────────────────────────────────
# Source : FAO GIEWS, ANASA Guinée, enquêtes marchés 2024
# Taux de change indicatif : 1 EUR ≈ 9 400 GNF | 1 USD ≈ 8 600 GNF
BASE_PRICES = {
    "riz":              13_500,   # riz local paddy transformé
    "manioc":            2_500,   # tubercule frais
    "fonio":            18_000,   # fonio décortiqué — spécialité Moyenne-Guinée
    "maïs":              6_500,
    "arachide":         14_000,   # arachide coque
    "banane_plantain":   4_000,   # prix au régime (GNF/kg)
    "café":             45_000,   # café Robusta Guinée Forestière
    "huile_de_palme":   18_000,   # huile brute
}

EXCHANGE_RATE_EUR = 9_400


def get_current_prices(commodity: str = None, region: str = None) -> List[dict]:
    results = []
    commodities = [commodity] if commodity else COMMODITIES
    markets = {k: v for k, v in MARKETS.items() if not region or v["region"] == region}

    for market_name, market_info in markets.items():
        for c in commodities:
            base = BASE_PRICES.get(c, 10_000)
            # Conakry : surcoût intermédiaires + transport (~13%)
            city_factor = 1.13 if "Conakry" in market_name else 1.0
            seasonal_factor = 1 + 0.22 * random.uniform(-1, 1)
            price = round(base * city_factor * seasonal_factor / 100) * 100
            results.append({
                "commodity": c,
                "market_name": market_name,
                "region": market_info["region"],
                "price_per_kg": price,
                "currency": "GNF",
                "unit": "kg",
                "price_per_tonne": price * 1000,
                "price_eur_kg": round(price / EXCHANGE_RATE_EUR, 3),
                "recorded_at": datetime.utcnow().isoformat(),
            })
    return results


def get_price_history(commodity: str, region: str = None, days: int = 30) -> List[dict]:
    base = BASE_PRICES.get(commodity, 10_000)
    history = []
    price = base
    for i in range(days, 0, -1):
        date = datetime.utcnow() - timedelta(days=i)
        change = random.uniform(-0.04, 0.06)
        price = round(price * (1 + change) / 100) * 100
        price = max(int(base * 0.60), min(int(base * 1.65), price))
        history.append({
            "date": date.strftime("%Y-%m-%d"),
            "price_per_kg": price,
            "commodity": commodity,
            "region": region or "Guinée",
        })
    return history


def get_market_trends(commodity: str) -> dict:
    base = BASE_PRICES.get(commodity, 10_000)
    current   = round(base * (1 + random.uniform(-0.12, 0.20)) / 100) * 100
    month_ago = round(base * (1 + random.uniform(-0.15, 0.12)) / 100) * 100
    change_pct = round((current - month_ago) / month_ago * 100, 2)

    demand = random.choice(["low", "normal", "normal", "high"])
    supply = random.choice(["low", "normal", "normal", "high"])

    forecast_7d  = round(current * (1 + random.uniform(-0.06, 0.09)) / 100) * 100
    forecast_30d = round(current * (1 + random.uniform(-0.12, 0.18)) / 100) * 100

    ANALYSES = {
        "riz": (
            "Le riz de bas-fond (Basse-Guinée) est en campagne active. "
            "Les importations asiatiques maintiennent une pression baissière sur le riz local."
        ),
        "fonio": (
            "Le fonio, culture emblématique de Moyenne-Guinée, bénéficie d'une demande "
            "internationale croissante (diaspora, marchés bio). Prix orientés à la hausse."
        ),
        "café": (
            "Le Robusta de Guinée Forestière est très apprécié à l'export. "
            "Récolte principale (nov–jan) génère une pression baissière temporaire sur les prix."
        ),
        "huile_de_palme": (
            "L'huile artisanale domine le marché local. "
            "Plantations villageoises de Basse-Guinée assurent l'essentiel de l'offre nationale."
        ),
        "manioc": (
            "Aliment de base de Basse-Guinée et Guinée Forestière. "
            "Pertes post-récolte élevées (35-45%) réduisent l'offre disponible sur les marchés."
        ),
        "banane_plantain": (
            "Banane plantain de Guinée Forestière alimente Conakry toute l'année. "
            "Périssabilité élevée crée des fluctuations importantes selon les routes."
        ),
        "maïs": (
            "Concentré en Haute-Guinée et Moyenne-Guinée. "
            "Corridors commerciaux actifs vers Mali et Sierra Leone."
        ),
        "arachide": (
            "Culture de rente de Haute-Guinée. Récolte (déc–fév) fait baisser les prix. "
            "Forte demande pour l'huile d'arachide artisanale à Conakry."
        ),
    }
    analysis = ANALYSES.get(commodity, f"Prix du {commodity.replace('_', ' ')} stable à court terme.")

    return {
        "commodity": commodity,
        "avg_price": current,
        "min_price": round(current * 0.80 / 100) * 100,
        "max_price": round(current * 1.25 / 100) * 100,
        "price_change_pct": change_pct,
        "demand_level": demand,
        "supply_level": supply,
        "forecast_7d": forecast_7d,
        "forecast_30d": forecast_30d,
        "analysis": analysis,
        "best_selling_markets": _get_best_markets(commodity),
        "currency": "GNF",
    }


def _get_best_markets(commodity: str) -> List[dict]:
    base = BASE_PRICES.get(commodity, 10_000)
    markets = list(MARKETS.keys())
    random.shuffle(markets)
    return [
        {
            "market": m,
            "region": MARKETS[m]["region"],
            "price_per_kg": round(base * (1 + random.uniform(0.05, 0.30)) / 100) * 100,
        }
        for m in markets[:3]
    ]


def get_trade_opportunities() -> List[dict]:
    """Opportunités de commerce inter-régional et sous-régional (CEDEAO)."""
    opportunities = []
    # Corridors commerciaux typiques de la Guinée
    CORRIDORS = [
        ("Guinée Forestière", "Conakry (Madina)", "café"),
        ("Guinée Forestière", "Conakry (Cosa)",   "huile_de_palme"),
        ("Haute-Guinée",      "Conakry (Madina)", "arachide"),
        ("Haute-Guinée",      "Conakry (Madina)", "maïs"),
        ("Moyenne-Guinée",    "Conakry (Madina)", "fonio"),
        ("Basse-Guinée",      "Haute-Guinée",     "riz"),
        ("Moyenne-Guinée",    "Haute-Guinée",     "fonio"),
        # Commerce sous-régional CEDEAO
        ("Haute-Guinée",      "Mali (Bamako)",    "maïs"),
        ("Guinée Forestière", "Sierra Leone",     "café"),
        ("Basse-Guinée",      "Guinée-Bissau",    "riz"),
        ("Moyenne-Guinée",    "Sénégal (Dakar)",  "fonio"),
    ]
    for src_region, dst, commodity in CORRIDORS:
        base = BASE_PRICES[commodity]
        src_price = round(base * random.uniform(0.70, 0.88) / 100) * 100
        dst_price = round(base * random.uniform(1.12, 1.50) / 100) * 100
        margin = round((dst_price - src_price) / src_price * 100, 1)
        if margin > 14:
            opportunities.append({
                "commodity": commodity.replace("_", " "),
                "source_region": src_region,
                "destination_region": dst,
                "source_price": src_price,
                "destination_price": dst_price,
                "margin_pct": margin,
                "estimated_volume_tons": round(random.uniform(1, 30), 1),
                "opportunity_score": min(100, round(margin * 2.2, 1)),
                "currency": "GNF",
                "transport_note": _transport_note(src_region),
            })
    return sorted(opportunities, key=lambda x: x["opportunity_score"], reverse=True)


def _transport_note(src: str) -> str:
    notes = {
        "Guinée Forestière": "Route N1 — difficile mai–oct (saison des pluies / axe enclavé)",
        "Haute-Guinée":       "Axe Kankan–Conakry ~650 km, 10-14h de trajet",
        "Moyenne-Guinée":     "Route de Labé — partiellement non bitumée",
        "Basse-Guinée":       "Proximité Conakry — logistique favorable",
    }
    return notes.get(src, "Transport routier disponible")
