import httpx
import random
from datetime import datetime, timedelta
from typing import Optional
from app.core.config import settings
from app.core.logging import logger


# Besoins en eau (mm/cycle) adaptés aux cultures guinéennes
# La Guinée reçoit 1 200 à 4 300 mm/an selon les régions
CROP_WATER_NEEDS = {
    "riz":              1200,   # riz de bas-fond / irrigué
    "manioc":            600,   # tolérant à la sécheresse
    "fonio":             300,   # très résistant à la sécheresse (Moyenne-Guinée)
    "maïs":              500,
    "arachide":          450,
    "banane_plantain":   900,   # humidité élevée nécessaire
    "café":              1800,  # Robusta — Guinée Forestière humide
    "huile_de_palme":    2000,  # palmier à huile — zone forestière
}


async def fetch_weather(lat: float, lon: float, days: int = 7) -> dict:
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "windspeed_10m_max",
            "et0_fao_evapotranspiration",
            "soil_moisture_0_to_7cm",
        ],
        "timezone": "Africa/Conakry",
        "forecast_days": days,
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(settings.weather_api_url, params=params)
            resp.raise_for_status()
            data = resp.json()
            logger.info(f"Weather fetched for ({lat},{lon})")
            return data
    except Exception as e:
        logger.warning(f"Weather API error: {e} — using simulated data")
        return _simulate_weather(lat, lon, days)


def _simulate_weather(lat: float, lon: float, days: int) -> dict:
    # Simulation réaliste pour la Guinée :
    # Basse-Guinée (lat ~9-11) : chaud et très humide (4000mm/an)
    # Guinée Forestière (lat ~7-9) : forêt tropicale, pluies intenses
    # Haute-Guinée (lat ~10-12, lon > -12) : savane, plus sec (1200-1500mm)
    # Moyenne-Guinée (lat ~10-12, lon -12 à -14) : Futa Djalon, plus frais
    is_forest = lat < 9.0
    is_haute = lon > -11.0
    is_moyenne = -14.0 < lon < -11.5 and lat > 10.0

    base_temp_max = 26.0 if is_forest else (31.0 if is_haute else 28.0)
    base_precip = 8.0 if is_forest else (3.0 if is_haute else 5.0)

    base_date = datetime.utcnow()
    daily = {
        "time": [(base_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)],
        "temperature_2m_max": [round(base_temp_max + random.uniform(-2, 4), 1) for _ in range(days)],
        "temperature_2m_min": [round((base_temp_max - 8) + random.uniform(-2, 3), 1) for _ in range(days)],
        "precipitation_sum": [round(max(0, random.gauss(base_precip, base_precip * 0.8)), 1) for _ in range(days)],
        "windspeed_10m_max": [round(random.uniform(3, 20), 1) for _ in range(days)],
        "et0_fao_evapotranspiration": [round(random.uniform(3.5, 6.5), 2) for _ in range(days)],
        "soil_moisture_0_to_7cm": [round(random.uniform(0.25, 0.50), 3) for _ in range(days)],
    }
    return {"latitude": lat, "longitude": lon, "daily": daily, "simulated": True}


def compute_yield_prediction(
    crop_type: str,
    area_ha: float,
    weather_data: dict,
    soil_health_score: float = 70.0,
    irrigation: bool = False,
) -> dict:
    daily = weather_data.get("daily", {})
    temps_max = daily.get("temperature_2m_max", [32] * 7)
    precip = daily.get("precipitation_sum", [2] * 7)
    soil_moisture = daily.get("soil_moisture_0_to_7cm", [0.2] * 7)

    avg_temp = sum(temps_max) / len(temps_max) if temps_max else 32
    total_rain = sum(precip) * 4  # scale 7d to ~monthly
    avg_soil_moisture = sum(soil_moisture) / len(soil_moisture) if soil_moisture else 0.2

    water_need = CROP_WATER_NEEDS.get(crop_type.lower(), 500)
    water_stress = min(1.0, (total_rain + (300 if irrigation else 0)) / water_need)

    temp_stress = 1.0
    if avg_temp > 35:
        temp_stress = max(0.5, 1 - (avg_temp - 35) * 0.05)
    elif avg_temp < 15:
        temp_stress = max(0.4, 1 - (15 - avg_temp) * 0.08)

    soil_factor = soil_health_score / 100

    # Rendements de base en Guinée (kg/ha) — sources : FAO, ANPROCA Guinée
    BASE_YIELDS = {
        "riz":              2200,  # riz pluvial (3500-4500 en irrigué bas-fond)
        "manioc":           7500,  # très productif en Guinée
        "fonio":             800,  # rendement modeste mais très résistant
        "maïs":             2000,
        "arachide":         1100,
        "banane_plantain":  8000,  # kg/ha
        "café":              600,  # Robusta — cerises transformées
        "huile_de_palme":   2500,  # régimes / ha
    }
    base_yield = BASE_YIELDS.get(crop_type.lower(), 1500)

    predicted_yield_kg = area_ha * base_yield * water_stress * temp_stress * soil_factor

    confidence = 0.60 + (0.2 * soil_factor) + (0.1 * water_stress) + random.uniform(-0.05, 0.05)
    confidence = min(0.95, max(0.40, confidence))

    drought_risk = max(0, 1 - water_stress) * 0.8
    flood_risk = min(1, max(0, total_rain - water_need * 1.5) / (water_need * 0.5)) * 0.5
    pest_risk = 0.2 + (avg_soil_moisture > 0.35) * 0.2 + random.uniform(0, 0.15)

    risk_score = (drought_risk + flood_risk + pest_risk) / 3
    risk_level = "low" if risk_score < 0.25 else ("high" if risk_score > 0.55 else "medium")

    recommendations = []
    if drought_risk > 0.4:
        recommendations.append("Risque de sécheresse élevé — envisager l'irrigation d'appoint.")
    if flood_risk > 0.3:
        recommendations.append("Risque d'inondation — prévoir des canaux de drainage.")
    if pest_risk > 0.35:
        recommendations.append("Surveiller les ravageurs en raison de l'humidité élevée.")
    if soil_factor < 0.6:
        recommendations.append("Améliorer la santé du sol avec des engrais organiques.")
    if not recommendations:
        recommendations.append("Conditions favorables — maintenir les pratiques actuelles.")

    return {
        "predicted_yield_kg": round(predicted_yield_kg, 2),
        "confidence_score": round(confidence, 3),
        "risk_level": risk_level,
        "drought_risk": round(drought_risk, 3),
        "flood_risk": round(flood_risk, 3),
        "pest_risk": round(pest_risk, 3),
        "recommendation": " ".join(recommendations),
        "water_stress_index": round(water_stress, 3),
        "temp_stress_index": round(temp_stress, 3),
    }


def get_soil_health_score(lat: float, lon: float) -> dict:
    random.seed(int((lat + lon) * 1000))
    ph = round(random.uniform(5.5, 7.5), 1)
    organic_matter = round(random.uniform(0.5, 3.5), 2)
    ndvi = round(random.uniform(0.1, 0.8), 3)
    health_score = round((
        (1 - abs(ph - 6.5) / 2) * 30 +
        (organic_matter / 3.5) * 30 +
        ndvi * 40
    ), 1)

    def level(v, t1, t2):
        return "low" if v < t1 else ("high" if v > t2 else "medium")

    return {
        "ph_level": ph,
        "organic_matter_pct": organic_matter,
        "nitrogen_level": level(organic_matter, 1.0, 2.5),
        "phosphorus_level": level(random.uniform(0, 1), 0.3, 0.7),
        "potassium_level": level(random.uniform(0, 1), 0.3, 0.7),
        "moisture_retention": "high" if ph > 6.5 else "medium",
        "erosion_risk": "low" if ndvi > 0.5 else ("high" if ndvi < 0.2 else "medium"),
        "ndvi_index": ndvi,
        "health_score": health_score,
        "recommendation": (
            "Sol en bonne santé." if health_score > 70
            else "Ajouter de la matière organique et corriger le pH."
        ),
    }
