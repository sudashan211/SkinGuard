import { useQuery } from '@tanstack/react-query'
import { useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, Loader2, MapPin, Calendar, AlertTriangle } from 'lucide-react'
import { patientService } from '@/services/patient'
import { formatDate, getRiskLevelColor } from '@/utils/helpers'
import { ROUTES } from '@/utils/constants'

export default function ReportDetailPage() {
  const navigate = useNavigate()
  const { reportId } = useParams<{ reportId: string }>()

  const { data: report, isLoading, error } = useQuery({
    queryKey: ['report', reportId],
    queryFn: () => patientService.getReport(reportId!),
    enabled: !!reportId,
  })

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
      return { type: 'Unknown', probability: 0, allPredictions: {} }
    }
    
    const entries = Object.entries(predictions) as [string, number][]
    const sorted = entries.sort((a, b) => b[1] - a[1])
    return {
      type: sorted[0][0].replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      probability: sorted[0][1] * 100,
      allPredictions: predictions
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Loader2 className="animate-spin mx-auto mb-4 text-primary-600" size={48} />
          <p className="text-gray-600">Loading report...</p>
        </div>
      </div>
    )
  }

  if (error || !report) {
    return (
      <div className="card text-center py-12">
        <p className="text-danger-600 mb-4">Failed to load report</p>
        <button
          onClick={() => navigate(ROUTES.PATIENT_REPORTS)}
          className="btn btn-primary"
        >
          Back to Reports
        </button>
      </div>
    )
  }

  const topPrediction = getTopPrediction(report)
  const riskColor = getRiskLevelColor(report.risk_level)

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate(ROUTES.PATIENT_REPORTS)}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft size={20} className="mr-2" />
          Back to Reports
        </button>
        <h1 className="text-3xl font-bold text-gray-900">Report Details</h1>
      </div>

      {/* Report Card */}
      <div className="card">
        {/* Risk Level Banner */}
        <div className={`p-4 rounded-t-lg ${riskColor.bg} border-b ${riskColor.border}`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <AlertTriangle className={riskColor.text} size={24} />
              <span className={`ml-2 text-lg font-semibold ${riskColor.text}`}>
                {report.risk_level.toUpperCase()} RISK
              </span>
            </div>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${riskColor.bg} ${riskColor.text}`}>
              {report.status}
            </span>
          </div>
        </div>

        <div className="p-6">
          {/* Image and Basic Info */}
          <div className="grid md:grid-cols-2 gap-6 mb-6">
            {/* Image */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Lesion Image</h3>
              <img
                src={`${import.meta.env.VITE_API_URL}${report.image_url}`}
                alt="Skin lesion"
                className="w-full rounded-lg border border-gray-200"
                onError={(e) => {
                  e.currentTarget.src = 'https://via.placeholder.com/400x300?text=Image+Not+Available'
                }}
              />
            </div>

            {/* Basic Info */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Information</h3>
              <div className="space-y-3">
                <div className="flex items-start">
                  <Calendar className="text-gray-400 mr-3 mt-1" size={20} />
                  <div>
                    <p className="text-sm text-gray-600">Date</p>
                    <p className="font-medium">{formatDate(report.created_at)}</p>
                  </div>
                </div>

                {report.body_location && (
                  <div className="flex items-start">
                    <MapPin className="text-gray-400 mr-3 mt-1" size={20} />
                    <div>
                      <p className="text-sm text-gray-600">Body Location</p>
                      <p className="font-medium">{report.body_location}</p>
                    </div>
                  </div>
                )}

                <div>
                  <p className="text-sm text-gray-600 mb-1">Report ID</p>
                  <p className="font-mono text-xs text-gray-500">{report.id}</p>
                </div>
              </div>
            </div>
          </div>

          {/* AI Analysis */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3">AI Analysis</h3>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="mb-4">
                <p className="text-sm text-gray-600 mb-1">Top Prediction</p>
                <p className="text-xl font-semibold text-gray-900">{topPrediction.type}</p>
                <p className="text-sm text-gray-600">Confidence: {topPrediction.probability.toFixed(1)}%</p>
              </div>

              {/* All Predictions */}
              {topPrediction.allPredictions && Object.keys(topPrediction.allPredictions).length > 0 && (
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">All Predictions:</p>
                  <div className="space-y-2">
                    {Object.entries(topPrediction.allPredictions)
                      .sort(([, a], [, b]) => (b as number) - (a as number))
                      .map(([type, probability]) => (
                        <div key={type} className="flex items-center justify-between">
                          <span className="text-sm text-gray-700">
                            {type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </span>
                          <div className="flex items-center">
                            <div className="w-32 bg-gray-200 rounded-full h-2 mr-3">
                              <div
                                className="bg-primary-600 h-2 rounded-full"
                                style={{ width: `${(probability as number) * 100}%` }}
                              />
                            </div>
                            <span className="text-sm font-medium text-gray-900 w-12 text-right">
                              {((probability as number) * 100).toFixed(1)}%
                            </span>
                          </div>
                        </div>
                      ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Symptoms */}
          {report.symptoms && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-3">Symptoms</h3>
              <div className="bg-gray-50 rounded-lg p-4">
                {report.symptoms.sensations && report.symptoms.sensations.length > 0 && (
                  <div className="mb-3">
                    <p className="text-sm font-medium text-gray-700 mb-1">Sensations:</p>
                    <p className="text-gray-900">{report.symptoms.sensations.join(', ')}</p>
                  </div>
                )}
                {report.symptoms.visual_changes && report.symptoms.visual_changes.length > 0 && (
                  <div className="mb-3">
                    <p className="text-sm font-medium text-gray-700 mb-1">Visual Changes:</p>
                    <p className="text-gray-900">{report.symptoms.visual_changes.join(', ')}</p>
                  </div>
                )}
                {report.symptoms.duration && (
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-1">Duration:</p>
                    <p className="text-gray-900">{report.symptoms.duration}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Consultation Notes */}
          {report.consultation_notes && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-3">Doctor's Notes</h3>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-gray-900">{report.consultation_notes}</p>
              </div>
            </div>
          )}

          {/* Disclaimer */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p className="text-sm text-yellow-800">
              <strong>Important:</strong> This AI analysis is for informational purposes only and should not replace professional medical advice. 
              Please consult with a qualified dermatologist for proper diagnosis and treatment.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
