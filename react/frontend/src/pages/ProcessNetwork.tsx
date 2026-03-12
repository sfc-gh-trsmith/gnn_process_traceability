import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import HeatmapChart from '../components/HeatmapChart'
import RiskBarChart from '../components/RiskBarChart'
import NetworkGraph from '../components/NetworkGraph'
import type { RiskScore, NetworkGraph as NetworkGraphType, SupplierDefectHeatmap, StationCorrelation } from '../types'

const tabs = ['Discovery Heatmaps', 'Risk Analysis', 'Network Graph', 'Algorithm Trace']

export default function ProcessNetwork() {
  const [activeTab, setActiveTab] = useState(0)
  const [sampleSize, setSampleSize] = useState(50)

  const { data: riskScores, isLoading: riskLoading } = useQuery<RiskScore[]>({
    queryKey: ['riskScores'],
    queryFn: async () => {
      const res = await fetch('/api/risk/scores')
      if (!res.ok) throw new Error('Failed to fetch risk scores')
      return res.json()
    },
  })

  const { data: networkData, isLoading: networkLoading } = useQuery<NetworkGraphType>({
    queryKey: ['network', sampleSize],
    queryFn: async () => {
      const res = await fetch(`/api/network/graph?sample_size=${sampleSize}`)
      if (!res.ok) throw new Error('Failed to fetch network')
      return res.json()
    },
  })

  const { data: supplierDefectData } = useQuery<SupplierDefectHeatmap[]>({
    queryKey: ['supplierDefectHeatmap'],
    queryFn: async () => {
      const res = await fetch('/api/risk/supplier-defect-heatmap')
      if (!res.ok) throw new Error('Failed to fetch supplier defect heatmap')
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

  const supplierHeatmapData = {
    x: [...new Set(supplierDefectData?.map(d => d.defect_type) || [])],
    y: [...new Set(supplierDefectData?.map(d => d.supplier_name) || [])],
    z: [] as number[][],
  }

  if (supplierDefectData) {
    const defectTypes = supplierHeatmapData.x
    const suppliers = supplierHeatmapData.y
    supplierHeatmapData.z = suppliers.map(s => {
      return defectTypes.map(d => {
        const match = supplierDefectData.find(item => 
          item.supplier_name === s && item.defect_type === d
        )
        return match?.defect_count || 0
      })
    })
  }

  const limitedStationData = stationData?.slice(0, 15)
  const stationHeatmapData = {
    x: [...new Set(limitedStationData?.map(d => d.defect_type) || [])],
    y: [...new Set(limitedStationData?.map(d => `${d.station_name} - ${d.line_id}`) || [])],
    z: [] as number[][],
  }
  
  if (limitedStationData) {
    const defectTypes = stationHeatmapData.x
    const stations = stationHeatmapData.y
    stationHeatmapData.z = stations.map(s => {
      return defectTypes.map(d => {
        const match = limitedStationData.find(item => 
          `${item.station_name} - ${item.line_id}` === s && item.defect_type === d
        )
        return match?.defect_count || 0
      })
    })
  }

  const topRiskScores = riskScores?.sort((a, b) => a.risk_score - b.risk_score)?.slice(0, 10) || []

  return (
    <div className="space-y-6">
      <div className="flex gap-2 border-b border-border pb-1">
        {tabs.map((tab, i) => (
          <button
            key={tab}
            onClick={() => setActiveTab(i)}
            className={`px-4 py-2 rounded-t-lg font-medium transition-colors ${
              activeTab === i
                ? 'bg-card text-primary border border-border border-b-0'
                : 'text-text-secondary hover:text-text-primary'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      <motion.div
        key={activeTab}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2 }}
      >
        {activeTab === 0 && (
          <div className="space-y-6">
            <div className="rounded-xl bg-card border border-border p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Supplier vs Defect Type
              </h3>
              <HeatmapChart
                data={supplierHeatmapData}
                xLabel="Defect Type"
                yLabel="Supplier"
                height={400}
              />
            </div>
            <div className="rounded-xl bg-card border border-border p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Station/Line vs Defect Type
              </h3>
              <HeatmapChart
                data={stationHeatmapData}
                xLabel="Defect Type"
                yLabel="Station - Line"
                height={400}
              />
            </div>
          </div>
        )}

        {activeTab === 1 && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="rounded-xl bg-card border border-border p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-2">
                Top 10 Risk Stations
              </h3>
              <p className="text-sm text-text-secondary mb-4">
                Process stations ranked by GNN-computed risk score. Higher scores indicate stronger correlation with defects. Investigate stations scoring above 0.4.
              </p>
              {riskLoading ? (
                <div className="h-64 flex items-center justify-center text-text-secondary">
                  Loading...
                </div>
              ) : (
                <RiskBarChart
                  data={{
                    labels: topRiskScores.map(r => r.entity_id),
                    values: topRiskScores.map(r => r.risk_score),
                  }}
                  title="Top 10 Risk Entities"
                  height={350}
                  orientation="h"
                />
              )}
            </div>
            <div className="rounded-xl bg-card border border-border p-6">
              <h3 className="text-lg font-semibold text-text-primary mb-4">
                Risk Summary
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 rounded-lg bg-critical/10 border border-critical/30">
                  <p className="text-sm text-text-secondary">Critical Risk</p>
                  <p className="text-2xl font-bold text-critical">
                    {riskScores?.filter(r => r.risk_score >= 0.7).length || 0}
                  </p>
                </div>
                <div className="p-4 rounded-lg bg-warning/10 border border-warning/30">
                  <p className="text-sm text-text-secondary">High Risk</p>
                  <p className="text-2xl font-bold text-warning">
                    {riskScores?.filter(r => r.risk_score >= 0.4 && r.risk_score < 0.7).length || 0}
                  </p>
                </div>
                <div className="p-4 rounded-lg bg-accent/10 border border-accent/30">
                  <p className="text-sm text-text-secondary">Medium Risk</p>
                  <p className="text-2xl font-bold text-accent">
                    {riskScores?.filter(r => r.risk_score >= 0.2 && r.risk_score < 0.4).length || 0}
                  </p>
                </div>
                <div className="p-4 rounded-lg bg-success/10 border border-success/30">
                  <p className="text-sm text-text-secondary">Low Risk</p>
                  <p className="text-2xl font-bold text-success">
                    {riskScores?.filter(r => r.risk_score < 0.2).length || 0}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 2 && (
          <div className="rounded-xl bg-card border border-border p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-text-primary">
                Process Network Graph
              </h3>
              <div className="flex items-center gap-4">
                <label className="text-sm text-text-secondary">Sample Size:</label>
                <input
                  type="range"
                  min="20"
                  max="100"
                  value={sampleSize}
                  onChange={(e) => setSampleSize(Number(e.target.value))}
                  className="w-32"
                />
                <span className="text-sm text-text-primary w-8">{sampleSize}</span>
              </div>
            </div>
            {networkLoading ? (
              <div className="h-96 flex items-center justify-center text-text-secondary">
                Loading network...
              </div>
            ) : networkData ? (
              <NetworkGraph data={networkData} height={500} />
            ) : null}
          </div>
        )}

        {activeTab === 3 && (
          <div className="rounded-xl bg-card border border-border p-6">
            <h3 className="text-lg font-semibold text-text-primary mb-6">
              GNN Algorithm Trace
            </h3>
            <div className="space-y-4">
              {['Message Passing', 'Node Aggregation', 'Graph Convolution', 'Risk Propagation'].map((step, i) => (
                <div key={step} className="flex items-start gap-4 p-4 rounded-lg bg-background">
                  <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary font-semibold">
                    {i + 1}
                  </div>
                  <div>
                    <h4 className="font-medium text-text-primary">{step}</h4>
                    <p className="text-sm text-text-secondary mt-1">
                      {i === 0 && 'Nodes exchange feature information with neighbors through edges'}
                      {i === 1 && 'Each node aggregates messages from its neighborhood using attention'}
                      {i === 2 && 'Learnable filters extract patterns from local graph structure'}
                      {i === 3 && 'Risk scores propagate through supply chain connections'}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </motion.div>
    </div>
  )
}
