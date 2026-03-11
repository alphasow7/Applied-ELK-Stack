from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.models.database import Base


class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    COOPERATIVE = "cooperative"
    ENTERPRISE = "enterprise"
    INSURER = "insurer"


class UserRole(str, enum.Enum):
    FARMER = "farmer"
    COOPERATIVE = "cooperative"
    BUYER = "buyer"
    INSURER = "insurer"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.FARMER)
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE)
    is_active = Column(Boolean, default=True)
    preferred_language = Column(String(5), default="fr")  # fr, en, sw, ha
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    farms = relationship("Farm", back_populates="owner")
    alerts = relationship("Alert", back_populates="user")


class Farm(Base):
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    area_hectares = Column(Float, nullable=False)
    region = Column(String(100), nullable=False)
    country = Column(String(100), default="Sénégal")
    soil_type = Column(String(100), nullable=True)
    irrigation = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="farms")
    crops = relationship("Crop", back_populates="farm")


class Crop(Base):
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    crop_type = Column(String(100), nullable=False)  # mil, sorgho, arachide, maïs, riz
    planting_date = Column(DateTime(timezone=True), nullable=False)
    expected_harvest_date = Column(DateTime(timezone=True), nullable=True)
    actual_harvest_date = Column(DateTime(timezone=True), nullable=True)
    area_planted_hectares = Column(Float, nullable=False)
    predicted_yield_kg = Column(Float, nullable=True)
    actual_yield_kg = Column(Float, nullable=True)
    status = Column(String(50), default="planted")  # planted, growing, harvested
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    farm = relationship("Farm", back_populates="crops")
    yield_predictions = relationship("YieldPrediction", back_populates="crop")


class YieldPrediction(Base):
    __tablename__ = "yield_predictions"

    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False)
    predicted_yield_kg = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)  # 0-1
    risk_level = Column(String(20), default="medium")  # low, medium, high
    drought_risk = Column(Float, default=0.0)  # 0-1
    flood_risk = Column(Float, default=0.0)
    pest_risk = Column(Float, default=0.0)
    recommendation = Column(Text, nullable=True)
    predicted_at = Column(DateTime(timezone=True), server_default=func.now())

    crop = relationship("Crop", back_populates="yield_predictions")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    alert_type = Column(String(50), nullable=False)  # weather, price, pest, harvest
    severity = Column(String(20), default="info")  # info, warning, critical
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    sent_via_sms = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="alerts")
