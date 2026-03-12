import Plot from 'react-plotly.js'
import { colors, plotlyLayout, plotlyConfig } from '../styles/theme'
import type { NetworkGraph as NetworkGraphType } from '../types'

interface NetworkGraphProps {
  data: NetworkGraphType
  title?: string
  height?: number
}

export default function NetworkGraph({ data, title, height = 500 }: NetworkGraphProps) {
  if (!data.nodes.length) {
    return (
      <div className="flex items-center justify-center h-64 text-text-secondary">
        No data available
      </div>
    )
  }

  const nodeX = data.nodes.map(n => n.x)
  const nodeY = data.nodes.map(n => n.y)
  
  const nodeColors = data.nodes.map(n => {
    if (n.risk_score >= 0.7) return colors.critical
    if (n.risk_score >= 0.4) return colors.warning
    if (n.risk_score >= 0.2) return colors.accent
    return colors.success
  })

  const nodeSizes = data.nodes.map(n => Math.max(10, Math.min(30, n.defect_count / 2)))

  const edgeX: (number | null)[] = []
  const edgeY: (number | null)[] = []
  
  data.edges.forEach(edge => {
    const source = data.nodes.find(n => n.id === edge.source)
    const target = data.nodes.find(n => n.id === edge.target)
    if (source && target) {
      edgeX.push(source.x, target.x, null)
      edgeY.push(source.y, target.y, null)
    }
  })

  const edgeTrace = {
    x: edgeX,
    y: edgeY,
    mode: 'lines' as const,
    line: { width: 1, color: colors.border },
    hoverinfo: 'none' as const,
    type: 'scatter' as const,
  }

  const nodeTrace = {
    x: nodeX,
    y: nodeY,
    mode: 'markers+text' as const,
    marker: {
      size: nodeSizes,
      color: nodeColors,
      line: { width: 2, color: colors.card },
    },
    text: data.nodes.map(n => n.label),
    textposition: 'top center' as const,
    textfont: { size: 10, color: colors.text },
    hovertemplate: data.nodes.map(n => 
      `<b>${n.label}</b><br>Type: ${n.type}<br>Risk: ${n.risk_score.toFixed(1)}<br>Defects: ${n.defect_count}<extra></extra>`
    ),
    type: 'scatter' as const,
  }

  return (
    <Plot
      data={[edgeTrace, nodeTrace]}
      layout={{
        ...plotlyLayout,
        title: title ? { text: title, font: { size: 16, color: colors.text } } : undefined,
        showlegend: false,
        hovermode: 'closest',
        xaxis: { showgrid: false, zeroline: false, showticklabels: false },
        yaxis: { showgrid: false, zeroline: false, showticklabels: false },
        height,
      }}
      config={plotlyConfig}
      className="w-full"
    />
  )
}
