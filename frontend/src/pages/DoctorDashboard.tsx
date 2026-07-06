import { useState } from 'react'
import DashboardLayout from '@/layouts/DashboardLayout'
import { useAuth } from '@/hooks/useAuth'
import { FileText, Calendar, User, LogOut } from 'lucide-react'
import PendingReportsView from '@/components/doctor/PendingReportsView'
import AppointmentsView from '@/components/doctor/AppointmentsView'
import DoctorProfilePage from './DoctorProfilePage'

type ViewType = 'reports' | 'appointments' | 'profile'

export default function DoctorDashboard() {
  const { user, logout } = useAuth()
  const [currentView, setCurrentView] = useState<ViewType>('appointments')

  const sidebar = (
    <nav className="p-4 space-y-2">
      <button
        onClick={() => setCurrentView('appointments')}
        className={`flex items-center w-full px-4 py-3 rounded-lg transition-colors ${
          currentView === 'appointments'
            ? 'text-gray-700 bg-primary-50'
            : 'text-gray-700 hover:bg-gray-50'
        }`}
      >
        <Calendar className="mr-3" size={20} />
        Appointments
      </button>
      <button
        onClick={() => setCurrentView('reports')}
        className={`flex items-center w-full px-4 py-3 rounded-lg transition-colors ${
          currentView === 'reports'
            ? 'text-gray-700 bg-primary-50'
            : 'text-gray-700 hover:bg-gray-50'
        }`}
      >
        <FileText className="mr-3" size={20} />
        Pending Reports
      </button>
      <button
        onClick={() => setCurrentView('profile')}
        className={`flex items-center w-full px-4 py-3 rounded-lg transition-colors ${
          currentView === 'profile'
            ? 'text-gray-700 bg-primary-50'
            : 'text-gray-700 hover:bg-gray-50'
        }`}
      >
        <User className="mr-3" size={20} />
        Profile
      </button>
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
      <div>
        <h1 className="text-3xl font-bold mb-6">Hospital/Clinic Dashboard</h1>
        
        {/* Main Content Area */}
        {currentView === 'reports' && (
          <PendingReportsView />
        )}
        
        {currentView === 'appointments' && (
          <AppointmentsView />
        )}
        
        {currentView === 'profile' && (
          <DoctorProfilePage />
        )}
      </div>
    </DashboardLayout>
  )
}
