import { motion } from 'framer-motion'
import clsx from 'clsx'

interface PatternCardProps {
  title: string
  defectType: string
  entities: string[]
  correlation: number
  defectCount: number
  severity: 'critical' | 'warning' | 'info'
}

const severityStyles = {
  critical: {
    border: 'border-l-critical',
    badge: 'bg-critical/20 text-critical',
    text: 'Critical',
  },
  warning: {
    border: 'border-l-warning',
    badge: 'bg-warning/20 text-warning',
    text: 'Warning',
  },
  info: {
    border: 'border-l-primary',
    badge: 'bg-primary/20 text-primary',
    text: 'Info',
  },
}

export default function PatternCard({
  title,
  defectType,
  entities,
  correlation,
  defectCount,
  severity,
}: PatternCardProps) {
  const style = severityStyles[severity]

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className={clsx(
        'rounded-lg bg-card border border-border border-l-4 p-5',
        style.border
      )}
    >
      <div className="flex items-start justify-between mb-3">
        <h3 className="font-semibold text-text-primary">{title}</h3>
        <span className={clsx('px-2 py-0.5 rounded text-xs font-medium', style.badge)}>
          {style.text}
        </span>
      </div>

      <div className="space-y-2 text-sm">
        <div className="flex items-center gap-2">
          <span className="text-text-secondary">Defect Type:</span>
          <span className="text-accent font-medium">{defectType}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-text-secondary">Entities:</span>
          <span className="text-text-primary">{entities.join(' + ')}</span>
        </div>
      </div>

      <div className="flex gap-6 mt-4 pt-4 border-t border-border">
        <div>
          <p className="text-xs text-text-secondary">Correlation</p>
          <p className="text-lg font-semibold text-primary">{(correlation * 100).toFixed(0)}%</p>
        </div>
        <div>
          <p className="text-xs text-text-secondary">Defects</p>
          <p className="text-lg font-semibold text-text-primary">{defectCount}</p>
        </div>
      </div>
    </motion.div>
  )
}
