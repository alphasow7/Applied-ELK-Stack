export default function RiskBadge({ level }: { level: 'low' | 'medium' | 'high' }) {
  const cfg = {
    low: { cls: 'badge-green', label: 'Faible' },
    medium: { cls: 'badge-yellow', label: 'Moyen' },
    high: { cls: 'badge-red', label: 'Élevé' },
  }
  const { cls, label } = cfg[level]
  return <span className={cls}>{label}</span>
}
