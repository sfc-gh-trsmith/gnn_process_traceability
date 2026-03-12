import Plot from 'react-plotly.js'
import { colors, plotlyLayout, plotlyConfig } from '../styles/theme'

interface RiskBarData {
  labels: string[]
  values: number[]
  colors?: string[]
}

interface RiskBarChartProps {
  data: RiskBarData
  title?: string
  height?: number
  orientation?: 'h' | 'v'
}

export default function RiskBarChart({ data, title, height = 400, orientation = 'h' }: RiskBarChartProps) {
  if (!data.labels.length) {
    return (
      <div className="flex items-center justify-center h-64 text-text-secondary">
        No data available
      </div>
    )
  }

  const barColors = data.colors || data.values.map(v => {
    if (v >= 80) return colors.critical
    if (v >= 60) return colors.warning
    return colors.success
  })

  const plotData = [{
    type: 'bar' as const,
    x: orientation === 'h' ? data.values : data.labels,
    y: orientation === 'h' ? data.labels : data.values,
    orientation,
    marker: {
      color: barColors,
      line: { width: 0 },
    },
    text: data.values.map(v => v.toFixed(1)),
    textposition: 'outside' as const,
    textfont: { color: colors.text },
  }]

  return (
    <Plot
      data={plotData}
      layout={{
        ...plotlyLayout,
        title: title ? { text: title, font: { size: 16, color: colors.text } } : undefined,
        xaxis: {
          tickfont: { color: colors.text },
          gridcolor: colors.border,
          showgrid: orientation === 'v',
          type: orientation === 'v' ? 'category' as const : undefined,
        },
        yaxis: {
          tickfont: { color: colors.text },
          gridcolor: colors.border,
          showgrid: orientation === 'h',
          automargin: true,
          type: 'category' as const,
        },
        height,
        bargap: 0.3,
      }}
      config={plotlyConfig}
      className="w-full"
    />
  )
}
