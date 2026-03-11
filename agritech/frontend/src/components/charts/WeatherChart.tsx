import {
  ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend
} from 'recharts'

interface WeatherDay {
  date: string
  temperature_max: number
  temperature_min: number
  precipitation_mm: number
}

export default function WeatherChart({ data }: { data: WeatherDay[] }) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <ComposedChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="date" tick={{ fontSize: 11 }} tickFormatter={(v) => v.slice(5)} />
        <YAxis yAxisId="temp" tick={{ fontSize: 11 }} unit="°C" width={40} />
        <YAxis yAxisId="rain" orientation="right" tick={{ fontSize: 11 }} unit="mm" width={40} />
        <Tooltip />
        <Legend />
        <Bar yAxisId="rain" dataKey="precipitation_mm" name="Pluie (mm)" fill="#93c5fd" opacity={0.7} />
        <Line yAxisId="temp" type="monotone" dataKey="temperature_max" name="T° max" stroke="#ef4444" strokeWidth={2} dot={false} />
        <Line yAxisId="temp" type="monotone" dataKey="temperature_min" name="T° min" stroke="#3b82f6" strokeWidth={2} dot={false} />
      </ComposedChart>
    </ResponsiveContainer>
  )
}
