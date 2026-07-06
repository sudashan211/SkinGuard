import { useState, useEffect } from 'react'
import { AlertCircle, Clock, User, MapPin, ChevronDown, ChevronRight } from 'lucide-react'
import type { MedicalReport } from '@/types/patient'
import type { PatientProfile } from '@/types/patient'
import api from '@/services/api'
import ReportDetailView from './ReportDetailView'

interface ReportWithPatient extends MedicalReport {
  patient?: {
    fullName: string
    age: number
    fitzpatrick_scale: string
  }
}

export default function PendingReportsView() {
  const [reports, setReports] = useState<ReportWithPatient[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'urgent' | 'safe'>('all')
  const [selectedReportId, setSelectedReportId] = useState<string | null>(null)
  const [expandedPatients, setExpandedPatients] = useState<Set<string>>(new Set())

  useEffect(() => {
    fetchPendingReports()
  }, [filter])

  const fetchPendingReports = async () => {
    try {
      setLoading(true)
      const response = await api.get<ReportWithPatient[]>('/api/doctors/reports/pending', {
        params: { filter }
      })
      setReports(response.data)
    } catch (error) {
      console.error('Failed to fetch pending reports:', error)
    } finally {
      setLoading(false)
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

  const getTopPrediction = (predictions: any) => {
    const entries = Object.entries(predictions) as [string, number][]
    const sorted = entries.sort((a, b) => b[1] - a[1])
    return {
      type: sorted[0][0].replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      probability: (sorted[0][1] * 100).toFixed(1)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const togglePatient = (patientId: string) => {
    setExpandedPatients(prev => {
      const newSet = new Set(prev)
      if (newSet.has(patientId)) {
        newSet.delete(patientId)
      } else {
        newSet.add(patientId)
      }
      return newSet
    })
  }

  // Group reports by patient
  const groupedReports = reports.reduce((acc, report) => {
    const patientId = report.patient_id
    if (!acc[patientId]) {
      acc[patientId] = {
        patientName: report.patient?.fullName || 'Unknown Patient',
        patientEmail: report.patient?.email || 'N/A',
        patientAge: report.patient?.age || 'N/A',
        patientSkinType: report.patient?.fitzpatrick_scale || 'N/A',
        reports: []
      }
    }
    acc[patientId].reports.push(report)
    return acc
  }, {} as Record<string, { patientName: string; patientEmail: string; patientAge: number | string; patientSkinType: string; reports: ReportWithPatient[] }>)

  // Sort each patient's reports: urgent first, then by date
  Object.values(groupedReports).forEach(group => {
    group.reports.sort((a, b) => {
      if (a.risk_level === 'urgent' && b.risk_level !== 'urgent') return -1
      if (a.risk_level !== 'urgent' && b.risk_level === 'urgent') return 1
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    })
  })

  // Sort patient groups: patients with urgent reports first
  const sortedPatientGroups = Object.entries(groupedReports).sort(([, a], [, b]) => {
    const aHasUrgent = a.reports.some(r => r.risk_level === 'urgent')
    const bHasUrgent = b.reports.some(r => r.risk_level === 'urgent')
    if (aHasUrgent && !bHasUrgent) return -1
    if (!aHasUrgent && bHasUrgent) return 1
    return 0
  })

  const totalReports = reports.length
  const urgentCount = reports.filter(r => r.risk_level === 'urgent').length

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Pending Reports</h2>
        
        {/* Filter buttons */}
        <div className="flex gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === 'all'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            All Reports
          </button>
          <button
            onClick={() => setFilter('urgent')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === 'urgent'
                ? 'bg-red-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Urgent Only
          </button>
          <button
            onClick={() => setFilter('safe')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === 'safe'
                ? 'bg-green-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Safe Cases
          </button>
        </div>
      </div>

      {/* Reports count */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-800">
          <strong>{totalReports}</strong> pending report{totalReports !== 1 ? 's' : ''} from{' '}
          <strong>{sortedPatientGroups.length}</strong> patient{sortedPatientGroups.length !== 1 ? 's' : ''}
          {urgentCount > 0 && (
            <span className="ml-2">
              • <strong className="text-red-600">{urgentCount}</strong> urgent case{urgentCount !== 1 ? 's' : ''}
            </span>
          )}
        </p>
      </div>

      {/* Reports grouped by patient */}
      {sortedPatientGroups.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-600">No pending reports found</p>
        </div>
      ) : (
        <div className="space-y-6">
          {sortedPatientGroups.map(([patientId, group]) => {
            const isExpanded = expandedPatients.has(patientId)
            
            return (
              <div key={patientId} className="border-2 border-gray-200 rounded-lg bg-white overflow-hidden">
                {/* Patient header - Clickable */}
                <div 
                  className="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
                  onClick={() => togglePatient(patientId)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3 flex-1">
                      {/* Expand/Collapse Icon */}
                      <div className="flex-shrink-0">
                        {isExpanded ? (
                          <ChevronDown size={24} className="text-gray-600" />
                        ) : (
                          <ChevronRight size={24} className="text-gray-600" />
                        )}
                      </div>
                      
                      <div className="flex-1">
                        <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                          <User size={20} className="text-primary-600" />
                          {group.patientName}
                        </h3>
                        <div className="flex items-center gap-4 mt-1 text-sm text-gray-600">
                          <span>Age: {group.patientAge}</span>
                          <span>Skin Type: {group.patientSkinType}</span>
                          <span>Email: {group.patientEmail}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="text-right flex-shrink-0 ml-4">
                      <span className="text-sm font-medium text-gray-700">
                        {group.reports.length} report{group.reports.length !== 1 ? 's' : ''}
                      </span>
                      {group.reports.some(r => r.risk_level === 'urgent') && (
                        <div className="mt-1">
                          <span className="px-2 py-1 bg-red-100 text-red-800 text-xs font-semibold rounded-full">
                            HAS URGENT CASES
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Patient's reports - Only shown when expanded */}
                {isExpanded && (
                  <div className="border-t border-gray-200 p-4 bg-gray-50">
                    <div className="space-y-3">
                      {group.reports.map((report) => {
                  const topPrediction = getTopPrediction(report.predictions)
                  
                  return (
                    <div
                      key={report.id}
                      className={`card hover:shadow-lg transition-shadow cursor-pointer ${
                        report.risk_level === 'urgent' ? 'border-2 border-red-300 bg-red-50' : 'bg-white'
                      }`}
                      onClick={(e) => {
                        e.stopPropagation() // Prevent triggering parent click
                        setSelectedReportId(report.id)
                      }}
                    >
                        <div className="flex gap-4">
                          {/* Image thumbnail */}
                          <div className="flex-shrink-0">
                            <img
                              src={`${import.meta.env.VITE_API_URL}${report.thumbnail_url || report.image_url}`}
                              alt="Lesion"
                              className="w-24 h-24 object-cover rounded-lg"
                            />
                          </div>

                          {/* Report details */}
                          <div className="flex-1 min-w-0">
                            <div className="flex items-start justify-between mb-2">
                              <div>
                                <div className="flex items-center gap-2 mb-1">
                                  {report.risk_level === 'urgent' && (
                                    <AlertCircle className="text-red-600" size={18} />
                                  )}
                                  <h4 className="text-base font-semibold text-gray-900">
                                    Report from {formatDate(report.created_at)}
                                  </h4>
                                </div>
                                <div className="flex items-center gap-3 text-xs text-gray-600">
                                  <span className="flex items-center gap-1">
                                    <MapPin size={14} />
                                    {report.symptoms?.body_location || 'Location not specified'}
                                  </span>
                                  <span className="flex items-center gap-1">
                                    <Clock size={14} />
                                    {formatDate(report.created_at)}
                                  </span>
                                </div>
                              </div>
                              
                              <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getRiskBadgeColor(report.risk_level)}`}>
                                {report.risk_level.toUpperCase()}
                              </span>
                            </div>

                            {/* AI Predictions */}
                            <div className="mt-2 p-2 bg-white rounded-lg border border-gray-200">
                              <p className="text-xs font-medium text-gray-700 mb-1">
                                Top AI Prediction:
                              </p>
                              <div className="flex items-center justify-between">
                                <span className="text-sm text-gray-900 font-semibold">
                                  {topPrediction.type}
                                </span>
                                <span className="text-sm font-bold text-primary-600">
                                  {topPrediction.probability}%
                                </span>
                              </div>
                            </div>

                            {/* Symptoms preview */}
                            {report.symptoms && report.symptoms.sensations && report.symptoms.sensations.length > 0 && (
                              <div className="mt-2 text-xs text-gray-600">
                                <span className="font-medium">Symptoms:</span> {report.symptoms.sensations.join(', ')}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )}

      {/* Report Detail Modal */}
      {selectedReportId && (
        <ReportDetailView
          reportId={selectedReportId}
          onClose={() => setSelectedReportId(null)}
        />
      )}
    </div>
  )
}
