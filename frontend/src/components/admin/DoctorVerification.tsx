import { useState, useEffect } from 'react'
import { CheckCircle, XCircle, MapPin, Phone, FileText, Loader2 } from 'lucide-react'
import { adminService } from '@/services/admin'
import type { PendingDoctor } from '@/types/admin'
import { useToast } from '@/hooks/useToast'

export default function DoctorVerification() {
  const [doctors, setDoctors] = useState<PendingDoctor[]>([])
  const [loading, setLoading] = useState(true)
  const [processingId, setProcessingId] = useState<string | null>(null)
  const { showToast } = useToast()

  useEffect(() => {
    loadPendingDoctors()
  }, [])

  const loadPendingDoctors = async () => {
    try {
      setLoading(true)
      const data = await adminService.getPendingDoctors()
      setDoctors(data)
    } catch (error) {
      showToast('Failed to load pending doctors', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleVerification = async (doctorId: string, approved: boolean) => {
    try {
      setProcessingId(doctorId)
      await adminService.verifyDoctor(doctorId, approved)
      showToast(
        `Doctor ${approved ? 'approved' : 'rejected'} successfully`,
        'success'
      )
      // Remove from list
      setDoctors(doctors.filter(d => d.id !== doctorId))
    } catch (error) {
      showToast('Failed to process verification', 'error')
    } finally {
      setProcessingId(null)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="animate-spin text-primary-600" size={32} />
      </div>
    )
  }

  if (doctors.length === 0) {
    return (
      <div className="card text-center py-12">
        <p className="text-gray-600">No pending doctor applications</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold mb-6">Doctor Verification</h2>
      
      {doctors.map(doctor => (
        <div key={doctor.id} className="card">
          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
            <div className="flex-1 space-y-3">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  {doctor.fullName}
                </h3>
                <p className="text-sm text-gray-600">{doctor.email}</p>
              </div>

              <div className="grid md:grid-cols-2 gap-3">
                <div className="flex items-start gap-2">
                  <FileText className="text-gray-400 mt-0.5" size={18} />
                  <div>
                    <p className="text-xs text-gray-500">License Number</p>
                    <p className="text-sm font-medium">{doctor.licenseNo}</p>
                  </div>
                </div>

                <div className="flex items-start gap-2">
                  <MapPin className="text-gray-400 mt-0.5" size={18} />
                  <div>
                    <p className="text-xs text-gray-500">Clinic</p>
                    <p className="text-sm font-medium">{doctor.clinicName}</p>
                  </div>
                </div>

                <div className="flex items-start gap-2">
                  <Phone className="text-gray-400 mt-0.5" size={18} />
                  <div>
                    <p className="text-xs text-gray-500">WhatsApp</p>
                    <p className="text-sm font-medium">{doctor.whatsappNo}</p>
                  </div>
                </div>

                {doctor.specialization && (
                  <div className="flex items-start gap-2">
                    <FileText className="text-gray-400 mt-0.5" size={18} />
                    <div>
                      <p className="text-xs text-gray-500">Specialization</p>
                      <p className="text-sm font-medium">{doctor.specialization}</p>
                    </div>
                  </div>
                )}
              </div>

              <div className="flex items-start gap-2">
                <MapPin className="text-gray-400 mt-0.5" size={18} />
                <div>
                  <p className="text-xs text-gray-500">Location Coordinates</p>
                  <p className="text-sm font-mono">
                    {doctor.lat.toFixed(6)}, {doctor.lng.toFixed(6)}
                  </p>
                </div>
              </div>

              <div className="text-xs text-gray-500">
                Applied: {new Date(doctor.createdAt).toLocaleDateString()}
              </div>
            </div>

            <div className="flex md:flex-col gap-2">
              <button
                onClick={() => handleVerification(doctor.id, true)}
                disabled={processingId === doctor.id}
                className="btn btn-primary flex items-center gap-2 flex-1 md:flex-initial"
              >
                {processingId === doctor.id ? (
                  <Loader2 className="animate-spin" size={18} />
                ) : (
                  <CheckCircle size={18} />
                )}
                Approve
              </button>
              <button
                onClick={() => handleVerification(doctor.id, false)}
                disabled={processingId === doctor.id}
                className="btn btn-outline border-danger-300 text-danger-600 hover:bg-danger-50 flex items-center gap-2 flex-1 md:flex-initial"
              >
                <XCircle size={18} />
                Reject
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
