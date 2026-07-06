import { Link } from 'react-router-dom'
import { ROUTES } from '@/utils/constants'
import { ArrowRight, Shield, MapPin, FileText } from 'lucide-react'

export default function LandingPage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <div className="bg-gradient-to-br from-primary-600 to-primary-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              SkinGuard
            </h1>
            <p className="text-xl md:text-2xl mb-8 text-primary-100">
              AI-Powered Skin Cancer Screening Platform
            </p>
            <p className="text-lg mb-12 max-w-2xl mx-auto text-primary-50">
              Get instant AI analysis of skin lesions, connect with verified dermatologists,
              and track your skin health history - all in one secure platform.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to={ROUTES.SIGNUP}
                className="btn btn-primary bg-white text-primary-600 hover:bg-gray-100 px-8 py-3 text-lg"
              >
                Get Started
                <ArrowRight className="inline ml-2" size={20} />
              </Link>
              <Link
                to={ROUTES.LOGIN}
                className="btn bg-primary-700 text-white hover:bg-primary-600 px-8 py-3 text-lg"
              >
                Sign In
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-12">
            How SkinGuard Works
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="text-center p-6">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Shield className="text-primary-600" size={32} />
              </div>
              <h3 className="text-xl font-semibold mb-3">AI Screening</h3>
              <p className="text-gray-600">
                Upload a photo and get instant AI analysis with 94% accuracy.
                Our advanced models detect 7 types of skin conditions.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="text-center p-6">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <MapPin className="text-primary-600" size={32} />
              </div>
              <h3 className="text-xl font-semibold mb-3">Find Hospitals</h3>
              <p className="text-gray-600">
                Locate hospitals and dermatology clinics near you. Book appointments
                and connect via WhatsApp or video consultation.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="text-center p-6">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <FileText className="text-primary-600" size={32} />
              </div>
              <h3 className="text-xl font-semibold mb-3">Secure History</h3>
              <p className="text-gray-600">
                Track your skin health over time. Compare reports and
                receive follow-up reminders every 6 months.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-gray-50 py-16">
        <div className="max-w-4xl mx-auto text-center px-4">
          <h2 className="text-3xl font-bold mb-4">
            Ready to Take Control of Your Skin Health?
          </h2>
          <p className="text-lg text-gray-600 mb-8">
            Join thousands of users who trust SkinGuard for early detection and peace of mind.
          </p>
          <Link
            to={ROUTES.SIGNUP}
            className="btn btn-primary px-8 py-3 text-lg inline-flex items-center"
          >
            Create Free Account
            <ArrowRight className="ml-2" size={20} />
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-300 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-sm">
            © 2026 SkinGuard. All rights reserved.
          </p>
          <p className="text-xs mt-2 text-gray-400">
            Medical Disclaimer: This platform provides AI-assisted screening only.
            Always consult with qualified healthcare professionals for diagnosis and treatment.
          </p>
        </div>
      </footer>
    </div>
  )
}
