from fastapi import APIRouter, Query
from typing import Optional
from app.services.market_service import (
    COMMODITIES, get_current_prices, get_price_history,
    get_market_trends, get_trade_opportunities,
)

router = APIRouter(prefix="/market", tags=["Market"])


@router.get("/prices")
async def get_prices(
    commodity: Optional[str] = Query(None, description="Filtre par culture"),
    region: Optional[str] = Query(None, description="Filtre par région"),
):
    prices = get_current_prices(commodity, region)
    return {"prices": prices, "count": len(prices)}


@router.get("/prices/history/{commodity}")
async def price_history(
    commodity: str,
    region: Optional[str] = Query(None),
    days: int = Query(30, ge=7, le=365),
):
    if commodity not in COMMODITIES:
        return {"error": f"Culture inconnue. Choisir parmi: {COMMODITIES}"}
    return {"commodity": commodity, "history": get_price_history(commodity, region, days)}


@router.get("/trends/{commodity}")
async def market_trend(commodity: str):
    if commodity not in COMMODITIES:
        return {"error": f"Culture inconnue. Disponibles: {', '.join(COMMODITIES)}"}
    return get_market_trends(commodity)


@router.get("/trends")
async def all_trends():
    return {"trends": [get_market_trends(c) for c in COMMODITIES]}


@router.get("/opportunities")
async def trade_opportunities():
    opportunities = get_trade_opportunities()
    return {"opportunities": opportunities, "count": len(opportunities)}


@router.get("/commodities")
async def list_commodities():
    return {
        "commodities": [
            {
                "name": c,
                "base_price_xof_kg": __import__("app.services.market_service", fromlist=["BASE_PRICES"]).BASE_PRICES[c],
            }
            for c in COMMODITIES
        ]
    }


@router.get("/summary")
async def market_summary():
    all_prices = get_current_prices()
    by_commodity = {}
    for p in all_prices:
        c = p["commodity"]
        if c not in by_commodity:
            by_commodity[c] = []
        by_commodity[c].append(p["price_per_kg"])

    return {
        "summary": [
            {
                "commodity": c,
                "avg_price_kg": round(sum(prices) / len(prices), 0),
                "min_price_kg": round(min(prices), 0),
                "max_price_kg": round(max(prices), 0),
                "spread_pct": round((max(prices) - min(prices)) / min(prices) * 100, 1),
            }
            for c, prices in by_commodity.items()
        ]
    }
