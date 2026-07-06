import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { patientService } from '@/services/patient'
import { ROUTES } from '@/utils/constants'
import { Loader2, Shield, Heart } from 'lucide-react'

type SkinType = 'I' | 'II' | 'III' | 'IV' | 'V' | 'VI'

export default function HealthProfileSetupPage() {
  const navigate = useNavigate()
  const [age, setAge] = useState('')
  const [skinType, setSkinType] = useState<SkinType>('III')
  const [familyHistory, setFamilyHistory] = useState('')
  const [agreedToDisclaimer, setAgreedToDisclaimer] = useState(false)
  const [error, setError] = useState('')

  const createProfileMutation = useMutation({
    mutationFn: patientService.createProfile,
    onSuccess: () => {
      // Navigate to patient dashboard after successful profile creation
      navigate(ROUTES.PATIENT_DASHBOARD)
    },
    onError: (error: any) => {
      setError(error.message || 'Failed to create health profile')
    }
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    // Validate age
    const ageNum = parseInt(age)
    if (isNaN(ageNum) || ageNum < 1 || ageNum > 120) {
      setError('Please enter a valid age between 1 and 120')
      return
    }

    // Validate disclaimer agreement
    if (!agreedToDisclaimer) {
      setError('You must agree to the privacy disclaimer to continue')
      return
    }

    // Submit profile
    createProfileMutation.mutate({
      age: ageNum,
      skin_type: skinType,
      family_history: familyHistory || undefined
    })
  }

  const skinTypeDescriptions = {
    'I': 'Very fair, always burns, never tans',
    'II': 'Fair, usually burns, tans minimally',
    'III': 'Medium, sometimes burns, tans uniformly',
    'IV': 'Olive, rarely burns, tans easily',
    'V': 'Brown, very rarely burns, tans very easily',
    'VI': 'Dark brown/black, never burns, deeply pigmented'
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center p-4">
      <div className="card max-w-2xl w-full">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mb-4">
            <Heart className="text-primary-600" size={32} />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Complete Your Health Profile
          </h1>
          <p className="text-gray-600">
            Help us provide better care by sharing your health information
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Age */}
          <div>
            <label htmlFor="age" className="block text-sm font-medium text-gray-700 mb-2">
              Age <span className="text-danger-500">*</span>
            </label>
            <input
              id="age"
              type="number"
              value={age}
              onChange={(e) => setAge(e.target.value)}
              className="input"
              placeholder="Enter your age"
              required
              min="1"
              max="120"
              disabled={createProfileMutation.isPending}
            />
            <p className="text-xs text-gray-500 mt-1">
              Must be between 1 and 120 years
            </p>
          </div>

          {/* Skin Type */}
          <div>
            <label htmlFor="skinType" className="block text-sm font-medium text-gray-700 mb-2">
              Fitzpatrick Skin Type <span className="text-danger-500">*</span>
            </label>
            <select
              id="skinType"
              value={skinType}
              onChange={(e) => setSkinType(e.target.value as SkinType)}
              className="input"
              required
              disabled={createProfileMutation.isPending}
            >
              {Object.entries(skinTypeDescriptions).map(([type, description]) => (
                <option key={type} value={type}>
                  Type {type}: {description}
                </option>
              ))}
            </select>
            <p className="text-xs text-gray-500 mt-1">
              Select the skin type that best describes you
            </p>
          </div>

          {/* Family History */}
          <div>
            <label htmlFor="familyHistory" className="block text-sm font-medium text-gray-700 mb-2">
              Family History of Skin Conditions
            </label>
            <textarea
              id="familyHistory"
              value={familyHistory}
              onChange={(e) => setFamilyHistory(e.target.value)}
              className="input"
              placeholder="e.g., Mother had melanoma, father has psoriasis..."
              rows={4}
              disabled={createProfileMutation.isPending}
            />
            <p className="text-xs text-gray-500 mt-1">
              Optional: Include any relevant family medical history
            </p>
          </div>

          {/* Privacy Disclaimer */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start">
              <Shield className="text-blue-600 mt-1 mr-3 flex-shrink-0" size={20} />
              <div className="flex-1">
                <h3 className="text-sm font-semibold text-blue-900 mb-2">
                  Privacy & Data Protection
                </h3>
                <p className="text-sm text-blue-800 mb-3">
                  By creating your health profile, you acknowledge that:
                </p>
                <ul className="text-sm text-blue-800 space-y-1 mb-3 list-disc list-inside">
                  <li>Your personal health information will be securely stored and encrypted</li>
                  <li>This data will be used to provide personalized medical analysis and recommendations</li>
                  <li>Your information will only be shared with healthcare providers you choose to consult</li>
                  <li>You can update or delete your information at any time from your profile settings</li>
                  <li>We comply with all applicable data protection regulations (HIPAA, GDPR)</li>
                </ul>
                
                <label className="flex items-start cursor-pointer">
                  <input
                    type="checkbox"
                    checked={agreedToDisclaimer}
                    onChange={(e) => setAgreedToDisclaimer(e.target.checked)}
                    className="mt-1 mr-3 h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                    disabled={createProfileMutation.isPending}
                  />
                  <span className="text-sm text-blue-900 font-medium">
                    I understand and agree to the privacy terms. I consent to the secure storage and processing of my health information.
                  </span>
                </label>
              </div>
            </div>
          </div>

          {error && (
            <div className="p-3 bg-danger-50 border border-danger-200 rounded-lg">
              <p className="text-sm text-danger-600">{error}</p>
            </div>
          )}

          <button
            type="submit"
            className="btn btn-primary w-full flex items-center justify-center"
            disabled={createProfileMutation.isPending || !agreedToDisclaimer}
          >
            {createProfileMutation.isPending ? (
              <>
                <Loader2 className="animate-spin mr-2" size={20} />
                Creating Profile...
              </>
            ) : (
              <>
                <Heart className="mr-2" size={20} />
                Create Health Profile
              </>
            )}
          </button>

          <p className="text-xs text-center text-gray-500">
            All fields marked with <span className="text-danger-500">*</span> are required
          </p>
        </form>
      </div>
    </div>
  )
}
