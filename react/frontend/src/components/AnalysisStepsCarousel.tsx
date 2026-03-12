import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Database, Link2, MapPin, FileText, Brain, CheckCircle, Loader2 } from 'lucide-react'

const analysisSteps = [
  {
    icon: Database,
    title: 'Querying Historical Data',
    description: 'Analyzing ROOT_CAUSE_ANALYSIS table for similar defect patterns and past root causes',
    duration: 2500,
  },
  {
    icon: Link2,
    title: 'Analyzing Supplier Correlations',
    description: 'Examining DEFECT_TYPE_SUPPLIER_BATCH data to identify supplier-related patterns',
    duration: 2000,
  },
  {
    icon: MapPin,
    title: 'Mapping Station Dependencies',
    description: 'Processing DEFECT_TYPE_STATION data to find manufacturing station correlations',
    duration: 2000,
  },
  {
    icon: FileText,
    title: 'Building Analysis Context',
    description: 'Constructing comprehensive prompt with historical defect data and correlations',
    duration: 1500,
  },
  {
    icon: Brain,
    title: 'AI Root Cause Analysis',
    description: 'Snowflake Cortex LLM (Llama 3.1-70B) generating 5-Whys Ishikawa analysis',
    duration: 3000,
  },
  {
    icon: CheckCircle,
    title: 'Structuring Results',
    description: 'Parsing AI response into Ishikawa diagram format with 6 cause categories',
    duration: 1000,
  },
]

export default function AnalysisStepsCarousel() {
  const [currentStep, setCurrentStep] = useState(0)
  const [completedSteps, setCompletedSteps] = useState<number[]>([])

  useEffect(() => {
    const step = analysisSteps[currentStep]
    if (!step) return

    const timer = setTimeout(() => {
      setCompletedSteps(prev => [...prev, currentStep])
      if (currentStep < analysisSteps.length - 1) {
        setCurrentStep(currentStep + 1)
      }
    }, step.duration)

    return () => clearTimeout(timer)
  }, [currentStep])

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="flex items-center justify-center mb-6">
        <Loader2 className="w-10 h-10 animate-spin text-primary" />
      </div>
      
      <h3 className="text-lg font-semibold text-text-primary text-center mb-2">
        Generating 5-Whys Analysis
      </h3>
      <p className="text-sm text-text-secondary text-center mb-8">
        AI-powered root cause investigation in progress
      </p>

      <div className="relative">
        <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-border" />

        <div className="space-y-4">
          {analysisSteps.map((step, index) => {
            const Icon = step.icon
            const isActive = index === currentStep
            const isCompleted = completedSteps.includes(index)
            const isPending = index > currentStep

            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ 
                  opacity: isPending ? 0.4 : 1, 
                  x: 0,
                }}
                transition={{ delay: index * 0.1, duration: 0.3 }}
                className={`relative flex items-start gap-4 pl-0 ${isPending ? 'opacity-40' : ''}`}
              >
                <div 
                  className={`relative z-10 flex items-center justify-center w-12 h-12 rounded-full border-2 transition-all duration-300 ${
                    isCompleted 
                      ? 'bg-success/20 border-success text-success' 
                      : isActive 
                        ? 'bg-primary/20 border-primary text-primary' 
                        : 'bg-card border-border text-text-secondary'
                  }`}
                >
                  {isCompleted ? (
                    <CheckCircle className="w-5 h-5" />
                  ) : isActive ? (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ repeat: Infinity, duration: 2, ease: 'linear' }}
                    >
                      <Icon className="w-5 h-5" />
                    </motion.div>
                  ) : (
                    <Icon className="w-5 h-5" />
                  )}
                </div>

                <div className="flex-1 pt-2">
                  <div className="flex items-center gap-2">
                    <h4 className={`font-medium ${
                      isCompleted ? 'text-success' : isActive ? 'text-primary' : 'text-text-secondary'
                    }`}>
                      {step.title}
                    </h4>
                    {isActive && (
                      <motion.span
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="text-xs px-2 py-0.5 rounded-full bg-primary/20 text-primary"
                      >
                        In Progress
                      </motion.span>
                    )}
                  </div>
                  
                  <AnimatePresence>
                    {(isActive || isCompleted) && (
                      <motion.p
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="text-sm text-text-secondary mt-1"
                      >
                        {step.description}
                      </motion.p>
                    )}
                  </AnimatePresence>
                </div>
              </motion.div>
            )
          })}
        </div>
      </div>

      <div className="mt-8 flex items-center justify-center gap-2">
        {analysisSteps.map((_, index) => (
          <div
            key={index}
            className={`h-1.5 rounded-full transition-all duration-300 ${
              completedSteps.includes(index)
                ? 'w-6 bg-success'
                : index === currentStep
                  ? 'w-6 bg-primary'
                  : 'w-2 bg-border'
            }`}
          />
        ))}
      </div>
    </div>
  )
}
