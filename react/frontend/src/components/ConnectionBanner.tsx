import { AlertTriangle, RefreshCw } from 'lucide-react'
import { useAppStore } from '../stores/appStore'

export default function ConnectionBanner() {
  const { connectionError } = useAppStore()

  const handleRetry = () => {
    window.location.reload()
  }

  return (
    <div className="bg-critical/10 border-b border-critical/30 px-6 py-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-critical" />
          <div>
            <p className="text-sm font-medium text-critical">
              Unable to connect to Snowflake
            </p>
            {connectionError && (
              <p className="text-xs text-text-secondary mt-0.5">
                {connectionError}
              </p>
            )}
          </div>
        </div>
        <button
          onClick={handleRetry}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-critical/20 hover:bg-critical/30 text-critical text-sm transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Retry
        </button>
      </div>
    </div>
  )
}
