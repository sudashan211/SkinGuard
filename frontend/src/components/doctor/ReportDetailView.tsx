import { useState, useEffect } from 'react'
import { X, User, Calendar, MapPin, AlertCircle, Save } from 'lucide-react'
import type { MedicalReport, PatientProfile } from '@/types/patient'
import { CANCER_TYPES } from '@/utils/constants'
import api from '@/services/api'
import { TouchImageViewer } from '@/components/common/TouchImageViewer'

interface ReportDetailViewProps {
  reportId: string
  onClose: () => void
}

interface ReportWithPatient extends MedicalReport {
  patient?: PatientProfile & {
    fullName: string
    email: string
  }
}

export default function ReportDetailView({ reportId, onClose }: ReportDetailViewProps) {
  const [report, setReport] = useState<ReportWithPatient | null>(null)
  const [loading, setLoading] = useState(true)
  const [consultationNotes, setConsultationNotes] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    fetchReportDetail()
  }, [reportId])

  const fetchReportDetail = async () => {
    try {
      setLoading(true)
      const response = await api.get<ReportWithPatient>(`/api/reports/${reportId}`)
      setReport(response.data)
      setConsultationNotes(response.data.consultation_notes || '')
    } catch (error) {
      console.error('Failed to fetch report details:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSaveNotes = async () => {
    if (!report) return
    
    try {
      setSaving(true)
      await api.post(`/api/doctors/reports/${reportId}/notes`, {
        notes: consultationNotes
      })
      alert('Consultation notes saved successfully')
    } catch (error) {
      console.error('Failed to save notes:', error)
      alert('Failed to save consultation notes')
    } finally {
      setSaving(false)
    }
  }

  const getRiskBadgeColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'urgent':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      default:
        return 'bg-green-100 text-green-800 border-green-200'
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getPredictionEntries = (predictions: any): [string, number][] => {
    if (!predictions || typeof predictions !== 'object') {
      return []
    }
    return Object.entries(predictions) as [string, number][]
  }

  const formatCancerType = (type: string): string => {
    return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
  }

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        </div>
      </div>
    )
  }

  if (!report) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <p className="text-red-600">Failed to load report</p>
          <button onClick={onClose} className="mt-4 btn-primary">Close</button>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-white rounded-lg max-w-6xl w-full my-8">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Medical Report Details</h2>
            <p className="text-sm text-gray-600 mt-1">Report ID: {report.id.slice(0, 8)}...</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        <div className="p-6 space-y-6 max-h-[calc(100vh-200px)] overflow-y-auto">
          {/* Risk Level Alert */}
          {report.risk_level === 'urgent' && (
            <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4 flex items-start gap-3">
              <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={24} />
              <div>
                <h3 className="font-semibold text-red-900">Urgent Case</h3>
                <p className="text-sm text-red-800 mt-1">
                  This case has been flagged as urgent based on AI analysis. Immediate attention recommended.
                </p>
              </div>
            </div>
          )}

          <div className="grid md:grid-cols-2 gap-6">
            {/* Left Column - Image and AI Predictions */}
            <div className="space-y-6">
              {/* Full Resolution Image */}
              <div className="card">
                <h3 className="text-lg font-semibold mb-3">Lesion Image</h3>
                <TouchImageViewer
                  src={`${import.meta.env.VITE_API_URL}${report.image_url}`}
                  alt="Lesion"
                  showControls={true}
                />
                <div className="mt-3 flex items-center justify-between text-sm text-gray-600">
                  <span className="flex items-center gap-1">
                    <Calendar size={16} />
                    {formatDate(report.created_at)}
                  </span>
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getRiskBadgeColor(report.risk_level)}`}>
                    {report.risk_level.toUpperCase()}
                  </span>
                </div>
              </div>

              {/* AI Predictions - All 7 Classes */}
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">AI Predictions (All Classes)</h3>
                <div className="space-y-3">
                  {getPredictionEntries(report.predictions)
                    .sort((a, b) => b[1] - a[1])
                    .map(([type, probability]) => (
                      <div key={type}>
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-sm font-medium text-gray-700">
                            {formatCancerType(type)}
                          </span>
                          <span className="text-sm font-bold text-gray-900">
                            {(probability * 100).toFixed(1)}%
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${
                              probability > 0.5
                                ? 'bg-red-500'
                                : probability > 0.3
                                ? 'bg-orange-500'
                                : 'bg-green-500'
                            }`}
                            style={{ width: `${probability * 100}%` }}
                          />
                        </div>
                      </div>
                    ))}
                </div>
                <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                  <p className="text-xs text-blue-800">
                    <strong>Disclaimer:</strong> This is a 94% probability estimate. Please consult verified doctors for clinical biopsy.
                  </p>
                </div>
              </div>
            </div>

            {/* Right Column - Patient Info and Notes */}
            <div className="space-y-6">
              {/* Patient Health Profile */}
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Patient Health Profile</h3>
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <User className="text-gray-400" size={20} />
                    <div>
                      <p className="text-sm text-gray-600">Patient Name</p>
                      <p className="font-medium">{report.patient?.fullName || 'N/A'}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Calendar className="text-gray-400" size={20} />
                    <div>
                      <p className="text-sm text-gray-600">Age</p>
                      <p className="font-medium">{report.patient?.age || 'N/A'} years</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <MapPin className="text-gray-400" size={20} />
                    <div>
                      <p className="text-sm text-gray-600">Fitzpatrick Skin Type</p>
                      <p className="font-medium">Type {report.patient?.fitzpatrick_scale || 'N/A'}</p>
                    </div>
                  </div>
                  {report.patient?.family_history && (
                    <div>
                      <p className="text-sm text-gray-600 mb-1">Family History</p>
                      <p className="text-sm bg-gray-50 p-3 rounded-lg">
                        {report.patient.family_history}
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* Symptoms */}
              {report.symptoms && (
                <div className="card">
                  <h3 className="text-lg font-semibold mb-4">Reported Symptoms</h3>
                  <div className="space-y-3">
                    <div>
                      <p className="text-sm text-gray-600">Body Location</p>
                      <p className="font-medium">{report.symptoms.body_location}</p>
                    </div>
                    {report.symptoms.sensations && report.symptoms.sensations.length > 0 && (
                      <div>
                        <p className="text-sm text-gray-600 mb-1">Sensations</p>
                        <div className="flex flex-wrap gap-2">
                          {report.symptoms.sensations.map((sensation) => (
                            <span
                              key={sensation}
                              className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                            >
                              {sensation}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {report.symptoms.visual_changes && report.symptoms.visual_changes.length > 0 && (
                      <div>
                        <p className="text-sm text-gray-600 mb-1">Visual Changes</p>
                        <div className="flex flex-wrap gap-2">
                          {report.symptoms.visual_changes.map((change) => (
                            <span
                              key={change}
                              className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm"
                            >
                              {change}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {report.symptoms.duration && (
                      <div>
                        <p className="text-sm text-gray-600">Duration</p>
                        <p className="font-medium">{report.symptoms.duration}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Consultation Notes Editor */}
              <div className="card">
                <h3 className="text-lg font-semibold mb-4">Consultation Notes</h3>
                <textarea
                  value={consultationNotes}
                  onChange={(e) => setConsultationNotes(e.target.value)}
                  placeholder="Enter your consultation notes here..."
                  className="w-full h-40 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
                />
                <button
                  onClick={handleSaveNotes}
                  disabled={saving}
                  className="mt-3 btn-primary w-full flex items-center justify-center gap-2"
                >
                  <Save size={20} />
                  {saving ? 'Saving...' : 'Save Notes'}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
