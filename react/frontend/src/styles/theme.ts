export const colors = {
  primary: '#29B5E8',
  secondary: '#11567F',
  accent: '#FF9F0A',
  purple: '#8B5CF6',
  background: '#0f172a',
  card: '#1e293b',
  text: '#e2e8f0',
  textSecondary: '#94a3b8',
  border: '#334155',
  critical: '#ef4444',
  warning: '#f59e0b',
  success: '#22c55e',
} as const;

export const chartColors = [
  colors.primary,
  colors.accent,
  colors.purple,
  colors.secondary,
  colors.success,
  colors.warning,
  colors.critical,
];

export const plotlyLayout = {
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  font: {
    color: colors.text,
    family: 'Inter, system-ui, sans-serif',
  },
  margin: { t: 40, r: 20, b: 40, l: 60 },
  colorway: chartColors,
};

export const plotlyConfig = {
  displayModeBar: true,
  displaylogo: false,
  modeBarButtonsToRemove: ['lasso2d', 'select2d', 'autoScale2d'],
  responsive: true,
};
