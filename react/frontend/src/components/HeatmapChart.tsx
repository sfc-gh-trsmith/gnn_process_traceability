import Plot from 'react-plotly.js'
import { colors, plotlyLayout, plotlyConfig } from '../styles/theme'

interface HeatmapData {
  x: string[]
  y: string[]
  z: number[][]
}

interface HeatmapChartProps {
  data: HeatmapData
  title?: string
  xLabel?: string
  yLabel?: string
  height?: number
}

export default function HeatmapChart({ data, title, xLabel, yLabel, height = 400 }: HeatmapChartProps) {
  if (!data.x.length || !data.y.length) {
    return (
      <div className="flex items-center justify-center h-64 text-text-secondary">
        No data available
      </div>
    )
  }

  const plotData = [{
    type: 'heatmap' as const,
    x: data.x,
    y: data.y,
    z: data.z,
    colorscale: [
      [0, colors.background],
      [0.5, colors.secondary],
      [1, colors.accent],
    ],
    hoverongaps: false,
    showscale: true,
    colorbar: {
      tickfont: { color: colors.text },
      title: { text: 'Count', font: { color: colors.text } },
    },
  }]

  return (
    <Plot
      data={plotData}
      layout={{
        ...plotlyLayout,
        title: title ? { text: title, font: { size: 16, color: colors.text } } : undefined,
        xaxis: {
          title: xLabel,
          tickfont: { color: colors.text, size: 10 },
          gridcolor: colors.border,
          tickangle: -45,
        },
        yaxis: {
          title: yLabel,
          tickfont: { color: colors.text, size: 10 },
          gridcolor: colors.border,
          automargin: true,
        },
        height: Math.max(height, 100 + data.y.length * 25),
        margin: { l: 150, r: 50, t: 50, b: 100 },
      }}
      config={plotlyConfig}
      className="w-full"
    />
  )
}
