/**
 * Self-Examination Guide Component
 * Requirements: 16.3, 16.4
 * 
 * Provides illustrated body map and step-by-step self-examination instructions
 */

import React, { useEffect, useState } from 'react';
import { educationService } from '../../services/education';
import { SelfExaminationGuide as GuideType, ExaminationStep, BodyMapRegion } from '../../types/education';

export const SelfExaminationGuide: React.FC = () => {
  const [guide, setGuide] = useState<GuideType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    loadGuide();
  }, []);

  const loadGuide = async () => {
    try {
      setLoading(true);
      const data = await educationService.getSelfExaminationGuide();
      setGuide(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load self-examination guide');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !guide) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <p className="text-red-800">{error || 'Guide not available'}</p>
        <button
          onClick={loadGuide}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">{guide.title}</h1>
        <p className="text-lg text-gray-600 max-w-3xl mx-auto">
          {guide.description}
        </p>
        <div className="mt-4 inline-flex items-center px-4 py-2 bg-blue-100 text-blue-800 rounded-full">
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
          <span className="font-semibold">Recommended Frequency: {guide.frequency}</span>
        </div>
      </div>

      {/* Educational Disclaimer */}
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
        <div className="flex items-start">
          <svg
            className="w-6 h-6 text-amber-600 mt-0.5 mr-3 flex-shrink-0"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
          <div>
            <h3 className="font-semibold text-amber-900 mb-1">Important Note</h3>
            <p className="text-sm text-amber-800">
              Self-examination is not a substitute for professional medical evaluation. If you notice
              any concerning changes, consult a dermatologist immediately.
            </p>
          </div>
        </div>
      </div>

      {/* Step-by-Step Guide */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Examination Steps</h2>

        {/* Step Navigation */}
        <div className="flex items-center justify-between mb-8 overflow-x-auto pb-4">
          {guide.steps.map((step, index) => (
            <button
              key={step.stepNumber}
              onClick={() => setActiveStep(index)}
              className={`flex flex-col items-center min-w-[80px] ${
                activeStep === index ? 'opacity-100' : 'opacity-50 hover:opacity-75'
              } transition-opacity`}
            >
              <div
                className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg mb-2 ${
                  activeStep === index
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-600'
                }`}
              >
                {step.stepNumber}
              </div>
              <span className="text-xs text-center text-gray-600">{step.title}</span>
            </button>
          ))}
        </div>

        {/* Active Step Content */}
        {guide.steps[activeStep] && (
          <div className="space-y-4">
            <div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">
                Step {guide.steps[activeStep].stepNumber}: {guide.steps[activeStep].title}
              </h3>
              <p className="text-gray-700">{guide.steps[activeStep].description}</p>
            </div>

            {/* Tips */}
            {guide.steps[activeStep].tips && guide.steps[activeStep].tips.length > 0 && (
              <div className="bg-blue-50 rounded-lg p-4">
                <h4 className="font-semibold text-blue-900 mb-2 flex items-center">
                  <svg
                    className="w-5 h-5 mr-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                    />
                  </svg>
                  Tips
                </h4>
                <ul className="space-y-1">
                  {guide.steps[activeStep].tips.map((tip, index) => (
                    <li key={index} className="text-sm text-blue-800 flex items-start">
                      <span className="mr-2">•</span>
                      <span>{tip}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Navigation Buttons */}
            <div className="flex justify-between pt-4">
              <button
                onClick={() => setActiveStep(Math.max(0, activeStep - 1))}
                disabled={activeStep === 0}
                className={`px-4 py-2 rounded-lg font-medium ${
                  activeStep === 0
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Previous
              </button>
              <button
                onClick={() => setActiveStep(Math.min(guide.steps.length - 1, activeStep + 1))}
                disabled={activeStep === guide.steps.length - 1}
                className={`px-4 py-2 rounded-lg font-medium ${
                  activeStep === guide.steps.length - 1
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Body Map */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Body Map Reference</h2>
        <p className="text-gray-600 mb-6">
          Different body areas are prone to different types of skin lesions. Pay special attention
          to these regions during your examination.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {guide.bodyMap.map((region) => (
            <div
              key={region.id}
              className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-md transition-all"
            >
              <h3 className="font-bold text-gray-900 mb-2">{region.name}</h3>
              <p className="text-sm text-gray-600 mb-3">{region.description}</p>
              <div>
                <p className="text-xs font-semibold text-gray-700 mb-1">Common Lesions:</p>
                <div className="flex flex-wrap gap-1">
                  {region.commonLesions.map((lesion, index) => (
                    <span
                      key={index}
                      className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded-full"
                    >
                      {lesion}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
