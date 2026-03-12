import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import PatternCard from '../components/PatternCard'
import AIInsightCard from '../components/AIInsightCard'
import RiskBarChart from '../components/RiskBarChart'
import Plot from 'react-plotly.js'
import type { RootCause, RiskScore } from '../types'
import { colors, plotlyLayout, plotlyConfig } from '../styles/theme'

export default function RiskAnalysis() {
  const { data: rootCauses, isLoading: causesLoading } = useQuery<RootCause[]>({
    queryKey: ['rootCauses'],
    queryFn: async () => {
      const res = await fetch('/api/risk/root-causes')
      if (!res.ok) throw new Error('Failed to fetch root causes')
      return res.json()
    },
  })

  const { data: riskScores, isLoading: scoresLoading } = useQuery<RiskScore[]>({
    queryKey: ['riskScores'],
    queryFn: async () => {
      const res = await fetch('/api/risk/scores')
      if (!res.ok) throw new Error('Failed to fetch risk scores')
      return res.json()
    },
  })

  const primaryPatterns = rootCauses?.filter(r => r.is_primary_root_cause) || []
  const supplierScores = riskScores?.filter(r => r.entity_type === 'supplier')?.sort((a, b) => a.risk_score - b.risk_score)?.slice(0, 10) || []
  const stationScores = riskScores?.filter(r => r.entity_type === 'station')?.sort((a, b) => a.risk_score - b.risk_score)?.slice(0, 10) || []

  const criticalCount = riskScores?.filter(r => r.risk_score >= 0.7).length || 0
  const warningCount = riskScores?.filter(r => r.risk_score >= 0.4 && r.risk_score < 0.7).length || 0
  const normalCount = riskScores?.filter(r => r.risk_score < 0.4).length || 0

  const aiSummary = primaryPatterns.length > 0 
    ? `Analysis has identified ${primaryPatterns.length} significant root cause patterns. The most critical finding involves ${primaryPatterns[0]?.entity_1} with a ${(primaryPatterns[0]?.correlation_strength * 100).toFixed(0)}% correlation to ${primaryPatterns[0]?.defect_type} defects. Recommended actions include immediate inspection of high-risk suppliers and process parameter optimization at flagged stations.`
    : 'Analyzing patterns...'

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-5 rounded-xl bg-critical/10 border border-critical/30">
          <p className="text-sm text-text-secondary">Critical Risk Entities</p>
          <p className="text-3xl font-bold text-critical mt-1">{criticalCount}</p>
        </div>
        <div className="p-5 rounded-xl bg-warning/10 border border-warning/30">
          <p className="text-sm text-text-secondary">Warning Level</p>
          <p className="text-3xl font-bold text-warning mt-1">{warningCount}</p>
        </div>
        <div className="p-5 rounded-xl bg-success/10 border border-success/30">
          <p className="text-sm text-text-secondary">Normal Range</p>
          <p className="text-3xl font-bold text-success mt-1">{normalCount}</p>
        </div>
      </div>

      <AIInsightCard
        title="AI Risk Summary"
        content={aiSummary}
        isLoading={causesLoading}
      />

      <div>
        <h2 className="text-lg font-semibold text-text-primary mb-4">
          Root Cause Patterns
        </h2>
        {causesLoading ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-48 rounded-xl bg-card border border-border animate-pulse" />
            ))}
          </div>
        ) : primaryPatterns.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {primaryPatterns.map((pattern, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
              >
                <PatternCard
                  title={`Pattern ${i + 1}: ${pattern.root_cause_type}`}
                  defectType={pattern.defect_type}
                  entities={[pattern.entity_1, pattern.entity_2].filter(Boolean) as string[]}
                  correlation={pattern.correlation_strength}
                  defectCount={pattern.defect_count}
                  severity={pattern.correlation_strength > 0.8 ? 'critical' : pattern.correlation_strength > 0.6 ? 'warning' : 'info'}
                />
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-text-secondary">
            No root cause patterns identified
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="rounded-xl bg-card border border-border p-6">
          <h3 className="text-lg font-semibold text-text-primary mb-4">
            Supplier Risk Scores
          </h3>
          {scoresLoading ? (
            <div className="h-64 flex items-center justify-center text-text-secondary">
              Loading...
            </div>
          ) : (
            <RiskBarChart
              data={{
                labels: supplierScores.map(s => s.entity_id),
                values: supplierScores.map(s => s.risk_score),
              }}
              height={350}
              orientation="h"
            />
          )}
        </div>

        <div className="rounded-xl bg-card border border-border p-6">
          <h3 className="text-lg font-semibold text-text-primary mb-4">
            Station Risk Scores
          </h3>
          {scoresLoading ? (
            <div className="h-64 flex items-center justify-center text-text-secondary">
              Loading...
            </div>
          ) : (
            <RiskBarChart
              data={{
                labels: stationScores.map(s => s.entity_id),
                values: stationScores.map(s => s.risk_score),
              }}
              height={350}
              orientation="h"
            />
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="rounded-xl bg-card border border-border p-6">
          <h3 className="text-lg font-semibold text-text-primary mb-4">
            Risk vs Defect Count
          </h3>
          {riskScores ? (
            <Plot
              data={[{
                type: 'scatter',
                mode: 'markers',
                x: riskScores.map(r => r.defect_count),
                y: riskScores.map(r => r.risk_score),
                marker: {
                  size: 10,
                  color: riskScores.map(r => 
                    r.risk_score >= 80 ? colors.critical : 
                    r.risk_score >= 60 ? colors.warning : colors.success
                  ),
                },
                text: riskScores.map(r => r.entity_id),
                hovertemplate: '%{text}<br>Defects: %{x}<br>Risk: %{y:.1f}<extra></extra>',
              }]}
              layout={{
                ...plotlyLayout,
                xaxis: { title: 'Defect Count', gridcolor: colors.border },
                yaxis: { title: 'Risk Score', gridcolor: colors.border },
                height: 350,
              }}
              config={plotlyConfig}
              className="w-full"
            />
          ) : null}
        </div>

        <div className="rounded-xl bg-card border border-border p-6">
          <h3 className="text-lg font-semibold text-text-primary mb-4">
            Risk Distribution
          </h3>
          <Plot
            data={[{
              type: 'pie',
              values: [criticalCount, warningCount, normalCount],
              labels: ['Critical', 'Warning', 'Normal'],
              marker: {
                colors: [colors.critical, colors.warning, colors.success],
              },
              hole: 0.5,
              textinfo: 'label+percent',
              textfont: { color: colors.text },
            }]}
            layout={{
              ...plotlyLayout,
              showlegend: false,
              height: 350,
            }}
            config={plotlyConfig}
            className="w-full"
          />
        </div>
      </div>
    </div>
  )
}
