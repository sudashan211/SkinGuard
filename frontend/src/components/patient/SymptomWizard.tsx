import { useState } from 'react'
import { ChevronLeft, ChevronRight, Check } from 'lucide-react'
import { BODY_LOCATIONS, SENSATIONS, VISUAL_CHANGES } from '@/utils/constants'
import type { SymptomData } from '@/types/patient'

interface SymptomWizardProps {
  onComplete: (symptoms: SymptomData) => void
  onSkip?: () => void
}

export default function SymptomWizard({ onComplete, onSkip }: SymptomWizardProps) {
  const [step, setStep] = useState(1)
  const [symptoms, setSymptoms] = useState<SymptomData>({
    body_location: '',
    sensations: [],
    visual_changes: [],
  })

  const handleBodyLocationSelect = (location: string) => {
    setSymptoms({ ...symptoms, body_location: location })
  }

  const handleSensationToggle = (sensation: string) => {
    const newSensations = symptoms.sensations.includes(sensation)
      ? symptoms.sensations.filter(s => s !== sensation)
      : [...symptoms.sensations, sensation]
    setSymptoms({ ...symptoms, sensations: newSensations })
  }

  const handleVisualChangeToggle = (change: string) => {
    const newChanges = symptoms.visual_changes.includes(change)
      ? symptoms.visual_changes.filter(c => c !== change)
      : [...symptoms.visual_changes, change]
    setSymptoms({ ...symptoms, visual_changes: newChanges })
  }

  const handleNext = () => {
    if (step < 3) {
      setStep(step + 1)
    } else {
      onComplete(symptoms)
    }
  }

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1)
    }
  }

  const canProceed = () => {
    switch (step) {
      case 1:
        return symptoms.body_location !== ''
      case 2:
        return true // Sensations are optional
      case 3:
        return true // Visual changes are optional
      default:
        return false
    }
  }

  return (
    <div className="space-y-6">
      {/* Progress Bar */}
      <div className="flex items-center justify-between mb-6">
        {[1, 2, 3].map((s) => (
          <div key={s} className="flex items-center flex-1">
            <div
              className={`
                w-10 h-10 rounded-full flex items-center justify-center font-semibold
                ${s < step ? 'bg-primary-600 text-white' : ''}
                ${s === step ? 'bg-primary-600 text-white' : ''}
                ${s > step ? 'bg-gray-200 text-gray-500' : ''}
              `}
            >
              {s < step ? <Check size={20} /> : s}
            </div>
            {s < 3 && (
              <div
                className={`
                  flex-1 h-1 mx-2
                  ${s < step ? 'bg-primary-600' : 'bg-gray-200'}
                `}
              />
            )}
          </div>
        ))}
      </div>

      {/* Step Content */}
      <div className="min-h-[300px]">
        {/* Step 1: Body Location */}
        {step === 1 && (
          <div>
            <h3 className="text-xl font-semibold mb-2">Where is the lesion located?</h3>
            <p className="text-gray-600 mb-6">Select the body part where you noticed the skin change</p>
            
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {BODY_LOCATIONS.map((location) => (
                <button
                  key={location}
                  onClick={() => handleBodyLocationSelect(location)}
                  className={`
                    p-4 rounded-lg border-2 text-left transition-all
                    ${symptoms.body_location === location
                      ? 'border-primary-600 bg-primary-50 text-primary-900'
                      : 'border-gray-200 hover:border-primary-300'
                    }
                  `}
                >
                  <span className="font-medium">{location}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Step 2: Sensations */}
        {step === 2 && (
          <div>
            <h3 className="text-xl font-semibold mb-2">What sensations do you feel?</h3>
            <p className="text-gray-600 mb-6">Select all that apply (optional)</p>
            
            <div className="space-y-3">
              {SENSATIONS.map((sensation) => (
                <label
                  key={sensation}
                  className="flex items-center p-4 rounded-lg border-2 cursor-pointer transition-all hover:border-primary-300"
                >
                  <input
                    type="checkbox"
                    checked={symptoms.sensations.includes(sensation)}
                    onChange={() => handleSensationToggle(sensation)}
                    className="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
                  />
                  <span className="ml-3 font-medium">{sensation}</span>
                </label>
              ))}
            </div>

            <button
              onClick={() => setSymptoms({ ...symptoms, sensations: [] })}
              className="mt-4 text-sm text-gray-600 hover:text-gray-900"
            >
              Clear all
            </button>
          </div>
        )}

        {/* Step 3: Visual Changes */}
        {step === 3 && (
          <div>
            <h3 className="text-xl font-semibold mb-2">What visual changes have you noticed?</h3>
            <p className="text-gray-600 mb-6">Select all that apply (optional)</p>
            
            <div className="space-y-3">
              {VISUAL_CHANGES.map((change) => (
                <label
                  key={change}
                  className="flex items-center p-4 rounded-lg border-2 cursor-pointer transition-all hover:border-primary-300"
                >
                  <input
                    type="checkbox"
                    checked={symptoms.visual_changes.includes(change)}
                    onChange={() => handleVisualChangeToggle(change)}
                    className="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
                  />
                  <span className="ml-3 font-medium">{change}</span>
                </label>
              ))}
            </div>

            <button
              onClick={() => setSymptoms({ ...symptoms, visual_changes: [] })}
              className="mt-4 text-sm text-gray-600 hover:text-gray-900"
            >
              Clear all
            </button>
          </div>
        )}
      </div>

      {/* Navigation Buttons */}
      <div className="flex items-center justify-between pt-6 border-t">
        <div>
          {step > 1 && (
            <button
              onClick={handleBack}
              className="btn btn-secondary flex items-center"
            >
              <ChevronLeft size={20} className="mr-1" />
              Back
            </button>
          )}
        </div>

        <div className="flex items-center space-x-3">
          {onSkip && step === 1 && (
            <button
              onClick={onSkip}
              className="text-gray-600 hover:text-gray-900"
            >
              Skip symptoms
            </button>
          )}
          
          <button
            onClick={handleNext}
            disabled={!canProceed()}
            className="btn btn-primary flex items-center"
          >
            {step === 3 ? (
              <>
                Complete
                <Check size={20} className="ml-2" />
              </>
            ) : (
              <>
                Next
                <ChevronRight size={20} className="ml-2" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
