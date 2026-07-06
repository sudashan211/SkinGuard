import { useState } from 'react'
import { AlertTriangle, Info, MapPin, BookOpen } from 'lucide-react'
import { Link } from 'react-router-dom'
import { CANCER_TYPES } from '@/utils/constants'
import { getRiskLevelColor } from '@/utils/helpers'
import type { AnalysisResult, Hotspot } from '@/types/patient'
import { TouchImageViewer } from '@/components/common/TouchImageViewer'

interface ResultsDisplayProps {
  result: AnalysisResult
  imageUrl: string
  onFindDoctor?: () => void
}

export default function ResultsDisplay({ result, imageUrl, onFindDoctor }: ResultsDisplayProps) {
  const [showHotspots, setShowHotspots] = useState(true)

  // Get top prediction
  const predictions = Object.entries(result.predictions)
    .map(([type, probability]) => ({
      type: type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      rawType: type, // Keep original type for linking
      probability: probability * 100,
    }))
    .sort((a, b) => b.probability - a.probability)

  const topPrediction = predictions[0]
  const isHighRisk = result.risk_level === 'high' || result.risk_level === 'urgent'

  // Helper function to convert cancer type to slug
  const getArticleSlug = (cancerType: string): string => {
    return cancerType.replace(/_/g, '-')
  }

  return (
    <div className="space-y-6">
      {/* Risk Level Alert */}
      {isHighRisk && (
        <div className="p-4 bg-danger-50 border-2 border-danger-300 rounded-lg">
          <div className="flex items-start">
            <AlertTriangle className="text-danger-600 mt-1 mr-3 flex-shrink-0" size={24} />
            <div>
              <h3 className="text-lg font-semibold text-danger-900 mb-1">
                Urgent: High Risk Detected
              </h3>
              <p className="text-sm text-danger-800 mb-3">
                Our AI has detected a high-risk lesion. We strongly recommend consulting with a dermatologist immediately.
              </p>
              {onFindDoctor && (
                <button
                  onClick={onFindDoctor}
                  className="btn btn-danger flex items-center"
                >
                  <MapPin size={18} className="mr-2" />
                  Find Nearby Doctors
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Image with Hotspots */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Analyzed Image</h3>
          {result.hotspots && result.hotspots.length > 0 && (
            <label className="flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={showHotspots}
                onChange={(e) => setShowHotspots(e.target.checked)}
                className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500 mr-2"
              />
              <span className="text-sm text-gray-700">Show hotspots</span>
            </label>
          )}
        </div>

        <div className="relative rounded-lg overflow-hidden bg-gray-100">
          <TouchImageViewer
            src={imageUrl}
            alt="Analyzed skin lesion"
            showControls={true}
          />
          
          {/* Hotspot Overlays */}
          {showHotspots && result.hotspots && result.hotspots.map((hotspot, index) => (
            <div
              key={index}
              className="absolute border-2 border-danger-500 bg-danger-500 bg-opacity-20 pointer-events-none"
              style={{
                left: `${hotspot.x * 100}%`,
                top: `${hotspot.y * 100}%`,
                width: `${hotspot.width * 100}%`,
                height: `${hotspot.height * 100}%`,
              }}
            >
              <div className="absolute -top-6 left-0 bg-danger-500 text-white text-xs px-2 py-1 rounded">
                {Math.round(hotspot.confidence * 100)}%
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Risk Level */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Risk Assessment</h3>
        <div className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium ${getRiskLevelColor(result.risk_level)}`}>
          Risk Level: {result.risk_level.toUpperCase()}
        </div>
      </div>

      {/* Predictions */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">AI Analysis Results</h3>
        
        <div className="space-y-4">
          {predictions.map((pred, index) => (
            <div key={index}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">
                  {pred.type}
                </span>
                <span className="text-sm font-semibold text-gray-900">
                  {pred.probability.toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all ${
                    index === 0 ? 'bg-primary-600' : 'bg-gray-400'
                  }`}
                  style={{ width: `${pred.probability}%` }}
                />
              </div>
            </div>
          ))}
        </div>

        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-700">
            <strong>Top Prediction:</strong> {topPrediction.type} ({topPrediction.probability.toFixed(1)}% confidence)
          </p>
        </div>
      </div>

      {/* Contextual Educational Links - Property 48 */}
      <div className="card bg-blue-50 border-blue-200">
        <div className="flex items-start">
          <BookOpen className="text-blue-600 mt-1 mr-3 flex-shrink-0" size={20} />
          <div className="flex-1">
            <h4 className="text-sm font-semibold text-blue-900 mb-2">
              Learn More About {topPrediction.type}
            </h4>
            <p className="text-sm text-blue-800 mb-3">
              Read detailed information about this condition, including risk factors, symptoms, and treatment options.
            </p>
            <Link
              to={`/skin-wiki/${getArticleSlug(topPrediction.rawType)}`}
              className="inline-flex items-center text-sm font-medium text-blue-600 hover:text-blue-700"
            >
              <BookOpen size={16} className="mr-2" />
              View Educational Article
              <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </Link>
          </div>
        </div>
      </div>

      {/* Medical Disclaimer */}
      <div className="card bg-primary-50 border-primary-200">
        <div className="flex items-start">
          <Info className="text-primary-600 mt-1 mr-3 flex-shrink-0" size={20} />
          <div>
            <h4 className="text-sm font-semibold text-primary-900 mb-2">
              Medical Disclaimer
            </h4>
            <p className="text-sm text-primary-800">
              This is a 94% probability estimate based on AI analysis. This tool is not a substitute for professional medical advice, diagnosis, or treatment. 
              Please consult verified doctors for clinical biopsy and proper diagnosis.
            </p>
          </div>
        </div>
      </div>

      {/* Call to Action */}
      {onFindDoctor && (
        <div className="card bg-gradient-to-r from-primary-600 to-primary-700 text-white">
          <h3 className="text-lg font-semibold mb-2">Next Steps</h3>
          <p className="mb-4 text-primary-50">
            Connect with verified dermatologists in your area for professional consultation.
          </p>
          <button
            onClick={onFindDoctor}
            className="btn bg-white text-primary-600 hover:bg-gray-100 flex items-center"
          >
            <MapPin size={18} className="mr-2" />
            Find Hospitals Near You
          </button>
        </div>
      )}
    </div>
  )
}
