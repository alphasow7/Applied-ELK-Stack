import { useState } from 'react'
import { useApi } from '../hooks/useApi'
import PriceChart from '../components/charts/PriceChart'
import Spinner from '../components/ui/Spinner'

const COMMODITIES = ['mil', 'sorgho', 'arachide', 'maïs', 'riz', 'niébé', 'coton', 'manioc']

interface PriceSummary {
  summary: {
    commodity: string
    avg_price_kg: number
    min_price_kg: number
    max_price_kg: number
    spread_pct: number
  }[]
}

interface PriceHistory {
  history: { date: string; price_per_kg: number }[]
}

interface TradeOpportunitiesData {
  opportunities: {
    commodity: string
    source_region: string
    destination_region: string
    source_price: number
    destination_price: number
    margin_pct: number
    opportunity_score: number
  }[]
}

export default function MarketPage() {
  const [selected, setSelected] = useState('mil')
  const [days] = useState(30)

  const { data: summary, loading: sLoading } = useApi<PriceSummary>('/market/summary')
  const { data: history, loading: hLoading } = useApi<PriceHistory>(
    `/market/prices/history/${selected}?days=${days}`,
    [selected, days]
  )
  const { data: opps } = useApi<TradeOpportunitiesData>('/market/opportunities')

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Prix du Marché</h1>
        <p className="text-gray-500 text-sm">Données en temps réel — Marchés du Sénégal</p>
      </div>

      {/* Price summary grid */}
      {sLoading ? <Spinner /> : (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {summary?.summary.map((row) => (
            <button
              key={row.commodity}
              onClick={() => setSelected(row.commodity)}
              className={`card text-left transition-all ${
                selected === row.commodity ? 'ring-2 ring-agri-500 bg-agri-50' : 'hover:bg-gray-50'
              }`}
            >
              <p className="font-semibold text-gray-800 capitalize">{row.commodity}</p>
              <p className="text-xl font-bold text-agri-700 mt-1">
                {row.avg_price_kg.toLocaleString('fr-FR')} <span className="text-xs font-normal">XOF/kg</span>
              </p>
              <p className="text-xs text-gray-400 mt-1">
                Écart: {row.spread_pct}%
              </p>
            </button>
          ))}
        </div>
      )}

      {/* Price history chart */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold capitalize">Historique des prix — {selected}</h2>
          <div className="flex gap-2">
            {COMMODITIES.map((c) => (
              <button
                key={c}
                onClick={() => setSelected(c)}
                className={`text-xs px-2 py-1 rounded ${
                  selected === c ? 'bg-agri-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {c}
              </button>
            ))}
          </div>
        </div>
        {hLoading ? <Spinner /> : history && (
          <PriceChart data={history.history} commodity={selected} />
        )}
      </div>

      {/* Trade opportunities */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Opportunités Commerciales</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left text-gray-500">
                <th className="pb-2">Culture</th>
                <th className="pb-2">Source</th>
                <th className="pb-2">Destination</th>
                <th className="pb-2 text-right">Prix source</th>
                <th className="pb-2 text-right">Prix dest.</th>
                <th className="pb-2 text-right">Marge</th>
                <th className="pb-2 text-right">Score</th>
              </tr>
            </thead>
            <tbody>
              {opps?.opportunities.slice(0, 8).map((o, i) => (
                <tr key={i} className="border-b hover:bg-gray-50">
                  <td className="py-2 font-medium capitalize">{o.commodity}</td>
                  <td className="py-2 text-gray-600">{o.source_region}</td>
                  <td className="py-2 text-gray-600">{o.destination_region}</td>
                  <td className="py-2 text-right">{o.source_price.toLocaleString('fr-FR')}</td>
                  <td className="py-2 text-right">{o.destination_price.toLocaleString('fr-FR')}</td>
                  <td className="py-2 text-right">
                    <span className="badge-green">+{o.margin_pct}%</span>
                  </td>
                  <td className="py-2 text-right">
                    <div className="flex items-center justify-end gap-1">
                      <div
                        className="h-2 rounded-full bg-agri-500"
                        style={{ width: `${o.opportunity_score}%`, maxWidth: '60px' }}
                      />
                      <span className="text-xs">{o.opportunity_score}</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
