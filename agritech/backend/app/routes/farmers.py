from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.models.database import get_db
from app.models.farmer import User, Farm, Crop, YieldPrediction
from app.routes.auth import get_current_user
from app.services.weather_service import fetch_weather, compute_yield_prediction, get_soil_health_score

router = APIRouter(prefix="/farmers", tags=["Farmers"])


class FarmCreate(BaseModel):
    name: str
    latitude: float
    longitude: float
    area_hectares: float
    region: str
    soil_type: Optional[str] = None
    irrigation: bool = False


class CropCreate(BaseModel):
    crop_type: str
    planting_date: datetime
    expected_harvest_date: Optional[datetime] = None
    area_planted_hectares: float
    notes: Optional[str] = None


@router.get("/farms")
async def list_farms(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Farm).where(Farm.owner_id == user.id).options(selectinload(Farm.crops))
    )
    farms = result.scalars().all()
    return [
        {
            "id": f.id,
            "name": f.name,
            "latitude": f.latitude,
            "longitude": f.longitude,
            "area_hectares": f.area_hectares,
            "region": f.region,
            "soil_type": f.soil_type,
            "irrigation": f.irrigation,
            "crop_count": len(f.crops),
            "created_at": f.created_at,
        }
        for f in farms
    ]


@router.post("/farms")
async def create_farm(data: FarmCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    farm = Farm(owner_id=user.id, **data.model_dump())
    db.add(farm)
    await db.commit()
    await db.refresh(farm)
    return {"id": farm.id, "message": "Champ créé avec succès"}


@router.get("/farms/{farm_id}")
async def get_farm(farm_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Farm).where(Farm.id == farm_id, Farm.owner_id == user.id)
        .options(selectinload(Farm.crops).selectinload(Crop.yield_predictions))
    )
    farm = result.scalar_one_or_none()
    if not farm:
        raise HTTPException(404, "Champ introuvable")

    soil = get_soil_health_score(farm.latitude, farm.longitude)
    return {
        "id": farm.id,
        "name": farm.name,
        "latitude": farm.latitude,
        "longitude": farm.longitude,
        "area_hectares": farm.area_hectares,
        "region": farm.region,
        "soil_type": farm.soil_type,
        "irrigation": farm.irrigation,
        "soil_health": soil,
        "crops": [
            {
                "id": c.id,
                "crop_type": c.crop_type,
                "planting_date": c.planting_date,
                "expected_harvest_date": c.expected_harvest_date,
                "area_planted_hectares": c.area_planted_hectares,
                "status": c.status,
                "latest_prediction": (
                    {
                        "predicted_yield_kg": c.yield_predictions[-1].predicted_yield_kg,
                        "confidence_score": c.yield_predictions[-1].confidence_score,
                        "risk_level": c.yield_predictions[-1].risk_level,
                        "recommendation": c.yield_predictions[-1].recommendation,
                    }
                    if c.yield_predictions else None
                ),
            }
            for c in farm.crops
        ],
    }


@router.post("/farms/{farm_id}/crops")
async def add_crop(
    farm_id: int,
    data: CropCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Farm).where(Farm.id == farm_id, Farm.owner_id == user.id))
    farm = result.scalar_one_or_none()
    if not farm:
        raise HTTPException(404, "Champ introuvable")

    crop = Crop(farm_id=farm_id, **data.model_dump())
    db.add(crop)
    await db.flush()

    # Generate yield prediction immediately
    weather = await fetch_weather(farm.latitude, farm.longitude)
    soil = get_soil_health_score(farm.latitude, farm.longitude)
    pred = compute_yield_prediction(
        data.crop_type, data.area_planted_hectares, weather, soil["health_score"], farm.irrigation
    )
    yp = YieldPrediction(crop_id=crop.id, **pred)
    db.add(yp)
    await db.commit()

    return {
        "crop_id": crop.id,
        "prediction": pred,
        "message": "Culture ajoutée avec prévision de rendement",
    }


@router.post("/farms/{farm_id}/predict")
async def predict_yield(farm_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Farm).where(Farm.id == farm_id, Farm.owner_id == user.id)
        .options(selectinload(Farm.crops))
    )
    farm = result.scalar_one_or_none()
    if not farm:
        raise HTTPException(404, "Champ introuvable")

    weather = await fetch_weather(farm.latitude, farm.longitude)
    soil = get_soil_health_score(farm.latitude, farm.longitude)

    predictions = []
    for crop in farm.crops:
        if crop.status != "harvested":
            pred = compute_yield_prediction(
                crop.crop_type, crop.area_planted_hectares, weather, soil["health_score"], farm.irrigation
            )
            yp = YieldPrediction(crop_id=crop.id, **pred)
            db.add(yp)
            predictions.append({"crop_id": crop.id, "crop_type": crop.crop_type, **pred})

    await db.commit()
    return {"predictions": predictions, "weather_source": "open-meteo" if not weather.get("simulated") else "simulated"}


@router.get("/dashboard")
async def farmer_dashboard(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Farm).where(Farm.owner_id == user.id).options(
            selectinload(Farm.crops).selectinload(Crop.yield_predictions)
        )
    )
    farms = result.scalars().all()

    total_area = sum(f.area_hectares for f in farms)
    active_crops = [c for f in farms for c in f.crops if c.status != "harvested"]
    total_predicted_yield = sum(
        c.yield_predictions[-1].predicted_yield_kg
        for c in active_crops if c.yield_predictions
    )

    return {
        "user": {"id": user.id, "name": user.full_name, "subscription": user.subscription_tier},
        "summary": {
            "total_farms": len(farms),
            "total_area_ha": round(total_area, 2),
            "active_crops": len(active_crops),
            "total_predicted_yield_kg": round(total_predicted_yield, 2),
        },
        "farms": [
            {
                "id": f.id,
                "name": f.name,
                "region": f.region,
                "area_ha": f.area_hectares,
                "crops": [c.crop_type for c in f.crops],
            }
            for f in farms
        ],
    }
