import Plot from 'react-plotly.js'
import { colors, plotlyLayout, plotlyConfig } from '../styles/theme'

interface ParetoData {
  labels: string[]
  values: number[]
  cumulativePct: number[]
}

interface ParetoChartProps {
  data: ParetoData
  title?: string
  height?: number
}

export default function ParetoChart({ data, title, height = 350 }: ParetoChartProps) {
  if (!data.labels.length) {
    return (
      <div className="flex items-center justify-center h-64 text-text-secondary">
        No data available
      </div>
    )
  }

  const barColors = data.values.map((_, i) => 
    data.cumulativePct[i] <= 80 ? colors.critical : colors.accent
  )

  return (
    <Plot
      data={[
        {
          type: 'bar',
          x: data.labels,
          y: data.values,
          marker: {
            color: barColors,
            line: { width: 0 },
          },
          text: data.values.map(v => String(v)),
          textposition: 'outside',
          textfont: { color: colors.text, size: 11 },
          name: 'Defects',
          yaxis: 'y',
        },
        {
          type: 'scatter',
          mode: 'lines+markers',
          x: data.labels,
          y: data.cumulativePct,
          marker: { color: colors.primary, size: 8 },
          line: { color: colors.primary, width: 2 },
          name: 'Cumulative %',
          yaxis: 'y2',
        },
      ]}
      layout={{
        ...plotlyLayout,
        title: title ? { text: title, font: { size: 14, color: colors.text } } : undefined,
        xaxis: {
          tickfont: { color: colors.text, size: 9 },
          tickangle: -45,
          gridcolor: colors.border,
          showgrid: false,
        },
        yaxis: {
          title: { text: 'Defect Count', font: { color: colors.text, size: 11 } },
          tickfont: { color: colors.text },
          gridcolor: colors.border,
          showgrid: true,
        },
        yaxis2: {
          title: { text: 'Cumulative %', font: { color: colors.primary, size: 11 } },
          tickfont: { color: colors.primary },
          overlaying: 'y',
          side: 'right',
          range: [0, 105],
          showgrid: false,
        },
        height,
        bargap: 0.2,
        showlegend: false,
        shapes: [{
          type: 'line',
          x0: -0.5,
          x1: data.labels.length - 0.5,
          y0: 80,
          y1: 80,
          yref: 'y2',
          line: { color: colors.warning, width: 1, dash: 'dash' },
        }],
      }}
      config={plotlyConfig}
      className="w-full"
    />
  )
}
