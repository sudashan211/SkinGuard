import { useState } from 'react'
import { Calendar, AlertCircle, Eye, GitCompare } from 'lucide-react'
import { formatDate, timeAgo, getRiskLevelColor } from '@/utils/helpers'
import type { MedicalReport } from '@/types/patient'

interface ReportHistoryProps {
  reports: MedicalReport[]
  onViewReport: (reportId: string) => void
  onCompareReports?: (reportId1: string, reportId2: string) => void
}

export default function ReportHistory({ reports, onViewReport, onCompareReports }: ReportHistoryProps) {
  const [selectedForComparison, setSelectedForComparison] = useState<string[]>([])

  const handleSelectForComparison = (reportId: string) => {
    if (selectedForComparison.includes(reportId)) {
      setSelectedForComparison(selectedForComparison.filter(id => id !== reportId))
    } else if (selectedForComparison.length < 2) {
      setSelectedForComparison([...selectedForComparison, reportId])
    }
  }

  const handleCompare = () => {
    if (selectedForComparison.length === 2 && onCompareReports) {
      onCompareReports(selectedForComparison[0], selectedForComparison[1])
      setSelectedForComparison([])
    }
  }

  const getTopPrediction = (predictions: any) => {
    // Handle null/undefined predictions
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

  const needsFollowUp = (report: MedicalReport) => {
    const sixMonthsAgo = new Date()
    sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6)
    return new Date(report.created_at) < sixMonthsAgo
  }

  if (reports.length === 0) {
    return (
      <div className="card text-center py-12">
        <Calendar className="mx-auto mb-4 text-gray-400" size={48} />
        <h3 className="text-lg font-semibold text-gray-700 mb-2">
          No Reports Yet
        </h3>
        <p className="text-gray-600">
          Upload your first skin image to get started with AI screening.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Comparison Mode */}
      {onCompareReports && (
        <div className="card bg-primary-50 border-primary-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <GitCompare className="text-primary-600 mr-3" size={24} />
              <div>
                <h4 className="font-semibold text-primary-900">Compare Reports</h4>
                <p className="text-sm text-primary-700">
                  Select 2 reports to compare changes over time
                </p>
              </div>
            </div>
            {selectedForComparison.length === 2 && (
              <button
                onClick={handleCompare}
                className="btn btn-primary"
              >
                Compare Selected
              </button>
            )}
          </div>
          {selectedForComparison.length > 0 && (
            <div className="mt-3 text-sm text-primary-700">
              {selectedForComparison.length} of 2 reports selected
            </div>
          )}
        </div>
      )}

      {/* Timeline */}
      <div className="space-y-4">
        {reports.map((report, index) => {
          // Handle both full predictions object and top_prediction summary
          const topPrediction = (report as any).top_prediction 
            ? {
                type: (report as any).top_prediction.type,
                probability: (report as any).top_prediction.probability * 100
              }
            : getTopPrediction(report.predictions)
          const isSelected = selectedForComparison.includes(report.id)
          const showFollowUp = needsFollowUp(report)

          return (
            <div
              key={report.id}
              className={`
                card transition-all cursor-pointer
                ${isSelected ? 'ring-2 ring-primary-500 bg-primary-50' : 'hover:shadow-lg'}
              `}
              onClick={() => onCompareReports && handleSelectForComparison(report.id)}
            >
              <div className="flex items-start space-x-4">
                {/* Thumbnail */}
                <div className="flex-shrink-0">
                  <img
                    src={`${import.meta.env.VITE_API_URL}${report.thumbnail_url || report.image_url}`}
                    alt="Report thumbnail"
                    className="w-24 h-24 object-cover rounded-lg"
                  />
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h4 className="text-lg font-semibold text-gray-900">
                        {topPrediction.type}
                      </h4>
                      <p className="text-sm text-gray-600">
                        {formatDate(report.created_at)} • {timeAgo(report.created_at)}
                      </p>
                    </div>
                    <div className={`px-3 py-1 rounded-full text-xs font-medium ${getRiskLevelColor(report.risk_level)}`}>
                      {report.risk_level.toUpperCase()}
                    </div>
                  </div>

                  <div className="mb-3">
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span className="text-gray-600">Confidence</span>
                      <span className="font-medium">{topPrediction.probability.toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary-600 h-2 rounded-full"
                        style={{ width: `${topPrediction.probability}%` }}
                      />
                    </div>
                  </div>

                  {/* Status */}
                  <div className="flex items-center space-x-4 text-sm">
                    <span className={`
                      px-2 py-1 rounded text-xs font-medium
                      ${report.status === 'reviewed' ? 'bg-success-100 text-success-700' : ''}
                      ${report.status === 'pending' ? 'bg-gray-100 text-gray-700' : ''}
                      ${report.status === 'urgent' ? 'bg-danger-100 text-danger-700' : ''}
                    `}>
                      {report.status.charAt(0).toUpperCase() + report.status.slice(1)}
                    </span>

                    {report.symptoms && (
                      <span className="text-gray-600">
                        Symptoms recorded
                      </span>
                    )}

                    {report.consultation_notes && (
                      <span className="text-gray-600">
                        Doctor reviewed
                      </span>
                    )}
                  </div>

                  {/* Follow-up Suggestion */}
                  {showFollowUp && (
                    <div className="mt-3 p-2 bg-warning-50 border border-warning-200 rounded flex items-start">
                      <AlertCircle className="text-warning-600 mr-2 flex-shrink-0 mt-0.5" size={16} />
                      <p className="text-xs text-warning-800">
                        This report is over 6 months old. Consider a follow-up screening.
                      </p>
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex-shrink-0">
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      onViewReport(report.id)
                    }}
                    className="btn btn-secondary flex items-center"
                  >
                    <Eye size={18} className="mr-2" />
                    View
                  </button>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
