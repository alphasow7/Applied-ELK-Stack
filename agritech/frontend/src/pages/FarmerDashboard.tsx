import { useApi } from '../hooks/useApi'
import StatCard from '../components/ui/StatCard'
import RiskBadge from '../components/ui/RiskBadge'
import WeatherChart from '../components/charts/WeatherChart'
import Spinner from '../components/ui/Spinner'

interface DashboardData {
  summary: {
    total_farms: number
    total_area_ha: number
    active_crops: number
    total_predicted_yield_kg: number
  }
  farms: { id: number; name: string; region: string; area_ha: number; crops: string[] }[]
  user: { name: string; subscription: string }
}

interface WeatherData {
  forecast: {
    daily: {
      time: string[]
      temperature_2m_max: number[]
      temperature_2m_min: number[]
      precipitation_sum: number[]
    }
  }
}

export default function FarmerDashboard() {
  const { data: dashboard, loading: dLoading } = useApi<DashboardData>('/farmers/dashboard')
  const { data: weather } = useApi<WeatherData>('/weather/region/Thiès')

  const weatherDays = weather?.forecast?.daily
    ? weather.forecast.daily.time.map((date, i) => ({
        date,
        temperature_max: weather.forecast.daily.temperature_2m_max[i],
        temperature_min: weather.forecast.daily.temperature_2m_min[i],
        precipitation_mm: weather.forecast.daily.precipitation_sum[i],
      }))
    : []

  if (dLoading) return <Spinner size="lg" />

  const s = dashboard?.summary

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Bonjour, {dashboard?.user.name} 👋
        </h1>
        <p className="text-gray-500 text-sm mt-1">Plan: {dashboard?.user.subscription} · Tableau de bord agriculteur</p>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Mes champs" value={s?.total_farms ?? 0} icon="🌾" color="green" />
        <StatCard title="Surface totale" value={`${s?.total_area_ha ?? 0} ha`} icon="📐" color="blue" />
        <StatCard title="Cultures actives" value={s?.active_crops ?? 0} icon="🌱" color="amber" />
        <StatCard
          title="Rendement prévu"
          value={`${((s?.total_predicted_yield_kg ?? 0) / 1000).toFixed(1)} t`}
          icon="📦"
          color="green"
        />
      </div>

      {/* Farms list */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Mes Champs</h2>
        {dashboard?.farms.length === 0 ? (
          <p className="text-gray-400 text-sm">Aucun champ enregistré.</p>
        ) : (
          <div className="space-y-3">
            {dashboard?.farms.map((farm) => (
              <div key={farm.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-sm">{farm.name}</p>
                  <p className="text-xs text-gray-500">{farm.region} · {farm.area_ha} ha</p>
                </div>
                <div className="flex gap-1 flex-wrap justify-end">
                  {farm.crops.map((c) => (
                    <span key={c} className="badge-blue text-xs">{c}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Weather */}
      {weatherDays.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Prévisions Météo — 7 jours</h2>
          <WeatherChart data={weatherDays} />
        </div>
      )}

      {/* USSD reminder */}
      <div className="card bg-agri-50 border-agri-200">
        <div className="flex items-center gap-4">
          <span className="text-3xl">📱</span>
          <div>
            <p className="font-semibold text-agri-800">Accès USSD disponible</p>
            <p className="text-sm text-agri-600">
              Consultez vos prévisions et les prix du marché sur tout téléphone via{' '}
              <span className="font-mono font-bold">*384*123#</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
