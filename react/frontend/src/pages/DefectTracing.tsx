import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import RiskBarChart from '../components/RiskBarChart'
import ParetoChart from '../components/ParetoChart'
import BubbleChart from '../components/BubbleChart'
import SankeyDiagram from '../components/SankeyDiagram'
import type { DefectTypeCount, ManufacturingFlow, SupplierBatchCorrelation, SupplierDefectBubble, StationCorrelation, ProcessStepCorrelation, RiskScore } from '../types'
import { colors } from '../styles/theme'

export default function DefectTracing() {
  const { data: defectTypes, isLoading: typesLoading } = useQuery<DefectTypeCount[]>({
    queryKey: ['defectTypes'],
    queryFn: async () => {
      const res = await fetch('/api/defects/type-counts')
      if (!res.ok) throw new Error('Failed to fetch defect types')
      return res.json()
    },
  })

  const { data: defectFlow } = useQuery<ManufacturingFlow>({
    queryKey: ['defectFlow'],
    queryFn: async () => {
      const res = await fetch('/api/network/flow')
      if (!res.ok) throw new Error('Failed to fetch flow')
      return res.json()
    },
  })

  const { data: supplierBatch } = useQuery<SupplierBatchCorrelation[]>({
    queryKey: ['supplierBatch'],
    queryFn: async () => {
      const res = await fetch('/api/risk/supplier-batch')
      if (!res.ok) throw new Error('Failed to fetch supplier batch')
      return res.json()
    },
  })

  const { data: stationData } = useQuery<StationCorrelation[]>({
    queryKey: ['stationData'],
    queryFn: async () => {
      const res = await fetch('/api/risk/station')
      if (!res.ok) throw new Error('Failed to fetch station data')
      return res.json()
    },
  })

  const { data: processSteps } = useQuery<ProcessStepCorrelation[]>({
    queryKey: ['processSteps'],
    queryFn: async () => {
      const res = await fetch('/api/risk/process-steps')
      if (!res.ok) throw new Error('Failed to fetch process steps')
      return res.json()
    },
  })

  const { data: riskScores } = useQuery<RiskScore[]>({
    queryKey: ['riskScores'],
    queryFn: async () => {
      const res = await fetch('/api/risk/scores')
      if (!res.ok) throw new Error('Failed to fetch risk scores')
      return res.json()
    },
  })

  const { data: bubbleData } = useQuery<SupplierDefectBubble[]>({
    queryKey: ['supplierDefectBubble'],
    queryFn: async () => {
      const res = await fetch('/api/risk/supplier-defect-bubble')
      if (!res.ok) throw new Error('Failed to fetch bubble data')
      return res.json()
    },
  })

  const aggregatedSupplierBatch = supplierBatch

  const filteredStations = stationData?.sort((a, b) => a.lift_ratio - b.lift_ratio)?.slice(0, 10)

  const filteredSteps = processSteps?.sort((a, b) => a.defect_rate - b.defect_rate)?.slice(0, 10)

  const topRiskyAssets = riskScores
    ?.filter(d => d.entity_type === 'station')
    ?.sort((a, b) => a.risk_score - b.risk_score)
    ?.slice(0, 10)

  return (
    <div className="space-y-6">
      <div className="rounded-xl bg-card border border-border p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-semibold text-text-primary">
              Defect Type Overview
            </h2>
            <p className="text-sm text-text-secondary mt-1">
              Total defects recorded by type across all work orders
            </p>
          </div>
        </div>

        {typesLoading ? (
          <div className="h-64 flex items-center justify-center text-text-secondary">
            Loading...
          </div>
        ) : defectTypes ? (
          (() => {
            const sortedDefectTypes = [...defectTypes].sort((a, b) => a.defect_count - b.defect_count)
            return (
              <RiskBarChart
                data={{
                  labels: sortedDefectTypes.map(d => d.defect_type),
                  values: sortedDefectTypes.map(d => d.defect_count),
                  colors: sortedDefectTypes.map(() => colors.critical),
                }}
                height={300}
                orientation="h"
              />
            )
          })()
        ) : null}
      </div>

      <div className="rounded-xl bg-card border border-border p-6">
        <h2 className="text-lg font-semibold text-text-primary mb-4">
          Manufacturing Defect Flow
        </h2>
        {defectFlow ? (
          <SankeyDiagram data={defectFlow} height={350} />
        ) : (
          <div className="h-64 flex items-center justify-center text-text-secondary">
            Loading flow...
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-xl bg-card border border-border p-6"
        >
          <h3 className="text-lg font-semibold text-text-primary">
            Supplier-Batch Defect Pareto
          </h3>
          <p className="text-sm text-text-secondary mt-1 mb-4">
            Top supplier/batch combinations by defect count. Red bars contribute to 80% of defects.
          </p>
          {aggregatedSupplierBatch?.length ? (
            <ParetoChart
              data={{
                labels: aggregatedSupplierBatch.map(d => `${d.supplier_name.split(' ')[0]} ${d.batch_id}`),
                values: aggregatedSupplierBatch.map(d => d.defect_count),
                cumulativePct: aggregatedSupplierBatch.map(d => d.cumulative_pct),
              }}
              height={320}
            />
          ) : (
            <div className="h-48 flex items-center justify-center text-text-secondary">
              No data
            </div>
          )}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="rounded-xl bg-card border border-border p-6"
        >
          <h3 className="text-lg font-semibold text-text-primary mb-4">
            Stations & Lines
          </h3>
          {filteredStations?.length ? (
            <RiskBarChart
              data={{
                labels: filteredStations.map(d => `${d.station_name}\n${d.line_id}`),
                values: filteredStations.map(d => d.lift_ratio),
                colors: filteredStations.map(d => 
                  d.lift_ratio > 2 ? colors.critical : d.lift_ratio > 1.5 ? colors.warning : colors.success
                ),
              }}
              title="Lift Ratio (vs Expected)"
              height={300}
              orientation="h"
            />
          ) : (
            <div className="h-48 flex items-center justify-center text-text-secondary">
              No data
            </div>
          )}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="rounded-xl bg-card border border-border p-6"
        >
          <h3 className="text-lg font-semibold text-text-primary mb-4">
            Process Steps
          </h3>
          {filteredSteps?.length ? (
            <RiskBarChart
              data={{
                labels: filteredSteps.map(d => d.step_name),
                values: filteredSteps.map(d => d.defect_rate * 100),
                colors: filteredSteps.map(d => 
                  d.defect_rate > 0.15 ? colors.critical : d.defect_rate > 0.1 ? colors.warning : colors.success
                ),
              }}
              title="Defect Rate (%)"
              height={300}
              orientation="h"
            />
          ) : (
            <div className="h-48 flex items-center justify-center text-text-secondary">
              No data
            </div>
          )}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="rounded-xl bg-card border border-border p-6"
        >
          <h3 className="text-lg font-semibold text-text-primary mb-4">
            Top Risky Assets
          </h3>
          {topRiskyAssets?.length ? (
            <RiskBarChart
              data={{
                labels: topRiskyAssets.map(d => d.entity_id),
                values: topRiskyAssets.map(d => d.risk_score),
                colors: topRiskyAssets.map(d => 
                  d.risk_score > 0.5 ? colors.critical : d.risk_score > 0.3 ? colors.warning : colors.success
                ),
              }}
              title="Risk Score"
              height={300}
              orientation="h"
            />
          ) : (
            <div className="h-48 flex items-center justify-center text-text-secondary">
              No data
            </div>
          )}
        </motion.div>
      </div>

      <div className="rounded-xl bg-card border border-border p-6">
        <h3 className="text-lg font-semibold text-text-primary">
          Supplier vs Defect Type
        </h3>
        <p className="text-sm text-text-secondary mt-1 mb-4">
          Bubble size = defect count, color = material type
        </p>
        {bubbleData?.length ? (
          <BubbleChart
            data={{
              x: bubbleData.map(d => d.supplier_name.split(' ')[0]),
              y: bubbleData.map(d => d.defect_type.replace(/_/g, ' ')),
              sizes: bubbleData.map(d => d.defect_count),
              colors: bubbleData.map(d => d.material_type),
              text: bubbleData.map(d => `${d.supplier_name}<br>${d.defect_type}<br>${d.material_type}: ${d.defect_count} defects`),
            }}
            height={450}
          />
        ) : (
          <div className="h-64 flex items-center justify-center text-text-secondary">
            No data
          </div>
        )}
      </div>
    </div>
  )
}
