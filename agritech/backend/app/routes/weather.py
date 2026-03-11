from fastapi import APIRouter, Query
from app.services.weather_service import fetch_weather, get_soil_health_score

router = APIRouter(prefix="/weather", tags=["Weather & Soil"])

SENEGAL_REGIONS = {
    "Dakar": (14.72, -17.47),
    "Thiès": (14.79, -16.93),
    "Kaolack": (14.15, -16.08),
    "Ziguinchor": (12.56, -16.27),
    "Saint-Louis": (16.02, -16.49),
    "Tambacounda": (13.77, -13.67),
    "Diourbel": (14.65, -16.23),
    "Louga": (15.62, -16.22),
    "Fatick": (14.34, -16.41),
    "Kolda": (12.89, -14.94),
    "Matam": (15.66, -13.26),
    "Kaffrine": (14.10, -15.55),
    "Kédougou": (12.56, -12.18),
    "Sédhiou": (12.71, -15.56),
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
    coords = SENEGAL_REGIONS.get(region_name)
    if not coords:
        return {"error": f"Région inconnue. Disponibles: {list(SENEGAL_REGIONS.keys())}"}
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
    return {"regions": list(SENEGAL_REGIONS.keys())}


@router.get("/soil")
async def soil_health(lat: float = Query(...), lon: float = Query(...)):
    return get_soil_health_score(lat, lon)
