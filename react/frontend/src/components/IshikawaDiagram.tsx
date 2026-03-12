import { useState } from 'react'
import { colors } from '../styles/theme'
import type { FiveWhysAnalysis, WhyChain } from '../types'
import { motion, AnimatePresence } from 'framer-motion'
import { X, AlertTriangle, ChevronRight } from 'lucide-react'

interface IshikawaDiagramProps {
  data: FiveWhysAnalysis
  height?: number
}

const categoryColors: Record<string, string> = {
  Material: colors.primary,
  Method: colors.purple,
  Machine: colors.accent,
  Man: '#f59e0b',
  Measurement: colors.success,
  Environment: colors.critical,
}

interface DetailsPanelProps {
  category: string
  causes: WhyChain[]
  color: string
  onClose: () => void
}

function DetailsPanel({ category, causes, color, onClose }: DetailsPanelProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      className="absolute right-0 top-0 bottom-0 w-[420px] bg-card border-l border-border p-6 overflow-y-auto z-20"
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold" style={{ color }}>
          {category}
        </h3>
        <button
          onClick={onClose}
          className="p-1.5 rounded-lg hover:bg-background transition-colors"
        >
          <X className="w-5 h-5 text-text-secondary" />
        </button>
      </div>

      {causes.map((chain, idx) => (
        <div key={idx} className="mb-6 last:mb-0">
          <div className="space-y-3">
            {[chain.why1, chain.why2, chain.why3, chain.why4, chain.why5].map((why, whyIdx) => (
              <div key={whyIdx} className="flex items-start gap-3">
                <div 
                  className="flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold"
                  style={{ backgroundColor: `${color}25`, color }}
                >
                  {whyIdx + 1}
                </div>
                <div className="pt-1">
                  <p className="text-xs text-text-secondary mb-0.5">Why {whyIdx + 1}</p>
                  <p className="text-sm text-text-primary leading-relaxed">{why}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 p-4 rounded-lg border-l-4" style={{ borderColor: color, backgroundColor: `${color}10` }}>
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className="w-4 h-4" style={{ color }} />
              <p className="text-xs font-medium text-text-secondary uppercase tracking-wide">Root Cause Identified</p>
            </div>
            <p className="text-sm font-medium leading-relaxed" style={{ color }}>{chain.root_cause}</p>
          </div>
        </div>
      ))}
    </motion.div>
  )
}

function truncateText(text: string, maxLen: number): string {
  if (text.length <= maxLen) return text
  return text.substring(0, maxLen - 3) + '...'
}

export default function IshikawaDiagram({ data, height = 280 }: IshikawaDiagramProps) {
  const [selectedCategory, setSelectedCategory] = useState<{
    category: string
    causes: WhyChain[]
    color: string
  } | null>(null)
  
  const [hoveredCategory, setHoveredCategory] = useState<string | null>(null)
  const [hoveredRootCause, setHoveredRootCause] = useState<{ text: string; x: number; y: number } | null>(null)

  if (!data.categories?.length) {
    return (
      <div className="flex items-center justify-center h-64 text-text-secondary">
        No analysis data available
      </div>
    )
  }

  const topCategories = data.categories.slice(0, 3)
  const bottomCategories = data.categories.slice(3, 6)

  const handleCategoryClick = (cat: typeof data.categories[0]) => {
    const color = categoryColors[cat.category] || colors.textSecondary
    setSelectedCategory({
      category: cat.category,
      causes: cat.causes,
      color
    })
  }

  const width = 820
  const svgHeight = 280
  const spineY = svgHeight / 2
  const spineStartX = 30
  const spineEndX = width - 160
  
  const boneXConnections = [140, 330, 520]

  return (
    <div className="relative">
      <svg 
        viewBox={`0 0 ${width} ${svgHeight}`}
        preserveAspectRatio="xMidYMid meet"
        style={{ height, width: '100%' }}
        className="overflow-visible"
      >
        <defs>
          <linearGradient id="spineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor={colors.textSecondary} stopOpacity="0.3" />
            <stop offset="50%" stopColor={colors.text} stopOpacity="0.8" />
            <stop offset="100%" stopColor={colors.critical} />
          </linearGradient>
          <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>

        <line
          x1={spineStartX}
          y1={spineY}
          x2={spineEndX}
          y2={spineY}
          stroke="url(#spineGradient)"
          strokeWidth="5"
          strokeLinecap="round"
        />

        <polygon
          points={`${spineEndX},${spineY - 10} ${spineEndX + 30},${spineY} ${spineEndX},${spineY + 10}`}
          fill={colors.critical}
        />

        <text
          x={spineEndX + 35}
          y={spineY - 8}
          fill={colors.textSecondary}
          fontSize="10"
          fontFamily="Inter, sans-serif"
        >
          Problem
        </text>
        <text
          x={spineEndX + 35}
          y={spineY + 10}
          fill={colors.critical}
          fontSize="13"
          fontWeight="700"
          fontFamily="Inter, sans-serif"
        >
          {truncateText(data.defect_type.replace(/_/g, ' ').toUpperCase(), 18)}
        </text>

        {topCategories.map((cat, idx) => {
          const boneConnectX = boneXConnections[idx]
          const boneEndX = boneConnectX - 50
          const boneEndY = 35
          const color = categoryColors[cat.category] || colors.textSecondary
          const isHovered = hoveredCategory === cat.category
          const isSelected = selectedCategory?.category === cat.category
          const rootCause = cat.causes?.[0]?.root_cause || 'Analysis pending'
          const boxX = boneEndX - 65
          const boxY = boneEndY + 40
          const boxWidth = 130
          const boxHeight = 42
          
          return (
            <g 
              key={cat.category}
              className="cursor-pointer"
              onClick={() => handleCategoryClick(cat)}
              onMouseEnter={() => setHoveredCategory(cat.category)}
              onMouseLeave={() => setHoveredCategory(null)}
            >
              <line
                x1={boneConnectX}
                y1={spineY}
                x2={boneEndX}
                y2={boneEndY}
                stroke={color}
                strokeWidth={isHovered || isSelected ? 3 : 2}
                strokeLinecap="round"
                style={{ filter: isSelected || isHovered ? 'url(#glow)' : undefined }}
              />
              
              <circle
                cx={boneEndX}
                cy={boneEndY}
                r={isHovered || isSelected ? 8 : 6}
                fill={color}
                style={{ filter: isSelected || isHovered ? 'url(#glow)' : undefined }}
              />

              <text
                x={boneEndX}
                y={boneEndY - 14}
                fill={color}
                fontSize="12"
                fontWeight="700"
                fontFamily="Inter, sans-serif"
                textAnchor="middle"
              >
                {cat.category}
              </text>

              <rect
                x={boxX}
                y={boxY}
                width={boxWidth}
                height={boxHeight}
                rx="6"
                fill={colors.card}
                stroke={color}
                strokeWidth="1.5"
                strokeOpacity="0.5"
                onMouseEnter={(e) => {
                  const rect = (e.target as SVGRectElement).getBoundingClientRect()
                  setHoveredRootCause({ text: rootCause, x: rect.left + rect.width / 2, y: rect.top - 10 })
                }}
                onMouseLeave={() => setHoveredRootCause(null)}
              />
              <text
                x={boneEndX}
                y={boxY + 16}
                fill={colors.textSecondary}
                fontSize="9"
                fontFamily="Inter, sans-serif"
                textAnchor="middle"
                pointerEvents="none"
              >
                Root Cause
              </text>
              <text
                x={boneEndX}
                y={boxY + 32}
                fill={color}
                fontSize="10"
                fontWeight="600"
                fontFamily="Inter, sans-serif"
                textAnchor="middle"
                pointerEvents="none"
              >
                {truncateText(rootCause, 22)}
              </text>
            </g>
          )
        })}

        {bottomCategories.map((cat, idx) => {
          const boneConnectX = boneXConnections[idx]
          const boneEndX = boneConnectX - 50
          const boneEndY = svgHeight - 35
          const color = categoryColors[cat.category] || colors.textSecondary
          const isHovered = hoveredCategory === cat.category
          const isSelected = selectedCategory?.category === cat.category
          const rootCause = cat.causes?.[0]?.root_cause || 'Analysis pending'
          const boxX = boneEndX - 65
          const boxY = boneEndY - 82
          const boxWidth = 130
          const boxHeight = 42
          
          return (
            <g 
              key={cat.category}
              className="cursor-pointer"
              onClick={() => handleCategoryClick(cat)}
              onMouseEnter={() => setHoveredCategory(cat.category)}
              onMouseLeave={() => setHoveredCategory(null)}
            >
              <line
                x1={boneConnectX}
                y1={spineY}
                x2={boneEndX}
                y2={boneEndY}
                stroke={color}
                strokeWidth={isHovered || isSelected ? 3 : 2}
                strokeLinecap="round"
                style={{ filter: isSelected || isHovered ? 'url(#glow)' : undefined }}
              />
              
              <circle
                cx={boneEndX}
                cy={boneEndY}
                r={isHovered || isSelected ? 8 : 6}
                fill={color}
                style={{ filter: isSelected || isHovered ? 'url(#glow)' : undefined }}
              />

              <text
                x={boneEndX}
                y={boneEndY + 18}
                fill={color}
                fontSize="12"
                fontWeight="700"
                fontFamily="Inter, sans-serif"
                textAnchor="middle"
              >
                {cat.category}
              </text>

              <rect
                x={boxX}
                y={boxY}
                width={boxWidth}
                height={boxHeight}
                rx="6"
                fill={colors.card}
                stroke={color}
                strokeWidth="1.5"
                strokeOpacity="0.5"
                onMouseEnter={(e) => {
                  const rect = (e.target as SVGRectElement).getBoundingClientRect()
                  setHoveredRootCause({ text: rootCause, x: rect.left + rect.width / 2, y: rect.top - 10 })
                }}
                onMouseLeave={() => setHoveredRootCause(null)}
              />
              <text
                x={boneEndX}
                y={boxY + 16}
                fill={colors.textSecondary}
                fontSize="9"
                fontFamily="Inter, sans-serif"
                textAnchor="middle"
                pointerEvents="none"
              >
                Root Cause
              </text>
              <text
                x={boneEndX}
                y={boxY + 32}
                fill={color}
                fontSize="10"
                fontWeight="600"
                fontFamily="Inter, sans-serif"
                textAnchor="middle"
                pointerEvents="none"
              >
                {truncateText(rootCause, 22)}
              </text>
            </g>
          )
        })}
      </svg>

      <div className="mt-2 px-4">
        <p className="text-xs text-text-secondary mb-3 text-center">
          Click any category on the diagram or button below to view the complete 5-Whys analysis chain
        </p>
        <div className="flex items-center justify-center gap-2 flex-wrap">
          {data.categories.map((cat) => {
            const color = categoryColors[cat.category] || colors.textSecondary
            const isSelected = selectedCategory?.category === cat.category
            return (
              <button
                key={cat.category}
                onClick={() => handleCategoryClick(cat)}
                onMouseEnter={() => setHoveredCategory(cat.category)}
                onMouseLeave={() => setHoveredCategory(null)}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg border transition-all ${
                  isSelected 
                    ? 'border-primary bg-primary/10' 
                    : 'border-border hover:border-primary/50'
                }`}
              >
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
                <span className="text-sm text-text-primary">{cat.category}</span>
                <ChevronRight className={`w-4 h-4 transition-colors ${
                  isSelected ? 'text-primary' : 'text-text-secondary'
                }`} />
              </button>
            )
          })}
        </div>
        <div className="flex items-center justify-center gap-4 mt-4 pt-4 border-t border-border">
          <div className="flex items-center gap-2 text-xs text-text-secondary">
            <span>AI Confidence:</span>
            <div className="flex items-center gap-1">
              <div className="w-16 h-2 rounded-full bg-background overflow-hidden">
                <div 
                  className="h-full rounded-full transition-all"
                  style={{ 
                    width: `${data.ai_confidence * 100}%`,
                    backgroundColor: data.ai_confidence >= 0.7 
                      ? colors.success 
                      : data.ai_confidence >= 0.5 
                        ? colors.warning 
                        : colors.critical
                  }}
                />
              </div>
              <span className={`font-medium ${data.ai_confidence >= 0.7 ? 'text-success' : data.ai_confidence >= 0.5 ? 'text-warning' : 'text-critical'}`}>
                {(data.ai_confidence * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        </div>
      </div>

      {hoveredRootCause && (
        <div 
          className="fixed z-50 px-3 py-2 bg-card border border-border rounded-lg shadow-lg max-w-xs text-sm text-text-primary"
          style={{ 
            left: hoveredRootCause.x, 
            top: hoveredRootCause.y,
            transform: 'translate(-50%, -100%)',
            pointerEvents: 'none'
          }}
        >
          {hoveredRootCause.text}
        </div>
      )}

      <AnimatePresence>
        {selectedCategory && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 z-10"
              onClick={() => setSelectedCategory(null)}
            />
            <DetailsPanel
              category={selectedCategory.category}
              causes={selectedCategory.causes}
              color={selectedCategory.color}
              onClose={() => setSelectedCategory(null)}
            />
          </>
        )}
      </AnimatePresence>
    </div>
  )
}
