import clsx from 'clsx'

interface StatCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon?: string
  trend?: 'up' | 'down' | 'neutral'
  trendValue?: string
  color?: 'green' | 'blue' | 'amber' | 'red'
}

export default function StatCard({ title, value, subtitle, icon, trend, trendValue, color = 'green' }: StatCardProps) {
  const colors = {
    green: 'bg-agri-50 text-agri-700 border-agri-100',
    blue: 'bg-blue-50 text-blue-700 border-blue-100',
    amber: 'bg-amber-50 text-amber-700 border-amber-100',
    red: 'bg-red-50 text-red-700 border-red-100',
  }
  return (
    <div className={clsx('card border', colors[color])}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium opacity-80">{title}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
          {subtitle && <p className="text-xs opacity-70 mt-1">{subtitle}</p>}
        </div>
        {icon && <span className="text-3xl opacity-60">{icon}</span>}
      </div>
      {trend && trendValue && (
        <div className="mt-3 flex items-center text-xs">
          <span className={trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-gray-500'}>
            {trend === 'up' ? '▲' : trend === 'down' ? '▼' : '→'} {trendValue}
          </span>
        </div>
      )}
    </div>
  )
}
