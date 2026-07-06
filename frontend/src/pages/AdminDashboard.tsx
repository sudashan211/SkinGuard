import { useState } from 'react'
import DashboardLayout from '@/layouts/DashboardLayout'
import { useAuth } from '@/hooks/useAuth'
import { Users, FileText, BarChart, BookOpen, LogOut, UserCog, Activity, Shield } from 'lucide-react'
import AnalyticsDashboard from '@/components/admin/AnalyticsDashboard'
import DoctorVerification from '@/components/admin/DoctorVerification'
import ContentModeration from '@/components/admin/ContentModeration'
import SkinWikiEditor from '@/components/admin/SkinWikiEditor'
import UserManagement from '@/components/admin/UserManagement'
import SystemHealth from '@/components/admin/SystemHealth'
import AuditLogs from '@/components/admin/AuditLogs'

type TabType = 'analytics' | 'doctors' | 'moderation' | 'wiki' | 'users' | 'system' | 'audit'

export default function AdminDashboard() {
  const { logout } = useAuth()
  const [activeTab, setActiveTab] = useState<TabType>('analytics')

  const sidebar = (
    <nav className="p-4 space-y-2">
      <button
        onClick={() => setActiveTab('analytics')}
        className={`flex items-center w-full px-4 py-3 rounded-lg ${
          activeTab === 'analytics'
            ? 'text-gray-700 bg-primary-50'
            : 'text-gray-700 hover:bg-gray-50'
        }`}
      >
        <BarChart className="mr-3" size={20} />
        Analytics
      </button>
      <button
        onClick={() => setActiveTab('users')}
        className={`flex items-center w-full px-4 py-3 rounded-lg ${
          activeTab === 'users'
            ? 'text-gray-700 bg-primary-50'
            : 'text-gray-700 hover:bg-gray-50'
        }`}
      >
        <UserCog className="mr-3" size={20} />
        User Management
      </button>
      <button
        onClick={() => setActiveTab('doctors')}
        className={`flex items-center w-full px-4 py-3 rounded-lg ${
          activeTab === 'doctors'
            ? 'text-gray-700 bg-primary-50'
            : 'text-gray-700 hover:bg-gray-50'
        }`}
      >
        <Users className="mr-3" size={20} />
        Doctor Verification
      </button>
      <button
        onClick={() => setActiveTab('moderation')}
        className={`flex items-center w-full px-4 py-3 rounded-lg ${
          activeTab === 'moderation'
            ? 'text-gray-700 bg-primary-50'
            : 'text-gray-700 hover:bg-gray-50'
        }`}
      >
        <FileText className="mr-3" size={20} />
        Content Moderation
      </button>
      <button
        onClick={() => setActiveTab('system')}
        className={`flex items-center w-full px-4 py-3 rounded-lg ${
          activeTab === 'system'
            ? 'text-gray-700 bg-primary-50'
            : 'text-gray-700 hover:bg-gray-50'
        }`}
      >
        <Activity className="mr-3" size={20} />
        System Health
      </button>
      <button
        onClick={() => setActiveTab('audit')}
        className={`flex items-center w-full px-4 py-3 rounded-lg ${
          activeTab === 'audit'
            ? 'text-gray-700 bg-primary-50'
            : 'text-gray-700 hover:bg-gray-50'
        }`}
      >
        <Shield className="mr-3" size={20} />
        Audit Logs
      </button>
      <button
        onClick={() => setActiveTab('wiki')}
        className={`flex items-center w-full px-4 py-3 rounded-lg ${
          activeTab === 'wiki'
            ? 'text-gray-700 bg-primary-50'
            : 'text-gray-700 hover:bg-gray-50'
        }`}
      >
        <BookOpen className="mr-3" size={20} />
        Skin-Wiki Editor
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
        {activeTab === 'analytics' && <AnalyticsDashboard />}
        {activeTab === 'users' && <UserManagement />}
        {activeTab === 'doctors' && <DoctorVerification />}
        {activeTab === 'moderation' && <ContentModeration />}
        {activeTab === 'system' && <SystemHealth />}
        {activeTab === 'audit' && <AuditLogs />}
        {activeTab === 'wiki' && <SkinWikiEditor />}
      </div>
    </DashboardLayout>
  )
}
