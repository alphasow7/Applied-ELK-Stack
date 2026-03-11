"""Analytics endpoint for cooperatives, buyers and insurers (B2B SaaS)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.database import get_db
from app.models.farmer import User, Farm, Crop, YieldPrediction, UserRole
from app.routes.auth import get_current_user
from app.services.market_service import get_market_trends, get_trade_opportunities, COMMODITIES

router = APIRouter(prefix="/analytics", tags=["Analytics B2B"])

B2B_ROLES = {UserRole.COOPERATIVE, UserRole.BUYER, UserRole.INSURER, UserRole.ADMIN}


def require_b2b(user: User = Depends(get_current_user)) -> User:
    if user.role not in B2B_ROLES:
        raise HTTPException(403, "Accès réservé aux comptes B2B (coopérative, acheteur, assureur)")
    return user


@router.get("/overview")
async def platform_overview(user: User = Depends(require_b2b), db: AsyncSession = Depends(get_db)):
    farm_count = (await db.execute(select(func.count(Farm.id)))).scalar()
    farmer_count = (await db.execute(select(func.count(User.id)).where(User.role == UserRole.FARMER))).scalar()
    crop_count = (await db.execute(select(func.count(Crop.id)))).scalar()
    total_area = (await db.execute(select(func.sum(Farm.area_hectares)))).scalar() or 0

    yield_sum = (await db.execute(
        select(func.sum(YieldPrediction.predicted_yield_kg))
        .join(Crop, YieldPrediction.crop_id == Crop.id)
        .where(Crop.status != "harvested")
    )).scalar() or 0

    return {
        "platform_stats": {
            "total_farmers": farmer_count,
            "total_farms": farm_count,
            "total_area_ha": round(float(total_area), 2),
            "active_crops": crop_count,
            "total_predicted_yield_tonnes": round(float(yield_sum) / 1000, 2),
        },
        "market_snapshot": [
            {
                "commodity": c,
                "avg_price_xof_kg": get_market_trends(c)["avg_price"],
                "trend": "up" if get_market_trends(c)["price_change_pct"] > 0 else "down",
            }
            for c in COMMODITIES[:5]
        ],
    }


@router.get("/supply-forecast")
async def supply_forecast(user: User = Depends(require_b2b), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(
            Crop.crop_type,
            func.count(Crop.id).label("field_count"),
            func.sum(Crop.area_planted_hectares).label("total_area"),
            func.sum(YieldPrediction.predicted_yield_kg).label("total_predicted_kg"),
            func.avg(YieldPrediction.confidence_score).label("avg_confidence"),
            func.avg(YieldPrediction.drought_risk).label("avg_drought_risk"),
        )
        .join(YieldPrediction, YieldPrediction.crop_id == Crop.id)
        .where(Crop.status != "harvested")
        .group_by(Crop.crop_type)
    )
    rows = result.all()

    return {
        "supply_forecast": [
            {
                "commodity": row.crop_type,
                "active_fields": row.field_count,
                "total_area_ha": round(float(row.total_area or 0), 2),
                "predicted_volume_tonnes": round(float(row.total_predicted_kg or 0) / 1000, 2),
                "confidence": round(float(row.avg_confidence or 0), 3),
                "drought_risk": round(float(row.avg_drought_risk or 0), 3),
            }
            for row in rows
        ]
    }


@router.get("/risk-heatmap")
async def risk_heatmap(user: User = Depends(require_b2b), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(
            Farm.region,
            Crop.crop_type,
            func.avg(YieldPrediction.drought_risk).label("drought"),
            func.avg(YieldPrediction.flood_risk).label("flood"),
            func.avg(YieldPrediction.pest_risk).label("pest"),
            func.count(Crop.id).label("n_fields"),
        )
        .join(Crop, Crop.farm_id == Farm.id)
        .join(YieldPrediction, YieldPrediction.crop_id == Crop.id)
        .group_by(Farm.region, Crop.crop_type)
    )
    rows = result.all()

    return {
        "risk_heatmap": [
            {
                "region": row.region,
                "commodity": row.crop_type,
                "drought_risk": round(float(row.drought or 0), 3),
                "flood_risk": round(float(row.flood or 0), 3),
                "pest_risk": round(float(row.pest or 0), 3),
                "composite_risk": round(
                    (float(row.drought or 0) + float(row.flood or 0) + float(row.pest or 0)) / 3, 3
                ),
                "fields_affected": row.n_fields,
            }
            for row in rows
        ]
    }


@router.get("/trade-opportunities")
async def opportunities(user: User = Depends(require_b2b)):
    return {"opportunities": get_trade_opportunities()}


@router.get("/insurance-scoring")
async def insurance_scoring(user: User = Depends(require_b2b), db: AsyncSession = Depends(get_db)):
    if user.role not in {UserRole.INSURER, UserRole.ADMIN}:
        raise HTTPException(403, "Accès réservé aux assureurs")

    result = await db.execute(
        select(
            Farm.id.label("farm_id"),
            Farm.region,
            Farm.area_hectares,
            Farm.irrigation,
            Crop.crop_type,
            YieldPrediction.predicted_yield_kg,
            YieldPrediction.confidence_score,
            YieldPrediction.drought_risk,
            YieldPrediction.flood_risk,
            YieldPrediction.pest_risk,
            YieldPrediction.risk_level,
        )
        .join(Crop, Crop.farm_id == Farm.id)
        .join(YieldPrediction, YieldPrediction.crop_id == Crop.id)
        .where(Crop.status != "harvested")
    )
    rows = result.all()

    scored = []
    for r in rows:
        composite_risk = (float(r.drought_risk) + float(r.flood_risk) + float(r.pest_risk)) / 3
        premium_rate = 0.03 + composite_risk * 0.12  # 3-15% of insured value
        from app.services.market_service import BASE_PRICES
        market_value = float(r.predicted_yield_kg) * BASE_PRICES.get(r.crop_type, 200)
        suggested_premium = round(market_value * premium_rate, 0)
        scored.append({
            "farm_id": r.farm_id,
            "region": r.region,
            "crop": r.crop_type,
            "area_ha": float(r.area_hectares),
            "irrigated": r.irrigation,
            "predicted_yield_kg": float(r.predicted_yield_kg),
            "market_value_xof": round(market_value, 0),
            "composite_risk_score": round(composite_risk, 3),
            "risk_level": r.risk_level,
            "suggested_premium_xof": suggested_premium,
            "premium_rate_pct": round(premium_rate * 100, 2),
        })

    return {"insurance_scores": sorted(scored, key=lambda x: x["composite_risk_score"], reverse=True)}
