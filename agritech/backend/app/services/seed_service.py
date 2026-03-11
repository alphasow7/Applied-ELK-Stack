"""Seed the database with realistic demo data — Contexte Guinée Conakry."""
import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.farmer import User, Farm, Crop, YieldPrediction, UserRole, SubscriptionTier
from app.models.market import CommodityPrice, MarketTrend
from app.models.weather import WeatherData, SoilHealth
from app.models.subscription import SubscriptionPlan
from app.core.security import get_password_hash
from app.services.market_service import COMMODITIES, MARKETS, BASE_PRICES  # prix en GNF
from app.services.weather_service import get_soil_health_score, compute_yield_prediction, _simulate_weather


# ─── Plans tarifés en GNF (Franc Guinéen) ──────────────────────────────────────
# 1 EUR ≈ 9 400 GNF | 1 USD ≈ 8 600 GNF
PLANS = [
    {
        "name": "Freemium Agriculteur",
        "tier": "free",
        "price_monthly_xof": 0,
        "max_farms": 1,
        "max_users": 1,
        "ussd_access": True,
        "web_dashboard": False,
        "market_analytics": False,
        "yield_predictions": True,
        "api_access": False,
        "weather_alerts": True,
        "insurance_module": False,
        "description": (
            "Accès gratuit via USSD (*384*1#) et SMS — météo, rendements, alertes. "
            "Financé par ONG partenaires (USAID, FAO, GIZ, FIDA en Guinée)."
        ),
    },
    {
        "name": "Coopérative / Groupement",
        "tier": "cooperative",
        "price_monthly_xof": 200_000,   # ~21 EUR/mois
        "price_yearly_xof": 2_160_000,
        "max_farms": 300,
        "max_users": 15,
        "ussd_access": True,
        "web_dashboard": True,
        "market_analytics": True,
        "yield_predictions": True,
        "api_access": False,
        "weather_alerts": True,
        "insurance_module": False,
        "description": (
            "Dashboard coopérative, prix marchés temps réel (12 marchés guinéens), "
            "gestion groupée, prévisions rendement multi-cultures, alertes saison des pluies."
        ),
    },
    {
        "name": "Acheteur / Exportateur",
        "tier": "enterprise",
        "price_monthly_xof": 650_000,   # ~69 EUR/mois
        "price_yearly_xof": 7_020_000,
        "max_farms": 5000,
        "max_users": 50,
        "ussd_access": True,
        "web_dashboard": True,
        "market_analytics": True,
        "yield_predictions": True,
        "api_access": True,
        "weather_alerts": True,
        "insurance_module": False,
        "description": (
            "API complète, prévision d'offre par région, corridors CEDEAO, "
            "opportunités d'arbitrage (café, fonio, arachide). Exportateurs et industriels."
        ),
    },
    {
        "name": "Assureur Agricole",
        "tier": "insurer",
        "price_monthly_xof": 1_300_000,  # ~138 EUR/mois
        "price_yearly_xof": 14_040_000,
        "max_farms": 99999,
        "max_users": 100,
        "ussd_access": True,
        "web_dashboard": True,
        "market_analytics": True,
        "yield_predictions": True,
        "api_access": True,
        "weather_alerts": True,
        "insurance_module": True,
        "description": (
            "Module assurance paramétrique (indice pluviométrique, NDVI), scoring risque "
            "par exploitation, données satellites. Pour assureurs et projets BAD/FIDA."
        ),
    },
]

# ─── Agriculteurs démo — 4 régions naturelles de Guinée ────────────────────────
# Noms représentatifs : Pular (Moyenne-Guinée), Malinké (Haute-Guinée), Susu (Basse-Guinée)
FARMERS_DATA = [
    # (nom,                 téléphone Orange GN,  région naturelle,    lat,    lon)
    ("Mamadou Diallo",      "+224620123456",  "Basse-Guinée",         9.55,  -13.68),
    ("Aissatou Bah",        "+224621234567",  "Moyenne-Guinée",      11.32,  -12.29),
    ("Ibrahima Sow",        "+224622345678",  "Moyenne-Guinée",      10.38,  -12.08),
    ("Fatoumata Barry",     "+224623456789",  "Haute-Guinée",        10.39,   -9.31),
    ("Sékou Kouyaté",       "+224624567890",  "Haute-Guinée",        11.42,   -9.17),
    ("Mariama Condé",       "+224625678901",  "Guinée Forestière",    7.75,   -8.82),
    ("Oumar Camara",        "+224626789012",  "Guinée Forestière",    8.55,  -10.13),
    ("Kadiatou Traoré",     "+224627890123",  "Basse-Guinée",        10.05,  -12.87),
]

# Cultures par région naturelle
CROPS_BY_REGION = {
    "Basse-Guinée":       ["riz", "manioc", "banane_plantain", "huile_de_palme"],
    "Moyenne-Guinée":     ["fonio", "maïs", "arachide", "riz"],
    "Haute-Guinée":       ["maïs", "arachide", "riz", "fonio"],
    "Guinée Forestière":  ["riz", "café", "manioc", "banane_plantain"],
}

# Types de sol typiques en Guinée
SOILS_BY_REGION = {
    "Basse-Guinée":       ["latéritique", "mangrove", "argilo-limoneux", "sablo-limoneux"],
    "Moyenne-Guinée":     ["latéritique", "gravillonnaire", "argilo-sableux"],
    "Haute-Guinée":       ["argilo-sableux", "latéritique", "limoneux"],
    "Guinée Forestière":  ["argilo-limoneux", "humifère", "latéritique rouge"],
}


async def seed_database(db: AsyncSession):
    existing = await db.execute(select(SubscriptionPlan).limit(1))
    if existing.scalar_one_or_none():
        return  # Already seeded

    # Plans
    plan_objs = []
    for p in PLANS:
        plan = SubscriptionPlan(**p)
        db.add(plan)
        plan_objs.append(plan)
    await db.flush()

    # Admin
    admin = User(
        phone_number="+224600000000",
        email="admin@agritech.gn",
        hashed_password=get_password_hash("admin123"),
        full_name="Admin AgriTech Guinée",
        role=UserRole.ADMIN,
        subscription_tier=SubscriptionTier.FREE,
    )
    db.add(admin)

    # Coopérative — Groupement Foulaya, Labé (Moyenne-Guinée, culture fonio)
    coop = User(
        phone_number="+224601111111",
        email="coop@groupement-foulaya.gn",
        hashed_password=get_password_hash("coop123"),
        full_name="Groupement Foulaya — Labé",
        role=UserRole.COOPERATIVE,
        subscription_tier=SubscriptionTier.COOPERATIVE,
    )
    db.add(coop)

    # Acheteur — exportateur café/fonio basé à Conakry
    buyer = User(
        phone_number="+224602222222",
        email="export@guinee-agri-export.gn",
        hashed_password=get_password_hash("buyer123"),
        full_name="Guinée Agri Export SARL",
        role=UserRole.BUYER,
        subscription_tier=SubscriptionTier.ENTERPRISE,
    )
    db.add(buyer)

    await db.flush()

    for name, phone, region, lat, lon in FARMERS_DATA:
        farmer = User(
            phone_number=phone,
            hashed_password=get_password_hash("farmer123"),
            full_name=name,
            role=UserRole.FARMER,
            subscription_tier=SubscriptionTier.FREE,
        )
        db.add(farmer)
        await db.flush()

        farm = Farm(
            owner_id=farmer.id,
            name=f"Exploitation de {name.split()[0]}",
            latitude=lat + random.uniform(-0.15, 0.15),
            longitude=lon + random.uniform(-0.15, 0.15),
            area_hectares=round(random.uniform(0.5, 3.5), 2),
            region=region,
            country="Guinée",
            soil_type=random.choice(SOILS_BY_REGION.get(region, ["latéritique"])),
            irrigation=random.random() > 0.78,  # irrigation très peu répandue en Guinée
        )
        db.add(farm)
        await db.flush()

        crop_type = random.choice(CROPS_BY_REGION.get(region, ["riz"]))
        # Calendrier Guinée : semis mai-juil, récolte oct-jan selon culture
        planting = datetime.utcnow() - timedelta(days=random.randint(20, 130))
        crop = Crop(
            farm_id=farm.id,
            crop_type=crop_type,
            planting_date=planting,
            expected_harvest_date=planting + timedelta(days=random.randint(90, 200)),
            area_planted_hectares=farm.area_hectares,
            status=random.choice(["planted", "growing", "growing"]),
        )
        db.add(crop)
        await db.flush()

        # Yield prediction
        weather = _simulate_weather(lat, lon, 7)
        soil = get_soil_health_score(lat, lon)
        pred = compute_yield_prediction(
            crop_type, farm.area_hectares, weather, soil["health_score"], farm.irrigation
        )
        yp = YieldPrediction(
            crop_id=crop.id,
            predicted_yield_kg=pred["predicted_yield_kg"],
            confidence_score=pred["confidence_score"],
            risk_level=pred["risk_level"],
            drought_risk=pred["drought_risk"],
            flood_risk=pred["flood_risk"],
            pest_risk=pred["pest_risk"],
            recommendation=pred["recommendation"],
        )
        db.add(yp)

    # Market prices — 7 jours d'historique (GNF)
    for days_ago in range(7, 0, -1):
        recorded = datetime.utcnow() - timedelta(days=days_ago)
        for market_name, minfo in MARKETS.items():
            for commodity in COMMODITIES:
                base = BASE_PRICES[commodity]
                price = round(base * (1 + random.uniform(-0.12, 0.18)) / 100) * 100
                db.add(CommodityPrice(
                    commodity=commodity,
                    market_name=market_name,
                    region=minfo["region"],
                    price_per_kg=price,
                    currency="GNF",
                    recorded_at=recorded,
                ))

    # Soil health records
    for _, _, region, lat, lon in FARMERS_DATA:
        soil = get_soil_health_score(lat, lon)
        db.add(SoilHealth(latitude=lat, longitude=lon, region=region, **soil))

    await db.commit()
