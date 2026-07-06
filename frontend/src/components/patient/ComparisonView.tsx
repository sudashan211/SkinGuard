import { ArrowRight, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { formatDate, getRiskLevelColor } from '@/utils/helpers'
import type { ReportComparison } from '@/types/patient'

interface ComparisonViewProps {
  comparison: ReportComparison
  onClose: () => void
}

export default function ComparisonView({ comparison, onClose }: ComparisonViewProps) {
  const { report1, report2, changes } = comparison

  const getTopPrediction = (report: any) => {
    // Handle backend format: ai_prediction.predictions array
    let predictions = report?.predictions
    
    // If predictions is not available, try ai_prediction.predictions
    if (!predictions && report?.ai_prediction?.predictions) {
      // Convert array format to object format
      const predArray = report.ai_prediction.predictions
      predictions = {}
      predArray.forEach((pred: any) => {
        const key = pred.cancer_type || pred.type
        if (key) {
          predictions[key.toLowerCase().replace(/\s+/g, '_')] = pred.probability
        }
      })
    }
    
    if (!predictions || typeof predictions !== 'object' || Object.keys(predictions).length === 0) {
      return {
        type: 'Unknown',
        probability: 0,
      }
    }
    
    const entries = Object.entries(predictions) as [string, number][]
    const sorted = entries.sort((a, b) => b[1] - a[1])
    return {
      type: sorted[0][0].replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      probability: sorted[0][1] * 100,
    }
  }

  const pred1 = getTopPrediction(report1)
  const pred2 = getTopPrediction(report2)

  const getChangeIcon = (change?: string | any) => {
    if (!change || typeof change !== 'string') return <Minus className="text-gray-400" size={20} />
    const changeLower = change.toLowerCase()
    if (changeLower.includes('increase') || changeLower.includes('worse')) {
      return <TrendingUp className="text-danger-600" size={20} />
    }
    if (changeLower.includes('decrease') || changeLower.includes('better')) {
      return <TrendingDown className="text-success-600" size={20} />
    }
    return <Minus className="text-gray-400" size={20} />
  }

  const getChangeColor = (change?: string | any) => {
    if (!change || typeof change !== 'string') return 'text-gray-600'
    const changeLower = change.toLowerCase()
    if (changeLower.includes('increase') || changeLower.includes('worse')) {
      return 'text-danger-600'
    }
    if (changeLower.includes('decrease') || changeLower.includes('better')) {
      return 'text-success-600'
    }
    return 'text-gray-600'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Report Comparison</h2>
        <button onClick={onClose} className="btn btn-secondary">
          Close
        </button>
      </div>

      {/* Time Difference */}
      <div className="card bg-primary-50 border-primary-200">
        <div className="text-center">
          <p className="text-sm text-primary-700 mb-1">Time Between Reports</p>
          <p className="text-2xl font-bold text-primary-900">
            {changes.time_difference_days || 0} days
          </p>
          <p className="text-sm text-primary-600 mt-1">
            ({((changes.time_difference_days || 0) / 30).toFixed(1)} months)
          </p>
        </div>
      </div>

      {/* Side-by-Side Images */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Report 1 */}
        <div className="card">
          <div className="mb-4">
            <h3 className="text-lg font-semibold mb-1">Earlier Report</h3>
            <p className="text-sm text-gray-600">{formatDate(report1.created_at)}</p>
          </div>
          
          <img
            src={`${import.meta.env.VITE_API_URL}${report1.image_url}`}
            alt="Earlier report"
            className="w-full h-64 object-cover rounded-lg mb-4"
          />

          <div className="space-y-3">
            <div>
              <p className="text-sm text-gray-600 mb-1">Top Prediction</p>
              <p className="font-semibold">{pred1.type}</p>
              <p className="text-sm text-gray-600">{pred1.probability.toFixed(1)}% confidence</p>
            </div>

            <div>
              <p className="text-sm text-gray-600 mb-1">Risk Level</p>
              <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${getRiskLevelColor(report1.risk_level)}`}>
                {report1.risk_level.toUpperCase()}
              </span>
            </div>
          </div>
        </div>

        {/* Report 2 */}
        <div className="card">
          <div className="mb-4">
            <h3 className="text-lg font-semibold mb-1">Recent Report</h3>
            <p className="text-sm text-gray-600">{formatDate(report2.created_at)}</p>
          </div>
          
          <img
            src={`${import.meta.env.VITE_API_URL}${report2.image_url}`}
            alt="Recent report"
            className="w-full h-64 object-cover rounded-lg mb-4"
          />

          <div className="space-y-3">
            <div>
              <p className="text-sm text-gray-600 mb-1">Top Prediction</p>
              <p className="font-semibold">{pred2.type}</p>
              <p className="text-sm text-gray-600">{pred2.probability.toFixed(1)}% confidence</p>
            </div>

            <div>
              <p className="text-sm text-gray-600 mb-1">Risk Level</p>
              <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${getRiskLevelColor(report2.risk_level)}`}>
                {report2.risk_level.toUpperCase()}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Changes Detected */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Changes Detected</h3>
        
        <div className="space-y-4">
          {/* Size Change */}
          {changes.size_change && (
            <div className="flex items-start p-4 bg-gray-50 rounded-lg">
              <div className="mr-3 mt-1">
                {getChangeIcon(typeof changes.size_change === 'string' ? changes.size_change : changes.size_change.changed)}
              </div>
              <div>
                <p className="font-medium text-gray-900 mb-1">Size</p>
                <p className={`text-sm ${getChangeColor(typeof changes.size_change === 'string' ? changes.size_change : changes.size_change.changed)}`}>
                  {typeof changes.size_change === 'string' 
                    ? changes.size_change 
                    : `${changes.size_change.from} → ${changes.size_change.to}`}
                </p>
              </div>
            </div>
          )}

          {/* Color Change */}
          {changes.color_change && (
            <div className="flex items-start p-4 bg-gray-50 rounded-lg">
              <div className="mr-3 mt-1">
                {getChangeIcon(typeof changes.color_change === 'string' ? changes.color_change : changes.color_change.changed)}
              </div>
              <div>
                <p className="font-medium text-gray-900 mb-1">Color</p>
                <p className={`text-sm ${getChangeColor(typeof changes.color_change === 'string' ? changes.color_change : changes.color_change.changed)}`}>
                  {typeof changes.color_change === 'string' 
                    ? changes.color_change 
                    : `${changes.color_change.from} → ${changes.color_change.to}`}
                </p>
              </div>
            </div>
          )}

          {/* Risk Level Change */}
          {changes.risk_level_change && (
            <div className="flex items-start p-4 bg-gray-50 rounded-lg">
              <div className="mr-3 mt-1">
                {getChangeIcon(typeof changes.risk_level_change === 'string' ? changes.risk_level_change : changes.risk_level_change.changed)}
              </div>
              <div>
                <p className="font-medium text-gray-900 mb-1">Risk Level</p>
                <p className={`text-sm ${getChangeColor(typeof changes.risk_level_change === 'string' ? changes.risk_level_change : changes.risk_level_change.changed)}`}>
                  {typeof changes.risk_level_change === 'string' 
                    ? changes.risk_level_change 
                    : `${changes.risk_level_change.from} → ${changes.risk_level_change.to}`}
                </p>
              </div>
            </div>
          )}

          {!changes.size_change && !changes.color_change && !changes.risk_level_change && (
            <div className="text-center py-8 text-gray-600">
              <Minus className="mx-auto mb-2 text-gray-400" size={32} />
              <p>No significant changes detected between these reports</p>
            </div>
          )}
        </div>
      </div>

      {/* Recommendation */}
      <div className="card bg-primary-50 border-primary-200">
        <h4 className="font-semibold text-primary-900 mb-2">Recommendation</h4>
        <p className="text-sm text-primary-800">
          {changes.size_change || changes.color_change || changes.risk_level_change ? (
            <>
              Changes have been detected in your skin lesion. We recommend consulting with a dermatologist 
              to discuss these changes and determine if further examination is needed.
            </>
          ) : (
            <>
              No significant changes detected. Continue monitoring and schedule regular check-ups 
              every 6 months or sooner if you notice any changes.
            </>
          )}
        </p>
      </div>
    </div>
  )
}
