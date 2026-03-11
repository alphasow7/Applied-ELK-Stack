from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from app.models.database import Base


class CommodityPrice(Base):
    __tablename__ = "commodity_prices"

    id = Column(Integer, primary_key=True, index=True)
    commodity = Column(String(100), nullable=False, index=True)
    market_name = Column(String(200), nullable=False)
    region = Column(String(100), nullable=False)
    country = Column(String(100), default="Sénégal")
    price_per_kg = Column(Float, nullable=False)
    currency = Column(String(10), default="XOF")
    unit = Column(String(20), default="kg")
    source = Column(String(100), nullable=True)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())


class MarketTrend(Base):
    __tablename__ = "market_trends"

    id = Column(Integer, primary_key=True, index=True)
    commodity = Column(String(100), nullable=False, index=True)
    region = Column(String(100), nullable=False)
    period = Column(String(20), nullable=False)  # weekly, monthly
    avg_price = Column(Float, nullable=False)
    min_price = Column(Float, nullable=False)
    max_price = Column(Float, nullable=False)
    price_change_pct = Column(Float, default=0.0)
    demand_level = Column(String(20), default="normal")  # low, normal, high
    supply_level = Column(String(20), default="normal")
    forecast_7d = Column(Float, nullable=True)
    forecast_30d = Column(Float, nullable=True)
    analysis = Column(Text, nullable=True)
    computed_at = Column(DateTime(timezone=True), server_default=func.now())


class TradeOpportunity(Base):
    __tablename__ = "trade_opportunities"

    id = Column(Integer, primary_key=True, index=True)
    commodity = Column(String(100), nullable=False)
    source_region = Column(String(100), nullable=False)
    destination_region = Column(String(100), nullable=False)
    source_price = Column(Float, nullable=False)
    destination_price = Column(Float, nullable=False)
    margin_pct = Column(Float, nullable=False)
    estimated_volume_tons = Column(Float, nullable=True)
    opportunity_score = Column(Float, nullable=False)  # 0-100
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
