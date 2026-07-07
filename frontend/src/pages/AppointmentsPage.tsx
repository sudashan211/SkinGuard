import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, Calendar, Clock, User, MapPin, Plus, X } from 'lucide-react'
import { useToast } from '@/hooks/useToast'
import { ROUTES } from '@/utils/constants'
import { formatDate } from '@/utils/helpers'
import { appointmentService } from '@/services/appointment'
import { doctorService } from '@/services/doctor'

export default function AppointmentsPage() {
  const navigate = useNavigate()
  const toast = useToast()
  const queryClient = useQueryClient()
  const [showBooking, setShowBooking] = useState(false)
  const [selectedTab, setSelectedTab] = useState<'upcoming' | 'past'>('upcoming')
  const [bookingData, setBookingData] = useState({
    doctor_id: '',
    scheduled_at: '',
    time: '',
    consultation_type: 'in_person' as 'in_person' | 'video',
    report_id: null as string | null,
  })

  // Fetch appointments
  const { data: allAppointments = [], isLoading } = useQuery({
    queryKey: ['appointments'],
    queryFn: appointmentService.getAppointments,
  })

  // Debug logging
  console.log('=== APPOINTMENTS DEBUG ===')
  console.log('All appointments:', allAppointments)
  console.log('Number of appointments:', allAppointments.length)
  if (allAppointments.length > 0) {
    console.log('First appointment:', allAppointments[0])
    console.log('scheduledAt:', allAppointments[0].scheduledAt)
    console.log('scheduled_at:', allAppointments[0].scheduled_at)
  }

  // Split appointments into upcoming and past
  const now = new Date()
  const appointments = {
    upcoming: allAppointments.filter((apt: any) => {
      const aptDate = new Date(apt.scheduledAt || apt.scheduled_at)
      console.log('Checking appointment:', apt.id, 'scheduled:', aptDate, 'now:', now, 'future?', aptDate >= now)
      return aptDate >= now && apt.status !== 'cancelled' && apt.status !== 'completed'
    }),
    past: allAppointments.filter((apt: any) => {
      const aptDate = new Date(apt.scheduledAt || apt.scheduled_at)
      return aptDate < now || apt.status === 'cancelled' || apt.status === 'completed'
    }),
  }
  
  console.log('Upcoming appointments:', appointments.upcoming.length)
  console.log('Past appointments:', appointments.past.length)

  // Fetch doctors for booking
  const { data: doctors = [] } = useQuery({
    queryKey: ['doctors'],
    queryFn: () => doctorService.getNearbyDoctors({ lat: 0, lng: 0, radius: 50 }),
    enabled: showBooking,
  })

  // Cancel appointment mutation
  const cancelMutation = useMutation({
    mutationFn: (appointmentId: string) =>
      appointmentService.updateAppointmentStatus(appointmentId, { status: 'cancelled' }),
    onSuccess: () => {
      toast.success('Appointment cancelled successfully')
      queryClient.invalidateQueries({ queryKey: ['appointments'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail?.message || 'Failed to cancel appointment')
    },
  })

  // Book appointment mutation
  const bookMutation = useMutation({
    mutationFn: (data: any) => appointmentService.createAppointment(data),
    onSuccess: () => {
      toast.success('Appointment booked successfully!')
      setShowBooking(false)
      setBookingData({
        doctor_id: '',
        scheduled_at: '',
        time: '',
        consultation_type: 'in_person',
        report_id: null,
      })
      queryClient.invalidateQueries({ queryKey: ['appointments'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail?.message || 'Failed to book appointment')
    },
  })

  const handleCancelAppointment = async (appointmentId: string) => {
    if (confirm('Are you sure you want to cancel this appointment?')) {
      cancelMutation.mutate(appointmentId)
    }
  }

  const handleBookAppointment = (e: React.FormEvent) => {
    e.preventDefault()

    if (!bookingData.doctor_id || !bookingData.scheduled_at || !bookingData.time) {
      toast.error('Please fill in all required fields')
      return
    }

    // Combine date and time
    const scheduledAt = new Date(`${bookingData.scheduled_at}T${bookingData.time}:00`)

    bookMutation.mutate({
      doctor_id: bookingData.doctor_id,
      scheduled_at: scheduledAt.toISOString(),
      consultation_type: bookingData.consultation_type,
      report_id: bookingData.report_id,
    })
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate(ROUTES.PATIENT_DASHBOARD)}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft size={20} className="mr-2" />
          Back to Dashboard
        </button>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Appointments</h1>
            <p className="text-gray-600 mt-2">Manage your doctor appointments</p>
          </div>
          <button
            onClick={() => setShowBooking(true)}
            className="btn btn-primary flex items-center"
          >
            <Plus className="mr-2" size={18} />
            Book Appointment
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex space-x-4 mb-6 border-b">
        <button
          onClick={() => setSelectedTab('upcoming')}
          className={`pb-3 px-4 font-medium transition-colors ${
            selectedTab === 'upcoming'
              ? 'text-primary-600 border-b-2 border-primary-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Upcoming ({appointments.upcoming.length})
        </button>
        <button
          onClick={() => setSelectedTab('past')}
          className={`pb-3 px-4 font-medium transition-colors ${
            selectedTab === 'past'
              ? 'text-primary-600 border-b-2 border-primary-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Past ({appointments.past.length})
        </button>
      </div>

      {/* Appointments List */}
      <div className="space-y-4">
        {isLoading ? (
          <div className="card text-center py-12">
            <p className="text-gray-600">Loading appointments...</p>
          </div>
        ) : appointments[selectedTab].length === 0 ? (
          <div className="card text-center py-12">
            <Calendar className="mx-auto text-gray-400 mb-4" size={48} />
            <p className="text-gray-600">No {selectedTab} appointments</p>
            {selectedTab === 'upcoming' && (
              <button
                onClick={() => setShowBooking(true)}
                className="btn btn-primary mt-4"
              >
                Book Your First Appointment
              </button>
            )}
          </div>
        ) : (
          appointments[selectedTab].map((appointment: any) => (
            <div key={appointment.id} className="card hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center mb-2">
                    <User className="text-primary-600 mr-2" size={20} />
                    <h3 className="text-lg font-semibold">Doctor</h3>
                    <span className="ml-3 text-sm text-gray-600">{appointment.consultationType}</span>
                  </div>

                  <div className="space-y-2 text-sm text-gray-600">
                    <div className="flex items-center">
                      <Calendar className="mr-2" size={16} />
                      {formatDate(appointment.scheduledAt)}
                    </div>
                    <div className="flex items-center">
                      <Clock className="mr-2" size={16} />
                      Status: {appointment.status}
                    </div>
                  </div>

                  <div className="mt-3">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        appointment.status === 'confirmed'
                          ? 'bg-success-100 text-success-800'
                          : appointment.status === 'pending'
                          ? 'bg-warning-100 text-warning-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {appointment.status}
                    </span>
                  </div>
                </div>

                {selectedTab === 'upcoming' && (
                  <div className="flex flex-col space-y-2 ml-4">
                    <button
                      onClick={() => handleCancelAppointment(appointment.id)}
                      className="btn bg-danger-600 hover:bg-danger-700 text-white text-sm"
                      disabled={cancelMutation.isPending}
                    >
                      {cancelMutation.isPending ? 'Cancelling...' : 'Cancel'}
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Booking Modal */}
      {showBooking && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold">Book Appointment</h2>
                <button
                  onClick={() => setShowBooking(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X size={24} />
                </button>
              </div>

              <form onSubmit={handleBookAppointment} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Select Hospital/Clinic <span className="text-danger-600">*</span>
                  </label>
                  <select
                    className="input"
                    value={bookingData.doctor_id}
                    onChange={(e) => setBookingData({ ...bookingData, doctor_id: e.target.value })}
                    required
                  >
                    <option value="">Choose a hospital or clinic...</option>
                    {doctors.map((doctor: any) => (
                      <option key={doctor.id} value={doctor.id}>
                        {doctor.clinic_name} - {doctor.specialization || 'Dermatology'}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Preferred Date <span className="text-danger-600">*</span>
                  </label>
                  <input
                    type="date"
                    className="input"
                    min={new Date().toISOString().split('T')[0]}
                    value={bookingData.scheduled_at}
                    onChange={(e) => setBookingData({ ...bookingData, scheduled_at: e.target.value })}
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Preferred Time <span className="text-danger-600">*</span>
                  </label>
                  <select
                    className="input"
                    value={bookingData.time}
                    onChange={(e) => setBookingData({ ...bookingData, time: e.target.value })}
                    required
                  >
                    <option value="">Select time...</option>
                    <option value="09:00">9:00 AM</option>
                    <option value="10:00">10:00 AM</option>
                    <option value="11:00">11:00 AM</option>
                    <option value="14:00">2:00 PM</option>
                    <option value="15:00">3:00 PM</option>
                    <option value="16:00">4:00 PM</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Consultation Type <span className="text-danger-600">*</span>
                  </label>
                  <select
                    className="input"
                    value={bookingData.consultation_type}
                    onChange={(e) => setBookingData({ ...bookingData, consultation_type: e.target.value as any })}
                    required
                  >
                    <option value="in_person">In-Person</option>
                    <option value="video">Video Consultation</option>
                  </select>
                </div>

                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowBooking(false)}
                    className="btn btn-secondary"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={bookMutation.isPending}
                  >
                    {bookMutation.isPending ? 'Booking...' : 'Book Appointment'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
