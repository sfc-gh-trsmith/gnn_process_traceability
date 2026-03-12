import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { RefreshCw } from 'lucide-react'
import IshikawaDiagram from '../components/IshikawaDiagram'
import AnalysisStepsCarousel from '../components/AnalysisStepsCarousel'
import type { DefectTypeCount, FiveWhysAnalysis } from '../types'

export default function FiveWhys() {
  const [selectedType, setSelectedType] = useState<string | null>(null)

  const { data: defectTypes, isLoading: typesLoading } = useQuery<DefectTypeCount[]>({
    queryKey: ['defectTypes'],
    queryFn: async () => {
      const res = await fetch('/api/defects/type-counts')
      if (!res.ok) throw new Error('Failed to fetch defect types')
      return res.json()
    },
  })

  const { data: fiveWhysData, isLoading: fiveWhysLoading, refetch: refetchFiveWhys, isFetching: fiveWhysFetching } = useQuery<FiveWhysAnalysis>({
    queryKey: ['fiveWhys', selectedType],
    queryFn: async () => {
      if (!selectedType) return null
      const res = await fetch(`/api/risk/five-whys/${encodeURIComponent(selectedType)}`)
      if (!res.ok) throw new Error('Failed to fetch 5-Whys analysis')
      return res.json()
    },
    enabled: !!selectedType,
    staleTime: 5 * 60 * 1000,
  })

  return (
    <div className="space-y-6">
      <div className="rounded-xl bg-card border border-border p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-semibold text-text-primary">
              Select Defect Type
            </h2>
            <p className="text-sm text-text-secondary mt-1">
              Choose a defect type to generate AI-powered root cause analysis
            </p>
          </div>
          <select
            value={selectedType || ''}
            onChange={(e) => setSelectedType(e.target.value || null)}
            className="px-4 py-2 rounded-lg bg-background border border-border text-text-primary min-w-[250px]"
          >
            <option value="">-- Select Defect Type --</option>
            {typesLoading ? (
              <option disabled>Loading...</option>
            ) : defectTypes?.map(d => (
              <option key={d.defect_type} value={d.defect_type}>
                {d.defect_type.replace(/_/g, ' ')} ({d.defect_count} defects)
              </option>
            ))}
          </select>
        </div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-xl bg-card border border-border p-6"
      >
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-semibold text-text-primary">
              5-Whys Ishikawa Diagram
            </h3>
            <p className="text-sm text-text-secondary mt-1">
              {selectedType 
                ? `Root cause analysis for: ${selectedType.replace(/_/g, ' ')}`
                : 'Analysis will appear here after selecting a defect type'
              }
            </p>
          </div>
          {selectedType && (
            <button
              onClick={() => refetchFiveWhys()}
              disabled={fiveWhysFetching}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary/10 text-primary hover:bg-primary/20 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${fiveWhysFetching ? 'animate-spin' : ''}`} />
              <span>Regenerate Analysis</span>
            </button>
          )}
        </div>

        {!selectedType ? (
          <div className="h-[320px] flex flex-col items-center justify-center text-text-secondary border-2 border-dashed border-border rounded-lg">
            <div className="text-6xl mb-4">&#129300;</div>
            <p className="text-lg">Select a defect type above</p>
            <p className="text-sm mt-2">to generate an AI-powered 5-Whys root cause analysis</p>
          </div>
        ) : fiveWhysLoading || fiveWhysFetching ? (
          <div className="py-8">
            <AnalysisStepsCarousel />
          </div>
        ) : fiveWhysData ? (
          <IshikawaDiagram data={fiveWhysData} />
        ) : (
          <div className="h-[320px] flex items-center justify-center text-text-secondary">
            No analysis available
          </div>
        )}
      </motion.div>

      {fiveWhysData && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="rounded-xl bg-card border border-border p-6"
        >
          <h3 className="text-lg font-semibold text-text-primary mb-4">
            Analysis Details
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {fiveWhysData.categories.map((category, idx) => (
              <div key={idx} className="p-4 rounded-lg bg-background border border-border">
                <h4 className="font-medium text-text-primary mb-2">{category.category}</h4>
                <div className="space-y-2 text-sm">
                  {category.causes.slice(0, 2).map((chain, chainIdx) => (
                    <div key={chainIdx} className="text-text-secondary">
                      <span className="text-primary font-medium">Root Cause:</span>{' '}
                      {chain.root_cause}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  )
}
