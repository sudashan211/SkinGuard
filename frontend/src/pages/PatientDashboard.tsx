import { Routes, Route, Link, useLocation } from 'react-router-dom'
import DashboardLayout from '@/layouts/DashboardLayout'
import { useAuth } from '@/hooks/useAuth'
import { Upload, FileText, MapPin, Calendar, LogOut, User, Settings } from 'lucide-react'
import UploadPage from './UploadPage'
import ReportsPage from './ReportsPage'
import ReportDetailPage from './ReportDetailPage'
import DoctorLocatorPage from './DoctorLocatorPage'
import HealthProfilePage from './HealthProfilePage'
import AppointmentsPage from './AppointmentsPage'
import PrivacySettingsPage from './PrivacySettingsPage'

function PatientHome() {
  const { user } = useAuth()

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Welcome, {user?.email}</h1>
      
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Link to="/patient/upload" className="card hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Upload Image</h3>
            <Upload className="text-primary-600" size={24} />
          </div>
          <p className="text-gray-600 mb-4">
            Get instant AI analysis of your skin lesion
          </p>
          <button className="btn btn-primary w-full">
            Start Screening
          </button>
        </Link>

        <Link to="/patient/reports" className="card hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">My Reports</h3>
            <FileText className="text-primary-600" size={24} />
          </div>
          <p className="text-gray-600 mb-4">
            View your screening history and results
          </p>
          <button className="btn btn-secondary w-full">
            View Reports
          </button>
        </Link>

        <Link to="/patient/doctors" className="card hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Find Hospitals</h3>
            <MapPin className="text-primary-600" size={24} />
          </div>
          <p className="text-gray-600 mb-4">
            Connect with hospitals and dermatology clinics
          </p>
          <button className="btn btn-secondary w-full">
            Find Hospitals
          </button>
        </Link>
      </div>

      <div className="mt-8 card bg-primary-50 border-primary-200">
        <h3 className="text-lg font-semibold mb-2">Getting Started</h3>
        <p className="text-gray-700">
          Welcome to SkinGuard! Upload a photo of your skin lesion to get started with AI-powered screening.
          Our system will analyze the image and provide you with detailed results.
        </p>
      </div>
    </div>
  )
}

export default function PatientDashboard() {
  const { logout } = useAuth()
  const location = useLocation()

  const isActive = (path: string) => location.pathname === path

  const sidebar = (
    <nav className="p-4 space-y-2">
      <Link
        to="/patient"
        className={`flex items-center px-4 py-3 rounded-lg ${
          isActive('/patient') ? 'text-gray-700 bg-primary-50' : 'text-gray-700 hover:bg-gray-50'
        }`}
      >
        <Upload className="mr-3" size={20} />
        Upload Image
      </Link>
      <Link
        to="/patient/reports"
        className={`flex items-center px-4 py-3 rounded-lg ${
          isActive('/patient/reports') ? 'text-gray-700 bg-primary-50' : 'text-gray-700 hover:bg-gray-50'
        }`}
      >
        <FileText className="mr-3" size={20} />
        My Reports
      </Link>
      <Link
        to="/patient/doctors"
        className={`flex items-center px-4 py-3 rounded-lg ${
          isActive('/patient/doctors') ? 'text-gray-700 bg-primary-50' : 'text-gray-700 hover:bg-gray-50'
        }`}
      >
        <MapPin className="mr-3" size={20} />
        Find Hospitals
      </Link>
      <Link
        to="/patient/appointments"
        className={`flex items-center px-4 py-3 rounded-lg ${
          isActive('/patient/appointments') ? 'text-gray-700 bg-primary-50' : 'text-gray-700 hover:bg-gray-50'
        }`}
      >
        <Calendar className="mr-3" size={20} />
        Appointments
      </Link>
      <Link
        to="/patient/profile"
        className={`flex items-center px-4 py-3 rounded-lg ${
          isActive('/patient/profile') ? 'text-gray-700 bg-primary-50' : 'text-gray-700 hover:bg-gray-50'
        }`}
      >
        <User className="mr-3" size={20} />
        Health Profile
      </Link>
      <Link
        to="/patient/settings"
        className={`flex items-center px-4 py-3 rounded-lg ${
          isActive('/patient/settings') ? 'text-gray-700 bg-primary-50' : 'text-gray-700 hover:bg-gray-50'
        }`}
      >
        <Settings className="mr-3" size={20} />
        Privacy & Security
      </Link>
      <button
        onClick={() => logout()}
        className="flex items-center w-full px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-lg mt-8"
      >
        <LogOut className="mr-3" size={20} />
        Logout
      </button>
    </nav>
  )

  return (
    <DashboardLayout sidebar={sidebar}>
      <Routes>
        <Route index element={<PatientHome />} />
        <Route path="upload" element={<UploadPage />} />
        <Route path="reports" element={<ReportsPage />} />
        <Route path="reports/:reportId" element={<ReportDetailPage />} />
        <Route path="doctors" element={<DoctorLocatorPage />} />
        <Route path="appointments" element={<AppointmentsPage />} />
        <Route path="profile" element={<HealthProfilePage />} />
        <Route path="settings" element={<PrivacySettingsPage />} />
      </Routes>
    </DashboardLayout>
  )
}
