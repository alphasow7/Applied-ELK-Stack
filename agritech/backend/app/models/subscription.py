from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from app.models.database import Base


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    tier = Column(String(50), nullable=False)  # free, cooperative, enterprise, insurer
    price_monthly_xof = Column(Float, nullable=False)
    price_yearly_xof = Column(Float, nullable=True)
    max_farms = Column(Integer, default=1)
    max_users = Column(Integer, default=1)
    ussd_access = Column(Boolean, default=True)
    web_dashboard = Column(Boolean, default=False)
    market_analytics = Column(Boolean, default=False)
    yield_predictions = Column(Boolean, default=True)
    api_access = Column(Boolean, default=False)
    weather_alerts = Column(Boolean, default=True)
    insurance_module = Column(Boolean, default=False)
    description = Column(Text, nullable=True)


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=False)
    status = Column(String(20), default="active")  # active, cancelled, expired
    starts_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    payment_ref = Column(String(100), nullable=True)
    funded_by = Column(String(100), nullable=True)  # NGO or subsidy name
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class APIUsageLog(Base):
    __tablename__ = "api_usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Float, nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    channel = Column(String(20), default="web")  # web, ussd, sms, api
    created_at = Column(DateTime(timezone=True), server_default=func.now())
