import Plot from 'react-plotly.js'
import { colors, plotlyLayout, plotlyConfig } from '../styles/theme'

interface BubbleData {
  x: string[]
  y: string[]
  sizes: number[]
  colors: string[]
  text: string[]
}

interface BubbleChartProps {
  data: BubbleData
  title?: string
  height?: number
}

const materialColors: Record<string, string> = {
  primer_batch: colors.primary,
  protective_coating: colors.accent,
  paint_batch: colors.purple,
  steel_rod: colors.critical,
  steel_tube: '#ec4899',
  steel_plate: '#f43f5e',
  gasket_set: colors.success,
  cable_assembly: colors.warning,
  hydraulic_valve: '#06b6d4',
  seal_kit: '#14b8a6',
  wire_harness: '#a855f7',
  hydraulic_cylinder: '#6366f1',
  bearing_set: '#0ea5e9',
}

export default function BubbleChart({ data, title, height = 400 }: BubbleChartProps) {
  if (!data.x.length) {
    return (
      <div className="flex items-center justify-center h-64 text-text-secondary">
        No data available
      </div>
    )
  }

  const maxSize = Math.max(...data.sizes)
  const normalizedSizes = data.sizes.map(s => 15 + (s / maxSize) * 45)
  const bubbleColors = data.colors.map(c => materialColors[c] || colors.textSecondary)

  const uniqueMaterials = [...new Set(data.colors)]
  const legendTraces = uniqueMaterials.map(mat => ({
    type: 'scatter' as const,
    mode: 'markers' as const,
    x: [null],
    y: [null],
    marker: { color: materialColors[mat] || colors.textSecondary, size: 10 },
    name: mat.replace(/_/g, ' '),
    showlegend: true,
  }))

  return (
    <Plot
      data={[
        {
          type: 'scatter',
          mode: 'markers',
          x: data.x,
          y: data.y,
          marker: {
            size: normalizedSizes,
            color: bubbleColors,
            opacity: 0.75,
            line: { width: 1, color: colors.border },
          },
          text: data.text,
          hovertemplate: '%{text}<extra></extra>',
          showlegend: false,
        },
        ...legendTraces,
      ]}
      layout={{
        ...plotlyLayout,
        title: title ? { text: title, font: { size: 14, color: colors.text } } : undefined,
        xaxis: {
          title: { text: 'Supplier', font: { color: colors.text, size: 11 } },
          tickfont: { color: colors.text, size: 9 },
          tickangle: -30,
          gridcolor: colors.border,
          showgrid: false,
        },
        yaxis: {
          title: { text: 'Defect Type', font: { color: colors.text, size: 11 } },
          tickfont: { color: colors.text, size: 10 },
          gridcolor: colors.border,
          showgrid: true,
        },
        height,
        showlegend: true,
        legend: {
          orientation: 'h',
          y: -0.25,
          x: 0.5,
          xanchor: 'center',
          font: { size: 9, color: colors.text },
        },
        margin: { t: 40, r: 20, b: 100, l: 140 },
      }}
      config={plotlyConfig}
      className="w-full"
    />
  )
}
