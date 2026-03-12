import { motion } from 'framer-motion'
import { Sparkles } from 'lucide-react'

interface AIInsightCardProps {
  title: string
  content: string
  isLoading?: boolean
}

export default function AIInsightCard({ title, content, isLoading }: AIInsightCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-lg bg-card border border-border border-l-4 border-l-primary p-5"
    >
      <div className="flex items-center gap-2 mb-3">
        <div className="p-1.5 rounded-lg bg-primary/10">
          <Sparkles className="w-4 h-4 text-primary" />
        </div>
        <h3 className="font-semibold text-text-primary">{title}</h3>
        <span className="px-2 py-0.5 rounded text-xs font-medium bg-primary/20 text-primary">
          AI Generated
        </span>
      </div>

      {isLoading ? (
        <div className="space-y-2">
          <div className="h-4 bg-border rounded animate-pulse w-full" />
          <div className="h-4 bg-border rounded animate-pulse w-3/4" />
          <div className="h-4 bg-border rounded animate-pulse w-5/6" />
        </div>
      ) : (
        <p className="text-sm text-text-secondary leading-relaxed whitespace-pre-wrap">
          {content}
        </p>
      )}
    </motion.div>
  )
}
