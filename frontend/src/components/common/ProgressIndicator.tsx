import { motion } from 'framer-motion'

interface ProgressIndicatorProps {
  progress: number // 0-100
  label?: string
  showPercentage?: boolean
  size?: 'sm' | 'md' | 'lg'
  color?: string
}

/**
 * Progress Indicator Component
 * 
 * Displays a progress bar with optional label and percentage.
 * Used for file uploads and long-running operations.
 * 
 * Requirements: 11.4 - Progress indicators for uploads
 */
export default function ProgressIndicator({
  progress,
  label,
  showPercentage = true,
  size = 'md',
  color = 'bg-blue-600',
}: ProgressIndicatorProps) {
  const heightClasses = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3',
  }

  const clampedProgress = Math.min(100, Math.max(0, progress))

  return (
    <div className="w-full">
      {(label || showPercentage) && (
        <div className="flex justify-between items-center mb-2">
          {label && <span className="text-sm font-medium text-gray-700">{label}</span>}
          {showPercentage && (
            <span className="text-sm font-medium text-gray-600">{Math.round(clampedProgress)}%</span>
          )}
        </div>
      )}
      <div className={`w-full ${heightClasses[size]} bg-gray-200 rounded-full overflow-hidden`}>
        <motion.div
          className={`${heightClasses[size]} ${color} rounded-full`}
          initial={{ width: 0 }}
          animate={{ width: `${clampedProgress}%` }}
          transition={{ duration: 0.3, ease: 'easeOut' }}
        />
      </div>
    </div>
  )
}

/**
 * Circular Progress Indicator
 * Displays progress in a circular format
 */
export function CircularProgress({
  progress,
  size = 64,
  strokeWidth = 4,
  color = '#3B82F6',
}: {
  progress: number
  size?: number
  strokeWidth?: number
  color?: string
}) {
  const clampedProgress = Math.min(100, Math.max(0, progress))
  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  const offset = circumference - (clampedProgress / 100) * circumference

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#E5E7EB"
          strokeWidth={strokeWidth}
          fill="none"
        />
        {/* Progress circle */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={strokeWidth}
          fill="none"
          strokeLinecap="round"
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
          style={{
            strokeDasharray: circumference,
          }}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-sm font-semibold text-gray-700">{Math.round(clampedProgress)}%</span>
      </div>
    </div>
  )
}

/**
 * Upload Progress Component
 * Specialized progress indicator for file uploads with status
 */
export function UploadProgress({
  fileName,
  progress,
  status = 'uploading',
}: {
  fileName: string
  progress: number
  status?: 'uploading' | 'processing' | 'complete' | 'error'
}) {
  const statusConfig = {
    uploading: {
      color: 'bg-blue-600',
      text: 'Uploading...',
      icon: (
        <svg className="w-5 h-5 text-blue-600 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      ),
    },
    processing: {
      color: 'bg-yellow-600',
      text: 'Processing...',
      icon: (
        <svg className="w-5 h-5 text-yellow-600 animate-pulse" fill="currentColor" viewBox="0 0 20 20">
          <path d="M10 3.5a1.5 1.5 0 013 0V4a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-.5a1.5 1.5 0 000 3h.5a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-.5a1.5 1.5 0 00-3 0v.5a1 1 0 01-1 1H6a1 1 0 01-1-1v-3a1 1 0 00-1-1h-.5a1.5 1.5 0 010-3H4a1 1 0 001-1V6a1 1 0 011-1h3a1 1 0 001-1v-.5z" />
        </svg>
      ),
    },
    complete: {
      color: 'bg-green-600',
      text: 'Complete',
      icon: (
        <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
          <path
            fillRule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
            clipRule="evenodd"
          />
        </svg>
      ),
    },
    error: {
      color: 'bg-red-600',
      text: 'Error',
      icon: (
        <svg className="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
          <path
            fillRule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
            clipRule="evenodd"
          />
        </svg>
      ),
    },
  }

  const config = statusConfig[status]

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
      <div className="flex items-center gap-3 mb-3">
        {config.icon}
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900 truncate">{fileName}</p>
          <p className="text-xs text-gray-500">{config.text}</p>
        </div>
      </div>
      {status !== 'complete' && status !== 'error' && (
        <ProgressIndicator progress={progress} color={config.color} size="sm" />
      )}
    </div>
  )
}
