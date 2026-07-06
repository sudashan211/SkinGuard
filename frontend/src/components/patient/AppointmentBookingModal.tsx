import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Calendar, Clock, Video, MapPin, AlertCircle } from 'lucide-react'
import { useForm } from 'react-hook-form'
import type { Doctor } from '@/types/doctor'
import type { AppointmentCreateRequest } from '@/types/appointment'
import { appointmentService } from '@/services/appointment'

interface AppointmentBookingModalProps {
  isOpen: boolean
  onClose: () => void
  doctor: Doctor
  reportId?: string
  onSuccess?: () => void
}

interface AppointmentFormData {
  consultationType: 'in_person' | 'video'
  date: string
  time: string
}

export default function AppointmentBookingModal({
  isOpen,
  onClose,
  doctor,
  reportId,
  onSuccess,
}: AppointmentBookingModalProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
    reset,
  } = useForm<AppointmentFormData>({
    defaultValues: {
      consultationType: 'in_person',
      date: '',
      time: '',
    },
  })

  const consultationType = watch('consultationType')

  const handleClose = () => {
    reset()
    setError(null)
    setSuccess(false)
    onClose()
  }

  const onSubmit = async (data: AppointmentFormData) => {
    try {
      setIsSubmitting(true)
      setError(null)

      // Combine date and time into ISO string
      const scheduledAt = new Date(`${data.date}T${data.time}`).toISOString()

      const appointmentData: AppointmentCreateRequest = {
        doctorId: doctor.id,
        reportId,
        scheduledAt,
        consultationType: data.consultationType,
      }

      await appointmentService.createAppointment(appointmentData)

      setSuccess(true)
      
      // Close modal after 2 seconds
      setTimeout(() => {
        handleClose()
        if (onSuccess) {
          onSuccess()
        }
      }, 2000)
    } catch (err: any) {
      console.error('Error creating appointment:', err)
      setError(
        err.response?.data?.detail?.message ||
          err.response?.data?.message ||
          'Failed to book appointment. Please try again.'
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  // Get minimum date (today)
  const getMinDate = () => {
    const today = new Date()
    return today.toISOString().split('T')[0]
  }

  // Get minimum time (current time if today is selected)
  const getMinTime = (selectedDate: string) => {
    const today = new Date().toISOString().split('T')[0]
    if (selectedDate === today) {
      const now = new Date()
      const hours = String(now.getHours()).padStart(2, '0')
      const minutes = String(now.getMinutes()).padStart(2, '0')
      return `${hours}:${minutes}`
    }
    return '00:00'
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleClose}
            className="fixed inset-0 bg-black bg-opacity-50 z-40"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
          >
            <div className="bg-white rounded-xl shadow-2xl max-w-md w-full max-h-[90vh] overflow-y-auto">
              {/* Header */}
              <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
                <h2 className="text-xl font-semibold text-gray-900">Book Appointment</h2>
                <button
                  onClick={handleClose}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                  disabled={isSubmitting}
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Content */}
              <div className="px-6 py-4">
                {/* Success message */}
                {success && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg"
                  >
                    <p className="text-green-800 text-sm font-medium">
                      Appointment booked successfully! Redirecting...
                    </p>
                  </motion.div>
                )}

                {/* Error message */}
                {error && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2"
                  >
                    <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                    <p className="text-red-800 text-sm">{error}</p>
                  </motion.div>
                )}

                {/* Doctor info */}
                <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-semibold text-gray-900 mb-1">{doctor.clinicName}</h3>
                  {doctor.fullName && (
                    <p className="text-sm text-gray-600">Dr. {doctor.fullName}</p>
                  )}
                  {doctor.specialization && (
                    <p className="text-sm text-gray-500 mt-1">{doctor.specialization}</p>
                  )}
                </div>

                {/* Form */}
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
                  {/* Consultation type */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-3">
                      Consultation Type
                    </label>
                    <div className="grid grid-cols-2 gap-3">
                      <label
                        className={`relative flex items-center justify-center p-4 border-2 rounded-lg cursor-pointer transition-all ${
                          consultationType === 'in_person'
                            ? 'border-blue-600 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <input
                          type="radio"
                          value="in_person"
                          {...register('consultationType')}
                          className="sr-only"
                        />
                        <div className="text-center">
                          <MapPin
                            className={`w-6 h-6 mx-auto mb-2 ${
                              consultationType === 'in_person'
                                ? 'text-blue-600'
                                : 'text-gray-400'
                            }`}
                          />
                          <span
                            className={`text-sm font-medium ${
                              consultationType === 'in_person'
                                ? 'text-blue-900'
                                : 'text-gray-700'
                            }`}
                          >
                            In-Person
                          </span>
                        </div>
                      </label>

                      <label
                        className={`relative flex items-center justify-center p-4 border-2 rounded-lg cursor-pointer transition-all ${
                          consultationType === 'video'
                            ? 'border-blue-600 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <input
                          type="radio"
                          value="video"
                          {...register('consultationType')}
                          className="sr-only"
                        />
                        <div className="text-center">
                          <Video
                            className={`w-6 h-6 mx-auto mb-2 ${
                              consultationType === 'video' ? 'text-blue-600' : 'text-gray-400'
                            }`}
                          />
                          <span
                            className={`text-sm font-medium ${
                              consultationType === 'video' ? 'text-blue-900' : 'text-gray-700'
                            }`}
                          >
                            Video Call
                          </span>
                        </div>
                      </label>
                    </div>
                  </div>

                  {/* Date picker */}
                  <div>
                    <label htmlFor="date" className="block text-sm font-medium text-gray-700 mb-2">
                      Date
                    </label>
                    <div className="relative">
                      <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                      <input
                        id="date"
                        type="date"
                        min={getMinDate()}
                        {...register('date', {
                          required: 'Date is required',
                          validate: value => {
                            const selectedDate = new Date(value)
                            const today = new Date()
                            today.setHours(0, 0, 0, 0)
                            return (
                              selectedDate >= today || 'Date must be today or in the future'
                            )
                          },
                        })}
                        className={`w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                          errors.date ? 'border-red-300' : 'border-gray-300'
                        }`}
                      />
                    </div>
                    {errors.date && (
                      <p className="mt-1 text-sm text-red-600">{errors.date.message}</p>
                    )}
                  </div>

                  {/* Time picker */}
                  <div>
                    <label htmlFor="time" className="block text-sm font-medium text-gray-700 mb-2">
                      Time
                    </label>
                    <div className="relative">
                      <Clock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                      <input
                        id="time"
                        type="time"
                        min={watch('date') ? getMinTime(watch('date')) : '00:00'}
                        {...register('time', {
                          required: 'Time is required',
                          validate: value => {
                            const selectedDate = watch('date')
                            if (!selectedDate) return true

                            const appointmentDateTime = new Date(`${selectedDate}T${value}`)
                            const now = new Date()

                            return (
                              appointmentDateTime > now ||
                              'Appointment time must be in the future'
                            )
                          },
                        })}
                        className={`w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                          errors.time ? 'border-red-300' : 'border-gray-300'
                        }`}
                      />
                    </div>
                    {errors.time && (
                      <p className="mt-1 text-sm text-red-600">{errors.time.message}</p>
                    )}
                  </div>

                  {/* Info message */}
                  <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="text-sm text-blue-800">
                      {consultationType === 'video'
                        ? 'You will receive a video call link via email before the appointment.'
                        : 'Please arrive at the clinic 10 minutes before your scheduled time.'}
                    </p>
                  </div>

                  {/* Action buttons */}
                  <div className="flex gap-3 pt-2">
                    <button
                      type="button"
                      onClick={handleClose}
                      disabled={isSubmitting}
                      className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={isSubmitting || success}
                      className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isSubmitting ? 'Booking...' : 'Book Appointment'}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
