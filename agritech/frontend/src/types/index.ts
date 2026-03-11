export interface User {
  id: number
  phone_number: string
  full_name: string
  email?: string
  role: 'farmer' | 'cooperative' | 'buyer' | 'insurer' | 'admin'
  subscription_tier: 'free' | 'cooperative' | 'enterprise' | 'insurer'
}

export interface Farm {
  id: number
  name: string
  latitude: number
  longitude: number
  area_hectares: number
  region: string
  soil_type?: string
  irrigation: boolean
  crop_count: number
}

export interface Crop {
  id: number
  crop_type: string
  planting_date: string
  expected_harvest_date?: string
  area_planted_hectares: number
  status: 'planted' | 'growing' | 'harvested'
  latest_prediction?: YieldPrediction
}

export interface YieldPrediction {
  predicted_yield_kg: number
  confidence_score: number
  risk_level: 'low' | 'medium' | 'high'
  recommendation: string
  drought_risk?: number
  flood_risk?: number
  pest_risk?: number
}

export interface MarketPrice {
  commodity: string
  market_name: string
  region: string
  price_per_kg: number
  currency: string
  recorded_at: string
}

export interface MarketTrend {
  commodity: string
  avg_price: number
  min_price: number
  max_price: number
  price_change_pct: number
  demand_level: 'low' | 'normal' | 'high'
  supply_level: 'low' | 'normal' | 'high'
  forecast_7d: number
  forecast_30d: number
  analysis: string
  best_selling_markets: { market: string; region: string; price_per_kg: number }[]
}

export interface WeatherDay {
  date: string
  temperature_max: number
  temperature_min: number
  precipitation_mm: number
  evapotranspiration?: number
}

export interface SoilHealth {
  ph_level: number
  organic_matter_pct: number
  nitrogen_level: string
  ndvi_index: number
  health_score: number
  erosion_risk: string
  recommendation: string
}

export interface TradeOpportunity {
  commodity: string
  source_region: string
  destination_region: string
  source_price: number
  destination_price: number
  margin_pct: number
  opportunity_score: number
}

export interface AuthState {
  token: string | null
  user: User | null
}
