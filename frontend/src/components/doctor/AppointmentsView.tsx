import { useState, useEffect } from 'react'
import { Calendar, Clock, User, Video, MapPin, ExternalLink } from 'lucide-react'
import type { Appointment } from '@/types/appointment'
import api from '@/services/api'

interface AppointmentWithDetails extends Appointment {
  patient?: {
    fullName: string
    email: string
  }
  report?: {
    id: string
    risk_level: string
  }
}

export default function AppointmentsView() {
  const [appointments, setAppointments] = useState<AppointmentWithDetails[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'upcoming' | 'completed'>('upcoming')
  const [selectedPatient, setSelectedPatient] = useState<string | null>(null)
  const [patientProfile, setPatientProfile] = useState<any>(null)
  const [loadingProfile, setLoadingProfile] = useState(false)

  useEffect(() => {
    fetchAppointments()
  }, [filter])

  const fetchAppointments = async () => {
    try {
      setLoading(true)
      const response = await api.get<AppointmentWithDetails[]>('/api/appointments', {
        params: { filter }
      })
      console.log('Fetched appointments:', response.data)
      response.data.forEach(apt => {
        console.log(`Appointment ${apt.id}: scheduledAt = ${apt.scheduledAt}`)
      })
      setAppointments(response.data)
    } catch (error) {
      console.error('Failed to fetch appointments:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleStatusUpdate = async (appointmentId: string, newStatus: string) => {
    try {
      await api.put(`/api/appointments/${appointmentId}`, {
        status: newStatus
      })
      fetchAppointments()
    } catch (error) {
      console.error('Failed to update appointment status:', error)
      alert('Failed to update appointment status')
    }
  }

  const handleViewPatientProfile = async (patientId: string) => {
    try {
      setLoadingProfile(true)
      setSelectedPatient(patientId)
      
      // Fetch patient profile and health data
      const response = await api.get(`/api/patients/${patientId}/profile`)
      setPatientProfile(response.data)
    } catch (error) {
      console.error('Failed to fetch patient profile:', error)
      alert('Failed to load patient profile')
      setSelectedPatient(null)
    } finally {
      setLoadingProfile(false)
    }
  }

  const closePatientProfile = () => {
    setSelectedPatient(null)
    setPatientProfile(null)
  }

  const formatDate = (dateString: string) => {
    if (!dateString) return 'Invalid Date'
    try {
      const date = new Date(dateString)
      if (isNaN(date.getTime())) return 'Invalid Date'
      return date.toLocaleDateString('en-US', {
        weekday: 'long',
        month: 'long',
        day: 'numeric',
        year: 'numeric'
      })
    } catch (error) {
      return 'Invalid Date'
    }
  }

  const formatTime = (dateString: string) => {
    if (!dateString) return 'Invalid Time'
    try {
      const date = new Date(dateString)
      if (isNaN(date.getTime())) return 'Invalid Time'
      return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch (error) {
      return 'Invalid Time'
    }
  }

  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'completed':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'cancelled':
        return 'bg-red-100 text-red-800 border-red-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const isUpcoming = (dateString: string) => {
    if (!dateString) return false
    try {
      const date = new Date(dateString)
      if (isNaN(date.getTime())) return false
      return date > new Date()
    } catch (error) {
      return false
    }
  }

  const isValidDate = (dateString: string | Date | null | undefined) => {
    if (!dateString) return false
    try {
      const date = new Date(dateString)
      return date instanceof Date && !isNaN(date.getTime()) && date.getTime() > 0
    } catch (error) {
      return false
    }
  }

  const sortedAppointments = [...appointments].sort((a, b) => {
    return new Date(a.scheduledAt).getTime() - new Date(b.scheduledAt).getTime()
  })

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
        <h2 className="text-2xl font-bold text-gray-900">My Appointments</h2>
        
        {/* Filter buttons */}
        <div className="flex gap-2">
          <button
            onClick={() => setFilter('upcoming')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === 'upcoming'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Upcoming
          </button>
          <button
            onClick={() => setFilter('completed')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === 'completed'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Completed
          </button>
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filter === 'all'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            All
          </button>
        </div>
      </div>

      {/* Appointments count */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-800">
          <strong>{sortedAppointments.length}</strong> appointment{sortedAppointments.length !== 1 ? 's' : ''}
          {filter === 'upcoming' && sortedAppointments.length > 0 && sortedAppointments[0].scheduledAt && !isNaN(new Date(sortedAppointments[0].scheduledAt).getTime()) && (
            <span className="ml-2">
              • Next appointment: {formatDate(sortedAppointments[0].scheduledAt)}
            </span>
          )}
        </p>
      </div>

      {/* Appointments list */}
      {sortedAppointments.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <Calendar className="mx-auto text-gray-400 mb-3" size={48} />
          <p className="text-gray-600">No appointments found</p>
        </div>
      ) : (
        <div className="space-y-4">
          {sortedAppointments.map((appointment) => (
            <div
              key={appointment.id}
              className={`card hover:shadow-lg transition-shadow ${
                isUpcoming(appointment.scheduledAt) && appointment.status === 'confirmed'
                  ? 'border-l-4 border-l-green-500'
                  : ''
              }`}
            >
              <div className="flex gap-4">
                {/* Date/Time Section */}
                <div className="flex-shrink-0 text-center p-4 bg-gray-50 rounded-lg">
                  {isValidDate(appointment.scheduledAt) ? (
                    <>
                      <div className="text-3xl font-bold text-primary-600">
                        {new Date(appointment.scheduledAt).getDate()}
                      </div>
                      <div className="text-sm text-gray-600">
                        {new Date(appointment.scheduledAt).toLocaleDateString('en-US', { month: 'short' })}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {formatTime(appointment.scheduledAt)}
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="text-3xl font-bold text-gray-400">?</div>
                      <div className="text-sm text-gray-500">N/A</div>
                      <div className="text-xs text-gray-400 mt-1">N/A</div>
                    </>
                  )}
                </div>

                {/* Appointment Details */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h3 
                        className={`text-lg font-semibold text-gray-900 ${
                          appointment.status === 'confirmed' || appointment.status === 'completed' 
                            ? 'cursor-pointer hover:text-blue-600 hover:underline' 
                            : ''
                        }`}
                        onClick={() => {
                          if ((appointment.status === 'confirmed' || appointment.status === 'completed') && appointment.patientId) {
                            handleViewPatientProfile(appointment.patientId)
                          }
                        }}
                      >
                        {appointment.status === 'confirmed' || appointment.status === 'completed'
                          ? appointment.patient?.fullName || 'Unknown Patient'
                          : 'Unknown Patient'}
                      </h3>
                      <div className="flex items-center gap-4 text-sm text-gray-600 mt-1">
                        <span className="flex items-center gap-1">
                          <User size={16} />
                          {appointment.status === 'confirmed' || appointment.status === 'completed'
                            ? appointment.patient?.email || 'N/A'
                            : 'N/A'}
                        </span>
                        <span className="flex items-center gap-1">
                          {appointment.consultationType === 'video' ? (
                            <>
                              <Video size={16} />
                              Video Consultation
                            </>
                          ) : (
                            <>
                              <MapPin size={16} />
                              In-Person
                            </>
                          )}
                        </span>
                      </div>
                    </div>
                    
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getStatusBadgeColor(appointment.status)}`}>
                      {appointment.status.toUpperCase()}
                    </span>
                  </div>

                  {/* Privacy Notice for Pending Appointments */}
                  {appointment.status === 'pending' && (
                    <div className="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-sm">
                      <p className="text-yellow-800 font-medium">
                        🔒 Patient details are hidden for privacy
                      </p>
                      <p className="text-yellow-700 text-xs mt-1">
                        Confirm this appointment to view patient information and medical reports
                      </p>
                    </div>
                  )}

                  {/* Report Link - Only visible after confirmation */}
                  {appointment.reportId && (appointment.status === 'confirmed' || appointment.status === 'completed') && (
                    <div className="mt-2 p-2 bg-blue-50 rounded-lg text-sm">
                      <span className="text-blue-800">
                        Related Report: {appointment.reportId.slice(0, 8)}...
                        {appointment.report?.risk_level && (
                          <span className={`ml-2 px-2 py-0.5 rounded text-xs ${
                            appointment.report.risk_level === 'urgent'
                              ? 'bg-red-100 text-red-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}>
                            {appointment.report.risk_level}
                          </span>
                        )}
                      </span>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="mt-3 flex gap-2">
                    {appointment.status === 'pending' && (
                      <>
                        <button
                          onClick={() => handleStatusUpdate(appointment.id, 'confirmed')}
                          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium"
                        >
                          Confirm
                        </button>
                        <button
                          onClick={() => handleStatusUpdate(appointment.id, 'cancelled')}
                          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm font-medium"
                        >
                          Cancel
                        </button>
                      </>
                    )}
                    
                    {appointment.status === 'confirmed' && isUpcoming(appointment.scheduledAt) && (
                      <button
                        onClick={() => handleStatusUpdate(appointment.id, 'completed')}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                      >
                        Mark as Completed
                      </button>
                    )}

                    {/* Video Consultation Link */}
                    {appointment.consultationType === 'video' && 
                     appointment.videoRoomUrl && 
                     isUpcoming(appointment.scheduledAt) &&
                     appointment.status === 'confirmed' && (
                      <a
                        href={appointment.videoRoomUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium flex items-center gap-2"
                      >
                        <Video size={16} />
                        Join Video Call
                        <ExternalLink size={14} />
                      </a>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Patient Profile Modal */}
      {selectedPatient && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <h2 className="text-xl font-semibold text-gray-900">Patient Health Profile</h2>
              <button
                onClick={closePatientProfile}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <ExternalLink className="w-5 h-5 rotate-45" />
              </button>
            </div>

            {/* Modal Content */}
            <div className="px-6 py-4">
              {loadingProfile ? (
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
                </div>
              ) : patientProfile ? (
                <div className="space-y-6">
                  {/* Basic Info */}
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-3">Basic Information</h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-gray-500">Full Name</p>
                        <p className="font-medium text-gray-900">{patientProfile.fullName || 'N/A'}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Email</p>
                        <p className="font-medium text-gray-900">{patientProfile.email || 'N/A'}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Age</p>
                        <p className="font-medium text-gray-900">{patientProfile.age || 'N/A'}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Skin Type</p>
                        <p className="font-medium text-gray-900">{patientProfile.skinType || 'N/A'}</p>
                      </div>
                    </div>
                  </div>

                  {/* Medical History */}
                  {patientProfile.familyHistory && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-3">Family History</h3>
                      <p className="text-gray-700">{patientProfile.familyHistory}</p>
                    </div>
                  )}

                  {/* Recent Reports */}
                  {patientProfile.reports && patientProfile.reports.length > 0 && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-3">Recent Skin Analysis Reports</h3>
                      <div className="space-y-3">
                        {patientProfile.reports.map((report: any) => (
                          <div key={report.id} className="border border-gray-200 rounded-lg p-4">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-sm font-medium text-gray-900">
                                {new Date(report.created_at).toLocaleDateString()}
                              </span>
                              <span className={`px-2 py-1 rounded text-xs font-semibold ${
                                report.risk_level === 'urgent' 
                                  ? 'bg-red-100 text-red-800'
                                  : report.risk_level === 'flagged'
                                  ? 'bg-yellow-100 text-yellow-800'
                                  : 'bg-green-100 text-green-800'
                              }`}>
                                {report.risk_level || report.status}
                              </span>
                            </div>
                            {report.body_location && (
                              <p className="text-sm text-gray-600">Location: {report.body_location}</p>
                            )}
                            {report.symptoms && (
                              <p className="text-sm text-gray-600 mt-1">Symptoms: {report.symptoms}</p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-12">
                  <p className="text-gray-600">Failed to load patient profile</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
