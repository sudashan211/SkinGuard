import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Save, User, MapPin, Phone, Award, BookOpen, Globe, Clock, Star } from 'lucide-react'
import { useToast } from '@/hooks/useToast'
import api from '@/services/api'

interface DoctorProfile {
  id: string
  user_id: string
  license_no: string
  clinic_name: string
  lat: number
  lng: number
  whatsapp_no: string
  specialization: string
  bio?: string
  education?: string
  certifications?: string
  languages?: string
  clinic_hours?: string
  average_rating: number
  review_count: number
  verified: boolean
}

interface Review {
  id: string
  patient_name: string
  rating: number
  comment: string
  created_at: string
}

export default function DoctorProfilePage() {
  const toast = useToast()
  const queryClient = useQueryClient()
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState<Partial<DoctorProfile>>({})

  // Fetch doctor profile
  const { data: profile, isLoading } = useQuery({
    queryKey: ['doctorProfile'],
    queryFn: async () => {
      const response = await api.get<DoctorProfile>('/api/doctors/profile')
      return response.data
    },
  })

  // Fetch reviews
  const { data: reviews = [] } = useQuery({
    queryKey: ['doctorReviews', profile?.id],
    queryFn: async () => {
      if (!profile?.id) return []
      const response = await api.get<{ reviews: Review[] }>(`/api/reviews/doctors/${profile.id}`)
      return response.data.reviews
    },
    enabled: !!profile?.id,
  })

  // Load profile data when available
  useEffect(() => {
    if (profile) {
      setFormData(profile)
    }
  }, [profile])

  // Update profile mutation
  const updateMutation = useMutation({
    mutationFn: async (data: Partial<DoctorProfile>) => {
      const response = await api.put('/api/doctors/profile', data)
      return response.data
    },
    onSuccess: () => {
      toast.success('Profile updated successfully!')
      setIsEditing(false)
      queryClient.invalidateQueries({ queryKey: ['doctorProfile'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail?.message || 'Failed to update profile')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    updateMutation.mutate(formData)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="card">
        <p className="text-gray-600">No profile found. Please register your hospital/clinic first.</p>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Hospital/Clinic Profile</h1>
          <p className="text-gray-600 mt-1">Manage your facility information</p>
        </div>
        {!isEditing && (
          <button
            onClick={() => setIsEditing(true)}
            className="btn btn-primary"
          >
            Edit Profile
          </button>
        )}
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {/* Left Column - Profile Form */}
        <div className="md:col-span-2 space-y-6">
          <form onSubmit={handleSubmit} className="card">
            <h2 className="text-xl font-semibold mb-4">Facility Information</h2>

            {/* License Number (Read-only) */}
            <div className="mb-4">
              <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
                <Award className="mr-2" size={18} />
                Medical License Number
              </label>
              <input
                type="text"
                value={profile.license_no}
                className="input bg-gray-50"
                disabled
              />
              <p className="text-xs text-gray-500 mt-1">License number cannot be changed</p>
            </div>

            {/* Clinic Name */}
            <div className="mb-4">
              <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
                <MapPin className="mr-2" size={18} />
                Hospital/Clinic Name
              </label>
              <input
                type="text"
                value={formData.clinic_name || ''}
                onChange={(e) => setFormData({ ...formData, clinic_name: e.target.value })}
                className="input"
                disabled={!isEditing}
                required
              />
            </div>

            {/* WhatsApp Number */}
            <div className="mb-4">
              <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
                <Phone className="mr-2" size={18} />
                WhatsApp Number
              </label>
              <input
                type="tel"
                value={formData.whatsapp_no || ''}
                onChange={(e) => setFormData({ ...formData, whatsapp_no: e.target.value })}
                className="input"
                placeholder="+1234567890"
                disabled={!isEditing}
                required
              />
            </div>

            {/* Specialization */}
            <div className="mb-4">
              <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
                <User className="mr-2" size={18} />
                Specialization
              </label>
              <input
                type="text"
                value={formData.specialization || ''}
                onChange={(e) => setFormData({ ...formData, specialization: e.target.value })}
                className="input"
                placeholder="e.g., Dermatology, Oncology"
                disabled={!isEditing}
                required
              />
            </div>

            {/* Bio */}
            <div className="mb-4">
              <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
                <User className="mr-2" size={18} />
                Facility Description
              </label>
              <textarea
                value={formData.bio || ''}
                onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                className="input"
                rows={4}
                placeholder="Brief description of your facility and services..."
                disabled={!isEditing}
              />
            </div>

            {/* Education */}
            <div className="mb-4">
              <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
                <BookOpen className="mr-2" size={18} />
                Education
              </label>
              <textarea
                value={formData.education || ''}
                onChange={(e) => setFormData({ ...formData, education: e.target.value })}
                className="input"
                rows={3}
                placeholder="Medical school and training..."
                disabled={!isEditing}
              />
            </div>

            {/* Certifications */}
            <div className="mb-4">
              <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
                <Award className="mr-2" size={18} />
                Certifications
              </label>
              <textarea
                value={formData.certifications || ''}
                onChange={(e) => setFormData({ ...formData, certifications: e.target.value })}
                className="input"
                rows={3}
                placeholder="Board certifications..."
                disabled={!isEditing}
              />
            </div>

            {/* Languages */}
            <div className="mb-4">
              <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
                <Globe className="mr-2" size={18} />
                Languages Spoken
              </label>
              <input
                type="text"
                value={formData.languages || ''}
                onChange={(e) => setFormData({ ...formData, languages: e.target.value })}
                className="input"
                placeholder="e.g., English, Spanish, French"
                disabled={!isEditing}
              />
            </div>

            {/* Clinic Hours */}
            <div className="mb-4">
              <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
                <Clock className="mr-2" size={18} />
                Operating Hours
              </label>
              <textarea
                value={formData.clinic_hours || ''}
                onChange={(e) => setFormData({ ...formData, clinic_hours: e.target.value })}
                className="input"
                rows={3}
                placeholder="e.g., Mon-Fri: 9AM-5PM, Sat: 10AM-2PM"
                disabled={!isEditing}
              />
            </div>

            {/* Action Buttons */}
            {isEditing && (
              <div className="flex justify-end space-x-3 pt-4 border-t">
                <button
                  type="button"
                  onClick={() => {
                    setIsEditing(false)
                    setFormData(profile)
                  }}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={updateMutation.isPending}
                  className="btn btn-primary flex items-center"
                >
                  <Save className="mr-2" size={18} />
                  {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            )}
          </form>
        </div>

        {/* Right Column - Stats and Reviews */}
        <div className="space-y-6">
          {/* Verification Status */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-3">Verification Status</h3>
            <div className="flex items-center">
              {profile.verified ? (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-success-100 text-success-800">
                  ✓ Verified
                </span>
              ) : (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-warning-100 text-warning-800">
                  ⏳ Pending Verification
                </span>
              )}
            </div>
          </div>

          {/* Rating Stats */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-3">Rating Statistics</h3>
            <div className="text-center py-4">
              <div className="flex items-center justify-center gap-2 mb-2">
                <Star className="text-yellow-500 fill-yellow-500" size={32} />
                <span className="text-4xl font-bold text-gray-900">
                  {profile.average_rating.toFixed(1)}
                </span>
              </div>
              <p className="text-sm text-gray-600">
                Based on {profile.review_count} review{profile.review_count !== 1 ? 's' : ''}
              </p>
            </div>
          </div>

          {/* Recent Reviews */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Recent Reviews</h3>
            {reviews.length === 0 ? (
              <p className="text-sm text-gray-600 text-center py-4">No reviews yet</p>
            ) : (
              <div className="space-y-4">
                {reviews.slice(0, 3).map((review) => (
                  <div key={review.id} className="border-b last:border-b-0 pb-3 last:pb-0">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-gray-900">
                        {review.patient_name}
                      </span>
                      <div className="flex items-center gap-1">
                        {[...Array(5)].map((_, i) => (
                          <Star
                            key={i}
                            size={14}
                            className={
                              i < review.rating
                                ? 'text-yellow-500 fill-yellow-500'
                                : 'text-gray-300'
                            }
                          />
                        ))}
                      </div>
                    </div>
                    {review.comment && (
                      <p className="text-sm text-gray-600">{review.comment}</p>
                    )}
                    <p className="text-xs text-gray-400 mt-1">
                      {new Date(review.created_at).toLocaleDateString()}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
