import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts'

interface PricePoint {
  date: string
  price_per_kg: number
}

interface Props {
  data: PricePoint[]
  commodity: string
}

export default function PriceChart({ data, commodity }: Props) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={data} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 11 }}
          tickFormatter={(v) => v.slice(5)} // MM-DD
        />
        <YAxis
          tick={{ fontSize: 11 }}
          tickFormatter={(v) => `${v} XOF`}
          width={75}
        />
        <Tooltip
          formatter={(v: number) => [`${v.toLocaleString('fr-FR')} XOF/kg`, commodity]}
          labelFormatter={(l) => `Date: ${l}`}
        />
        <Legend />
        <Line
          type="monotone"
          dataKey="price_per_kg"
          name={`Prix ${commodity}`}
          stroke="#16a34a"
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 4 }}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
