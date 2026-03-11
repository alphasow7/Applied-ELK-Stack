from fastapi import APIRouter, Query
from app.services.weather_service import fetch_weather, get_soil_health_score

router = APIRouter(prefix="/weather", tags=["Weather & Soil"])

# 4 régions naturelles de Guinée + principales villes
# Source : Institut National de la Statistique Guinée (INS)
GUINEE_REGIONS = {
    # Basse-Guinée (Guinée Maritime)
    "Conakry":   (9.55,  -13.68),
    "Kindia":    (10.05, -12.87),
    "Boké":      (10.93, -14.30),
    "Coyah":     (9.70,  -13.38),
    "Forécariah":(9.43,  -13.10),
    # Moyenne-Guinée (Futa Djalon)
    "Labé":      (11.32, -12.29),
    "Mamou":     (10.38, -12.08),
    "Dalaba":    (10.69, -12.25),
    "Pita":      (11.07, -12.40),
    # Haute-Guinée
    "Kankan":    (10.39,  -9.31),
    "Faranah":   (10.04, -10.74),
    "Siguiri":   (11.42,  -9.17),
    "Kouroussa": (10.65, -10.00),
    # Guinée Forestière
    "N'Zérékoré":   (7.75,   -8.82),
    "Guéckédou":    (8.55,  -10.13),
    "Macenta":      (8.55,   -9.47),
    "Lola":         (7.82,   -8.53),
}


@router.get("/forecast")
async def weather_forecast(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    days: int = Query(7, ge=1, le=14),
):
    data = await fetch_weather(lat, lon, days)
    return {"location": {"lat": lat, "lon": lon}, "forecast": data}


@router.get("/region/{region_name}")
async def region_weather(region_name: str, days: int = Query(7, ge=1, le=14)):
    coords = GUINEE_REGIONS.get(region_name)
    if not coords:
        return {"error": f"Région inconnue. Disponibles: {list(GUINEE_REGIONS.keys())}"}
    lat, lon = coords
    data = await fetch_weather(lat, lon, days)
    soil = get_soil_health_score(lat, lon)
    return {
        "region": region_name,
        "coordinates": {"lat": lat, "lon": lon},
        "weather_forecast": data,
        "soil_health": soil,
    }


@router.get("/regions")
async def all_regions():
    return {"regions": list(GUINEE_REGIONS.keys())}


@router.get("/soil")
async def soil_health(lat: float = Query(...), lon: float = Query(...)):
    return get_soil_health_score(lat, lon)
