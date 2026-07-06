import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { ArrowLeft } from 'lucide-react'
import DiagnosticUploader from '@/components/patient/DiagnosticUploader'
import SymptomWizard from '@/components/patient/SymptomWizard'
import ResultsDisplay from '@/components/patient/ResultsDisplay'
import LoadingSpinner from '@/components/common/LoadingSpinner'
import { UploadProgress } from '@/components/common/ProgressIndicator'
import { patientService } from '@/services/patient'
import { useToast } from '@/hooks/useToast'
import { withRetry, handleMutationError } from '@/utils/errorHandling'
import { ROUTES } from '@/utils/constants'
import type { SymptomData, AnalysisResult } from '@/types/patient'

export default function UploadPage() {
  const navigate = useNavigate()
  const toast = useToast()
  const [step, setStep] = useState<'upload' | 'symptoms' | 'results'>('upload')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [symptoms, setSymptoms] = useState<SymptomData | null>(null)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadStatus, setUploadStatus] = useState<'uploading' | 'processing' | 'complete' | 'error'>('uploading')
  const [retryCount, setRetryCount] = useState(0)

  // Analysis mutation with retry logic
  const analyzeMutation = useMutation({
    mutationFn: async (formData: FormData) => {
      setUploadStatus('uploading')
      setUploadProgress(0)
      
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + 10
        })
      }, 200)
      
      try {
        // Use retry logic for transient failures
        const data = await withRetry(
          () => patientService.analyzeSkin(formData),
          {
            maxRetries: 3,
            retryDelay: 1000,
            onRetry: (attempt) => {
              setRetryCount(attempt)
              toast.info(`Retrying... (Attempt ${attempt} of 3)`)
            }
          }
        )
        
        clearInterval(progressInterval)
        setUploadProgress(100)
        setUploadStatus('complete')
        
        return data
      } catch (error) {
        clearInterval(progressInterval)
        setUploadStatus('error')
        throw error
      }
    },
    onSuccess: (data) => {
      setResult(data)
      setStep('results')
      toast.success('Analysis complete!')
      setRetryCount(0)
    },
    onError: (error: any) => {
      const message = handleMutationError(error, toast)
      console.error('Analysis error:', message)
    },
  })

  const handleImageSelect = (file: File) => {
    setSelectedFile(file)
    
    // Create preview
    const reader = new FileReader()
    reader.onloadend = () => {
      setImagePreview(reader.result as string)
    }
    reader.readAsDataURL(file)
    
    // Move to symptoms step
    setStep('symptoms')
  }

  const handleSymptomsComplete = (symptomData: SymptomData) => {
    setSymptoms(symptomData)
    submitAnalysis(symptomData)
  }

  const handleSkipSymptoms = () => {
    submitAnalysis(null)
  }

  const submitAnalysis = (symptomData: SymptomData | null) => {
    if (!selectedFile) return

    const formData = new FormData()
    formData.append('image', selectedFile)
    
    if (symptomData) {
      formData.append('body_location', symptomData.body_location)
      formData.append('sensations', JSON.stringify(symptomData.sensations))
      formData.append('visual_changes', JSON.stringify(symptomData.visual_changes))
    }

    analyzeMutation.mutate(formData)
  }

  const handleFindDoctor = () => {
    navigate(ROUTES.PATIENT_DOCTORS)
  }

  const handleStartOver = () => {
    setStep('upload')
    setSelectedFile(null)
    setImagePreview(null)
    setSymptoms(null)
    setResult(null)
    setUploadProgress(0)
    setUploadStatus('uploading')
    setRetryCount(0)
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => step === 'upload' ? navigate(ROUTES.PATIENT_DASHBOARD) : handleStartOver()}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft size={20} className="mr-2" />
          {step === 'upload' ? 'Back to Dashboard' : 'Start Over'}
        </button>
        
        <h1 className="text-3xl font-bold mb-2">
          {step === 'upload' && 'Upload Skin Image'}
          {step === 'symptoms' && 'Describe Your Symptoms'}
          {step === 'results' && 'Analysis Results'}
        </h1>
        <p className="text-gray-600">
          {step === 'upload' && 'Upload a clear photo of your skin lesion for AI analysis'}
          {step === 'symptoms' && 'Help us understand your condition better (optional)'}
          {step === 'results' && 'Review your AI-powered skin analysis'}
        </p>
      </div>

      {/* Content */}
      <div className="card">
        {step === 'upload' && (
          <DiagnosticUploader
            onImageSelect={handleImageSelect}
            isLoading={false}
          />
        )}

        {step === 'symptoms' && (
          <SymptomWizard
            onComplete={handleSymptomsComplete}
            onSkip={handleSkipSymptoms}
          />
        )}

        {step === 'results' && result && imagePreview && (
          <ResultsDisplay
            result={result}
            imageUrl={imagePreview}
            onFindDoctor={handleFindDoctor}
          />
        )}

        {/* Loading State with Progress */}
        {analyzeMutation.isPending && selectedFile && (
          <div className="py-12">
            <UploadProgress
              fileName={selectedFile.name}
              progress={uploadProgress}
              status={uploadStatus}
            />
            
            <div className="mt-8 text-center">
              <LoadingSpinner size="lg" />
              <h3 className="text-lg font-semibold mt-4 mb-2">
                {uploadStatus === 'uploading' && 'Uploading Image...'}
                {uploadStatus === 'processing' && 'Analyzing Your Image...'}
                {uploadStatus === 'complete' && 'Analysis Complete!'}
              </h3>
              <p className="text-gray-600">
                {uploadStatus === 'uploading' && 'Securely uploading your image to our servers'}
                {uploadStatus === 'processing' && 'Our AI is processing your image. This may take up to 30 seconds...'}
                {uploadStatus === 'complete' && 'Preparing your results...'}
              </p>
              
              {retryCount > 0 && (
                <p className="text-yellow-600 mt-2 text-sm">
                  Retrying... (Attempt {retryCount} of 3)
                </p>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Results Actions */}
      {step === 'results' && (
        <div className="mt-6 flex items-center justify-between">
          <button
            onClick={handleStartOver}
            className="btn btn-secondary"
          >
            Analyze Another Image
          </button>
          <button
            onClick={() => navigate(ROUTES.PATIENT_REPORTS)}
            className="btn btn-primary"
          >
            View All Reports
          </button>
        </div>
      )}
    </div>
  )
}
