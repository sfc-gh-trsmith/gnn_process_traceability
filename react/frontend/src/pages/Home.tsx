import { useQuery } from '@tanstack/react-query'
import { Package, AlertTriangle, Users, Lightbulb, ArrowRight } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import MetricCard from '../components/MetricCard'
import PatternCard from '../components/PatternCard'
import SankeyDiagram from '../components/SankeyDiagram'
import type { DashboardMetrics, ManufacturingFlow, RootCause } from '../types'

export default function Home() {
  const navigate = useNavigate()

  const { data: metrics, isLoading: metricsLoading } = useQuery<DashboardMetrics>({
    queryKey: ['metrics'],
    queryFn: async () => {
      const res = await fetch('/api/summary/metrics')
      if (!res.ok) throw new Error('Failed to fetch metrics')
      return res.json()
    },
  })

  const { data: flow, isLoading: flowLoading } = useQuery<ManufacturingFlow>({
    queryKey: ['flow'],
    queryFn: async () => {
      const res = await fetch('/api/network/flow')
      if (!res.ok) throw new Error('Failed to fetch flow')
      return res.json()
    },
  })

  const { data: patterns, isLoading: patternsLoading } = useQuery<RootCause[]>({
    queryKey: ['patterns'],
    queryFn: async () => {
      const res = await fetch('/api/risk/root-causes')
      if (!res.ok) throw new Error('Failed to fetch patterns')
      return res.json()
    },
  })

  const topPatterns = patterns?.filter(p => p.is_primary_root_cause).slice(0, 2) || []

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="Work Orders"
          value={metricsLoading ? '...' : metrics?.workOrders ?? 0}
          icon={<Package className="w-5 h-5" />}
          color="primary"
        />
        <MetricCard
          label="Total Defects"
          value={metricsLoading ? '...' : metrics?.defects ?? 0}
          icon={<AlertTriangle className="w-5 h-5" />}
          color="critical"
        />
        <MetricCard
          label="Active Suppliers"
          value={metricsLoading ? '...' : metrics?.suppliers ?? 0}
          icon={<Users className="w-5 h-5" />}
          color="accent"
        />
        <MetricCard
          label="Patterns Found"
          value={metricsLoading ? '...' : metrics?.patternsFound ?? 0}
          icon={<Lightbulb className="w-5 h-5" />}
          color="purple"
        />
      </div>

      <div className="rounded-xl bg-card border border-border p-6">
        <h2 className="text-lg font-semibold text-text-primary mb-4">
          Manufacturing Supply Chain Flow
        </h2>
        {flowLoading ? (
          <div className="h-96 flex items-center justify-center text-text-secondary">
            Loading flow diagram...
          </div>
        ) : flow ? (
          <SankeyDiagram data={flow} height={400} />
        ) : (
          <div className="h-96 flex items-center justify-center text-text-secondary">
            No flow data available
          </div>
        )}
      </div>

      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-text-primary">
            Discovered Root Cause Patterns
          </h2>
          <button
            onClick={() => navigate('/risk')}
            className="flex items-center gap-2 text-sm text-primary hover:text-primary/80 transition-colors"
          >
            View All <ArrowRight className="w-4 h-4" />
          </button>
        </div>

        {patternsLoading ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {[1, 2].map(i => (
              <div key={i} className="h-48 rounded-xl bg-card border border-border animate-pulse" />
            ))}
          </div>
        ) : topPatterns.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {topPatterns.map((pattern, i) => (
              <PatternCard
                key={i}
                title={`Pattern ${i + 1}: ${pattern.root_cause_type}`}
                defectType={pattern.defect_type}
                entities={[pattern.entity_1, pattern.entity_2].filter(Boolean) as string[]}
                correlation={pattern.correlation_strength}
                defectCount={pattern.defect_count}
                severity={pattern.correlation_strength > 0.8 ? 'critical' : 'warning'}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-text-secondary">
            No patterns discovered yet
          </div>
        )}
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Explore Process Network', path: '/network', color: 'bg-primary/10 hover:bg-primary/20 text-primary' },
          { label: 'Trace Defects', path: '/defects', color: 'bg-critical/10 hover:bg-critical/20 text-critical' },
          { label: 'Analyze Risk', path: '/risk', color: 'bg-warning/10 hover:bg-warning/20 text-warning' },
          { label: 'Learn More', path: '/about', color: 'bg-purple/10 hover:bg-purple/20 text-purple' },
        ].map((action) => (
          <button
            key={action.path}
            onClick={() => navigate(action.path)}
            className={`p-4 rounded-xl font-medium transition-colors ${action.color}`}
          >
            {action.label}
          </button>
        ))}
      </div>
    </div>
  )
}
