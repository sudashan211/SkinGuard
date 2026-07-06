import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { ArrowLeft, Save, User, Calendar, Heart, AlertCircle } from 'lucide-react'
import { useToast } from '@/hooks/useToast'
import { ROUTES } from '@/utils/constants'
import { healthProfileService } from '@/services/healthProfile'

const SKIN_TYPES = [
  { value: 'I', label: 'Type I - Always burns, never tans (Very fair)' },
  { value: 'II', label: 'Type II - Usually burns, tans minimally (Fair)' },
  { value: 'III', label: 'Type III - Sometimes burns, tans uniformly (Medium)' },
  { value: 'IV', label: 'Type IV - Burns minimally, tans easily (Olive)' },
  { value: 'V', label: 'Type V - Rarely burns, tans very easily (Brown)' },
  { value: 'VI', label: 'Type VI - Never burns, deeply pigmented (Dark brown/Black)' },
]

export default function HealthProfilePage() {
  const navigate = useNavigate()
  const toast = useToast()
  const [formData, setFormData] = useState({
    age: '',
    skin_type: '',
    family_history: '',
  })

  // Fetch existing profile
  const { data: profile, isLoading: loadingProfile } = useQuery({
    queryKey: ['healthProfile'],
    queryFn: healthProfileService.getProfile,
    retry: false,
  })

  // Load profile data when available
  useEffect(() => {
    if (profile) {
      setFormData({
        age: profile.age?.toString() || '',
        skin_type: profile.skin_type || '',
        family_history: profile.family_history || '',
      })
    }
  }, [profile])

  // Create or update mutation
  const saveMutation = useMutation({
    mutationFn: async (data: any) => {
      if (profile) {
        return healthProfileService.updateProfile(data)
      } else {
        return healthProfileService.createProfile(data)
      }
    },
    onSuccess: () => {
      toast.success('Health profile saved successfully!')
      setTimeout(() => navigate(ROUTES.PATIENT_DASHBOARD), 1500)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail?.message || error.message || 'Failed to save profile')
    },
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.age || !formData.skin_type) {
      toast.error('Please fill in all required fields')
      return
    }

    saveMutation.mutate({
      age: parseInt(formData.age),
      skin_type: formData.skin_type,
      family_history: formData.family_history || '',
    })
  }

  return (
    <div className="max-w-3xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate(ROUTES.PATIENT_DASHBOARD)}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft size={20} className="mr-2" />
          Back to Dashboard
        </button>
        <h1 className="text-3xl font-bold text-gray-900">Health Profile</h1>
        <p className="text-gray-600 mt-2">
          Help us provide better care by completing your health profile
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="card">
        {/* Age */}
        <div className="mb-6">
          <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
            <Calendar className="mr-2" size={18} />
            Age <span className="text-danger-600 ml-1">*</span>
          </label>
          <input
            type="number"
            min="1"
            max="120"
            value={formData.age}
            onChange={(e) => setFormData({ ...formData, age: e.target.value })}
            className="input"
            placeholder="Enter your age"
            required
          />
        </div>

        {/* Skin Type */}
        <div className="mb-6">
          <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
            <User className="mr-2" size={18} />
            Skin Type (Fitzpatrick Scale) <span className="text-danger-600 ml-1">*</span>
          </label>
          <select
            value={formData.skin_type}
            onChange={(e) => setFormData({ ...formData, skin_type: e.target.value })}
            className="input"
            required
          >
            <option value="">Select your skin type</option>
            {SKIN_TYPES.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
          <p className="text-sm text-gray-500 mt-2">
            The Fitzpatrick scale helps determine your skin's sensitivity to UV radiation
          </p>
        </div>

        {/* Family History */}
        <div className="mb-6">
          <label className="flex items-center text-sm font-medium text-gray-700 mb-2">
            <Heart className="mr-2" size={18} />
            Family History of Skin Conditions
          </label>
          <textarea
            value={formData.family_history}
            onChange={(e) => setFormData({ ...formData, family_history: e.target.value })}
            className="input"
            rows={4}
            placeholder="Please describe any family history of skin cancer, melanoma, or other skin conditions..."
          />
          <p className="text-sm text-gray-500 mt-2">
            Include information about immediate family members (parents, siblings, children)
          </p>
        </div>

        {/* Info Box */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-start">
            <AlertCircle className="text-blue-600 mr-3 mt-0.5" size={20} />
            <div className="text-sm text-blue-800">
              <p className="font-medium mb-1">Why we need this information</p>
              <p>
                Your health profile helps our AI provide more accurate risk assessments and helps
                doctors give you personalized care. All information is encrypted and kept confidential.
              </p>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={() => navigate(ROUTES.PATIENT_DASHBOARD)}
            className="btn btn-secondary"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={saveMutation.isPending || loadingProfile}
            className="btn btn-primary flex items-center"
          >
            <Save className="mr-2" size={18} />
            {saveMutation.isPending ? 'Saving...' : 'Save Profile'}
          </button>
        </div>
      </form>
    </div>
  )
}
