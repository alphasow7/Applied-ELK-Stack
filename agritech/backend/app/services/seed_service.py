"""Seed the database with realistic demo data."""
import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.farmer import User, Farm, Crop, YieldPrediction, UserRole, SubscriptionTier
from app.models.market import CommodityPrice, MarketTrend
from app.models.weather import WeatherData, SoilHealth
from app.models.subscription import SubscriptionPlan
from app.core.security import get_password_hash
from app.services.market_service import COMMODITIES, MARKETS, BASE_PRICES
from app.services.weather_service import get_soil_health_score, compute_yield_prediction, _simulate_weather


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
        "description": "Accès gratuit via USSD/SMS — prévisions météo, rendements et alertes.",
    },
    {
        "name": "Coopérative",
        "tier": "cooperative",
        "price_monthly_xof": 25000,
        "price_yearly_xof": 270000,
        "max_farms": 200,
        "max_users": 10,
        "ussd_access": True,
        "web_dashboard": True,
        "market_analytics": True,
        "yield_predictions": True,
        "api_access": False,
        "weather_alerts": True,
        "insurance_module": False,
        "description": "Dashboard coopérative, prix marchés en temps réel, gestion groupée.",
    },
    {
        "name": "Acheteur Industriel",
        "tier": "enterprise",
        "price_monthly_xof": 75000,
        "price_yearly_xof": 810000,
        "max_farms": 5000,
        "max_users": 50,
        "ussd_access": True,
        "web_dashboard": True,
        "market_analytics": True,
        "yield_predictions": True,
        "api_access": True,
        "weather_alerts": True,
        "insurance_module": False,
        "description": "Accès API complet, opportunités commerciales, analyses sectorielles.",
    },
    {
        "name": "Assureur Agricole",
        "tier": "insurer",
        "price_monthly_xof": 150000,
        "price_yearly_xof": 1620000,
        "max_farms": 99999,
        "max_users": 100,
        "ussd_access": True,
        "web_dashboard": True,
        "market_analytics": True,
        "yield_predictions": True,
        "api_access": True,
        "weather_alerts": True,
        "insurance_module": True,
        "description": "Module assurance paramétrique, scoring risque, données satellites complètes.",
    },
]

FARMERS_DATA = [
    ("Moussa Diallo", "+221771234567", "Thiès", 14.79, -16.93),
    ("Fatou Ndiaye", "+221772345678", "Kaolack", 14.15, -16.08),
    ("Ibrahima Sow", "+221773456789", "Saint-Louis", 16.02, -16.49),
    ("Aminata Diop", "+221774567890", "Ziguinchor", 12.56, -16.27),
    ("Cheikh Ba", "+221775678901", "Tambacounda", 13.77, -13.67),
    ("Rokhaya Fall", "+221776789012", "Thiès", 14.85, -16.55),
    ("Oumar Gueye", "+221777890123", "Louga", 15.62, -16.22),
    ("Ndéye Sarr", "+221778901234", "Kaolack", 14.23, -15.97),
]


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

    # Admin user
    admin = User(
        phone_number="+221700000000",
        email="admin@agritech.sn",
        hashed_password=get_password_hash("admin123"),
        full_name="Admin AgriTech",
        role=UserRole.ADMIN,
        subscription_tier=SubscriptionTier.FREE,
    )
    db.add(admin)

    # Cooperative user
    coop = User(
        phone_number="+221701111111",
        email="coop@groupement-thiès.sn",
        hashed_password=get_password_hash("coop123"),
        full_name="Groupement Thiès Nord",
        role=UserRole.COOPERATIVE,
        subscription_tier=SubscriptionTier.COOPERATIVE,
    )
    db.add(coop)

    # Buyer
    buyer = User(
        phone_number="+221702222222",
        email="achat@senagri.sn",
        hashed_password=get_password_hash("buyer123"),
        full_name="Senagri Industries",
        role=UserRole.BUYER,
        subscription_tier=SubscriptionTier.ENTERPRISE,
    )
    db.add(buyer)

    await db.flush()

    # Farmers with farms and crops
    crop_types = ["mil", "arachide", "sorgho", "maïs", "niébé"]
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
            name=f"Champ de {name.split()[0]}",
            latitude=lat + random.uniform(-0.1, 0.1),
            longitude=lon + random.uniform(-0.1, 0.1),
            area_hectares=round(random.uniform(0.5, 5.0), 2),
            region=region,
            soil_type=random.choice(["sableux", "argileux", "limoneux", "argilo-sableux"]),
            irrigation=random.random() > 0.7,
        )
        db.add(farm)
        await db.flush()

        crop_type = random.choice(crop_types)
        planting = datetime.utcnow() - timedelta(days=random.randint(30, 90))
        crop = Crop(
            farm_id=farm.id,
            crop_type=crop_type,
            planting_date=planting,
            expected_harvest_date=planting + timedelta(days=random.randint(90, 150)),
            area_planted_hectares=farm.area_hectares,
            status=random.choice(["planted", "growing", "growing"]),
        )
        db.add(crop)
        await db.flush()

        # Yield prediction
        weather = _simulate_weather(lat, lon, 7)
        soil = get_soil_health_score(lat, lon)
        pred = compute_yield_prediction(crop_type, farm.area_hectares, weather, soil["health_score"], farm.irrigation)
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

    # Market prices — 7 days of history
    for days_ago in range(7, 0, -1):
        recorded = datetime.utcnow() - timedelta(days=days_ago)
        for market_name, minfo in MARKETS.items():
            for commodity in COMMODITIES:
                base = BASE_PRICES[commodity]
                price = round(base * (1 + random.uniform(-0.1, 0.15)), 0)
                db.add(CommodityPrice(
                    commodity=commodity,
                    market_name=market_name,
                    region=minfo["region"],
                    price_per_kg=price,
                    recorded_at=recorded,
                ))

    # Soil health records
    for _, _, region, lat, lon in FARMERS_DATA:
        soil = get_soil_health_score(lat, lon)
        db.add(SoilHealth(latitude=lat, longitude=lon, region=region, **soil))

    await db.commit()
