from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from app.models.database import Base


class WeatherData(Base):
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    region = Column(String(100), nullable=True)
    temperature_max = Column(Float, nullable=True)
    temperature_min = Column(Float, nullable=True)
    precipitation_mm = Column(Float, default=0.0)
    humidity_pct = Column(Float, nullable=True)
    wind_speed_ms = Column(Float, nullable=True)
    solar_radiation = Column(Float, nullable=True)
    evapotranspiration = Column(Float, nullable=True)
    soil_moisture = Column(Float, nullable=True)
    is_forecast = Column(Boolean, default=False)
    forecast_days_ahead = Column(Integer, default=0)
    recorded_at = Column(DateTime(timezone=True), nullable=False)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())


class SoilHealth(Base):
    __tablename__ = "soil_health"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    region = Column(String(100), nullable=True)
    ph_level = Column(Float, nullable=True)
    organic_matter_pct = Column(Float, nullable=True)
    nitrogen_level = Column(String(20), nullable=True)  # low, medium, high
    phosphorus_level = Column(String(20), nullable=True)
    potassium_level = Column(String(20), nullable=True)
    moisture_retention = Column(String(20), nullable=True)
    erosion_risk = Column(String(20), default="low")  # low, medium, high
    ndvi_index = Column(Float, nullable=True)  # vegetation health -1 to 1
    health_score = Column(Float, nullable=True)  # 0-100
    recommendation = Column(String(500), nullable=True)
    assessed_at = Column(DateTime(timezone=True), server_default=func.now())
