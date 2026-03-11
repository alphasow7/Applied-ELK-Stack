import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'

interface SupplyRow {
  commodity: string
  predicted_volume_tonnes: number
  confidence: number
  drought_risk: number
}

const COLORS = ['#16a34a', '#22c55e', '#4ade80', '#86efac', '#bbf7d0', '#d97706', '#b45309', '#92400e']

export default function SupplyForecastChart({ data }: { data: SupplyRow[] }) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={data} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="commodity" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 11 }} unit="t" width={55} />
        <Tooltip
          formatter={(v: number) => [`${v.toLocaleString('fr-FR')} tonnes`, 'Volume prévu']}
        />
        <Bar dataKey="predicted_volume_tonnes" name="Volume prévu (t)" radius={[4, 4, 0, 0]}>
          {data.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
