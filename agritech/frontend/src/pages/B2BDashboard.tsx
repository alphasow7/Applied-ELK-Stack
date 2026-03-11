import { useApi } from '../hooks/useApi'
import StatCard from '../components/ui/StatCard'
import SupplyForecastChart from '../components/charts/SupplyForecastChart'
import RiskBadge from '../components/ui/RiskBadge'
import Spinner from '../components/ui/Spinner'
import FarmMap from '../components/maps/FarmMap'

interface OverviewData {
  platform_stats: {
    total_farmers: number
    total_farms: number
    total_area_ha: number
    active_crops: number
    total_predicted_yield_tonnes: number
  }
  market_snapshot: { commodity: string; avg_price_xof_kg: number; trend: string }[]
}

interface SupplyData {
  supply_forecast: {
    commodity: string
    active_fields: number
    total_area_ha: number
    predicted_volume_tonnes: number
    confidence: number
    drought_risk: number
  }[]
}

interface RiskData {
  risk_heatmap: {
    region: string
    commodity: string
    drought_risk: number
    flood_risk: number
    pest_risk: number
    composite_risk: number
    fields_affected: number
  }[]
}

// Exploitations démo — 4 régions naturelles de Guinée
const GUINEE_FARMS = [
  // Basse-Guinée (Guinée Maritime)
  { id: 1, name: 'Expl. Mamadou', latitude:  9.55, longitude: -13.68, region: 'Basse-Guinée',      crop_type: 'riz',              risk_level: 'low'    as const, predicted_yield_kg: 4400 },
  { id: 2, name: 'Expl. Kadiatou', latitude: 10.05, longitude: -12.87, region: 'Basse-Guinée',     crop_type: 'manioc',           risk_level: 'medium' as const, predicted_yield_kg: 15000 },
  // Moyenne-Guinée (Futa Djalon)
  { id: 3, name: 'Expl. Aissatou', latitude: 11.32, longitude: -12.29, region: 'Moyenne-Guinée',   crop_type: 'fonio',            risk_level: 'low'    as const, predicted_yield_kg: 640 },
  { id: 4, name: 'Expl. Ibrahima', latitude: 10.38, longitude: -12.08, region: 'Moyenne-Guinée',   crop_type: 'maïs',             risk_level: 'medium' as const, predicted_yield_kg: 3200 },
  // Haute-Guinée
  { id: 5, name: 'Expl. Fatoumata', latitude: 10.39, longitude:  -9.31, region: 'Haute-Guinée',   crop_type: 'arachide',         risk_level: 'medium' as const, predicted_yield_kg: 1760 },
  { id: 6, name: 'Expl. Sékou',     latitude: 11.42, longitude:  -9.17, region: 'Haute-Guinée',   crop_type: 'maïs',             risk_level: 'high'   as const, predicted_yield_kg: 1200 },
  // Guinée Forestière
  { id: 7, name: 'Expl. Mariama',   latitude:  7.75, longitude:  -8.82, region: 'Guinée Forestière', crop_type: 'café',           risk_level: 'low'    as const, predicted_yield_kg: 900 },
  { id: 8, name: 'Expl. Oumar',     latitude:  8.55, longitude: -10.13, region: 'Guinée Forestière', crop_type: 'banane_plantain', risk_level: 'medium' as const, predicted_yield_kg: 24000 },
]

export default function B2BDashboard() {
  const { data: overview, loading: oLoading } = useApi<OverviewData>('/analytics/overview')
  const { data: supply, loading: sLoading } = useApi<SupplyData>('/analytics/supply-forecast')
  const { data: risk, loading: rLoading } = useApi<RiskData>('/analytics/risk-heatmap')

  const stats = overview?.platform_stats

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Tableau de Bord B2B — Guinée</h1>
        <p className="text-gray-500 text-sm">Vue plateforme — coopératives, exportateurs & acheteurs industriels · Basse-Guinée · Moyenne-Guinée · Haute-Guinée · Guinée Forestière</p>
      </div>

      {oLoading ? <Spinner /> : (
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
          <StatCard title="Agriculteurs" value={stats?.total_farmers ?? 0} icon="👨‍🌾" color="green" />
          <StatCard title="Champs" value={stats?.total_farms ?? 0} icon="🌾" color="green" />
          <StatCard title="Surface totale" value={`${stats?.total_area_ha ?? 0} ha`} icon="📐" color="blue" />
          <StatCard title="Cultures actives" value={stats?.active_crops ?? 0} icon="🌱" color="amber" />
          <StatCard
            title="Volume prévu"
            value={`${stats?.total_predicted_yield_tonnes ?? 0} t`}
            icon="📦"
            color="green"
          />
        </div>
      )}

      {/* Market snapshot */}
      {overview && (
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Snapshot Marché</h2>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {overview.market_snapshot.map((m) => (
              <div key={m.commodity} className="text-center bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-500 capitalize">{m.commodity}</p>
                <p className="text-lg font-bold text-agri-700">{m.avg_price_xof_kg.toLocaleString('fr-FR')}</p>
                <p className="text-xs text-gray-400">GNF/kg</p>
                <span className={`text-xs ${m.trend === 'up' ? 'text-green-600' : 'text-red-500'}`}>
                  {m.trend === 'up' ? '▲' : '▼'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Supply forecast chart */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Prévision d'Offre par Culture</h2>
        {sLoading ? <Spinner /> : supply && (
          <SupplyForecastChart data={supply.supply_forecast} />
        )}
        {supply && (
          <div className="overflow-x-auto mt-4">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-gray-500">
                  <th className="pb-2">Culture</th>
                  <th className="pb-2 text-right">Champs</th>
                  <th className="pb-2 text-right">Surface (ha)</th>
                  <th className="pb-2 text-right">Volume (t)</th>
                  <th className="pb-2 text-right">Confiance</th>
                  <th className="pb-2 text-right">Risque sécheresse</th>
                </tr>
              </thead>
              <tbody>
                {supply.supply_forecast.map((row) => (
                  <tr key={row.commodity} className="border-b hover:bg-gray-50">
                    <td className="py-2 font-medium capitalize">{row.commodity}</td>
                    <td className="py-2 text-right">{row.active_fields}</td>
                    <td className="py-2 text-right">{row.total_area_ha}</td>
                    <td className="py-2 text-right font-semibold">{row.predicted_volume_tonnes}</td>
                    <td className="py-2 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <div className="w-16 h-2 bg-gray-100 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-agri-500 rounded-full"
                            style={{ width: `${row.confidence * 100}%` }}
                          />
                        </div>
                        <span>{Math.round(row.confidence * 100)}%</span>
                      </div>
                    </td>
                    <td className="py-2 text-right">
                      <RiskBadge level={row.drought_risk > 0.5 ? 'high' : row.drought_risk > 0.25 ? 'medium' : 'low'} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Farm map */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Carte des Exploitations</h2>
        <FarmMap farms={GUINEE_FARMS} />
      </div>

      {/* Risk heatmap */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Risques par Région & Culture</h2>
        {rLoading ? <Spinner /> : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-gray-500">
                  <th className="pb-2">Région</th>
                  <th className="pb-2">Culture</th>
                  <th className="pb-2 text-right">Sécheresse</th>
                  <th className="pb-2 text-right">Inondation</th>
                  <th className="pb-2 text-right">Ravageurs</th>
                  <th className="pb-2 text-right">Risque global</th>
                  <th className="pb-2 text-right">Champs</th>
                </tr>
              </thead>
              <tbody>
                {risk?.risk_heatmap.map((r, i) => (
                  <tr key={i} className="border-b hover:bg-gray-50">
                    <td className="py-2">{r.region}</td>
                    <td className="py-2 capitalize">{r.commodity}</td>
                    <td className="py-2 text-right">
                      <RiskBadge level={r.drought_risk > 0.5 ? 'high' : r.drought_risk > 0.25 ? 'medium' : 'low'} />
                    </td>
                    <td className="py-2 text-right">
                      <RiskBadge level={r.flood_risk > 0.5 ? 'high' : r.flood_risk > 0.25 ? 'medium' : 'low'} />
                    </td>
                    <td className="py-2 text-right">
                      <RiskBadge level={r.pest_risk > 0.5 ? 'high' : r.pest_risk > 0.25 ? 'medium' : 'low'} />
                    </td>
                    <td className="py-2 text-right">
                      <RiskBadge level={r.composite_risk > 0.5 ? 'high' : r.composite_risk > 0.25 ? 'medium' : 'low'} />
                    </td>
                    <td className="py-2 text-right text-gray-500">{r.fields_affected}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
