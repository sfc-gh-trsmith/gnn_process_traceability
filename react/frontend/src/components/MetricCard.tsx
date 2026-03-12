import { ReactNode } from 'react'
import { motion } from 'framer-motion'
import clsx from 'clsx'

interface MetricCardProps {
  label: string
  value: string | number
  icon?: ReactNode
  trend?: {
    value: number
    label: string
  }
  color?: 'primary' | 'accent' | 'purple' | 'success' | 'warning' | 'critical'
}

const colorMap = {
  primary: 'from-primary/20 to-primary/5 border-primary/30',
  accent: 'from-accent/20 to-accent/5 border-accent/30',
  purple: 'from-purple/20 to-purple/5 border-purple/30',
  success: 'from-success/20 to-success/5 border-success/30',
  warning: 'from-warning/20 to-warning/5 border-warning/30',
  critical: 'from-critical/20 to-critical/5 border-critical/30',
}

const iconColorMap = {
  primary: 'text-primary',
  accent: 'text-accent',
  purple: 'text-purple',
  success: 'text-success',
  warning: 'text-warning',
  critical: 'text-critical',
}

export default function MetricCard({ label, value, icon, trend, color = 'primary' }: MetricCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={clsx(
        'relative overflow-hidden rounded-xl border p-6',
        'bg-gradient-to-br',
        colorMap[color]
      )}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-text-secondary">{label}</p>
          <p className="mt-2 text-3xl font-bold text-text-primary">
            {typeof value === 'number' ? value.toLocaleString() : value}
          </p>
          {trend && (
            <p className={clsx(
              'mt-2 text-sm',
              trend.value >= 0 ? 'text-success' : 'text-critical'
            )}>
              {trend.value >= 0 ? '+' : ''}{trend.value}% {trend.label}
            </p>
          )}
        </div>
        {icon && (
          <div className={clsx('p-2 rounded-lg bg-card/50', iconColorMap[color])}>
            {icon}
          </div>
        )}
      </div>
    </motion.div>
  )
}
