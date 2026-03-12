import Plot from 'react-plotly.js'
import { colors, plotlyLayout, plotlyConfig } from '../styles/theme'
import type { ManufacturingFlow } from '../types'

interface SankeyDiagramProps {
  data: ManufacturingFlow
  title?: string
  height?: number
}

export default function SankeyDiagram({ data, title, height = 400 }: SankeyDiagramProps) {
  if (!data.nodes.length || !data.links.length) {
    return (
      <div className="flex items-center justify-center h-64 text-text-secondary">
        No data available
      </div>
    )
  }

  const nodeIndices = new Map(data.nodes.map((node, i) => [node, i]))
  
  const nodeColors = data.nodes.map(node => {
    if (node.includes('Supplier')) return colors.primary
    if (node.includes('Material')) return colors.secondary
    if (node.includes('Process') || node.includes('Assembly')) return colors.purple
    if (node.includes('Product')) return colors.accent
    if (node.includes('Defect')) return colors.critical
    return colors.text
  })

  const linkColors = data.links.map(link => {
    const targetIdx = nodeIndices.get(link.target) ?? 0
    const color = nodeColors[targetIdx] || colors.primary
    return color.replace(')', ', 0.4)').replace('rgb', 'rgba').replace('#', '')
  })

  const plotData = [{
    type: 'sankey' as const,
    orientation: 'h',
    node: {
      pad: 20,
      thickness: 25,
      line: { color: colors.border, width: 1 },
      label: data.nodes,
      color: nodeColors,
    },
    link: {
      source: data.links.map(l => nodeIndices.get(l.source) ?? 0),
      target: data.links.map(l => nodeIndices.get(l.target) ?? 0),
      value: data.links.map(l => l.value),
      color: linkColors.map(c => `rgba(${parseInt(c.slice(1,3),16)}, ${parseInt(c.slice(3,5),16)}, ${parseInt(c.slice(5,7),16)}, 0.4)`),
    },
  }]

  return (
    <Plot
      data={plotData}
      layout={{
        ...plotlyLayout,
        title: title ? { text: title, font: { size: 16, color: colors.text } } : undefined,
        height,
      }}
      config={plotlyConfig}
      className="w-full"
    />
  )
}
