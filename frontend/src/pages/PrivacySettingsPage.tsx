import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { ArrowLeft, Lock, Shield, Download, Trash2, Key, Bell } from 'lucide-react'
import { useToast } from '@/hooks/useToast'
import { ROUTES } from '@/utils/constants'
import { securityService } from '@/services/security'

export default function PrivacySettingsPage() {
  const navigate = useNavigate()
  const toast = useToast()
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [showPasswordForm, setShowPasswordForm] = useState(false)
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  })

  // Password change mutation
  const passwordMutation = useMutation({
    mutationFn: (data: { current_password: string; new_password: string }) =>
      securityService.changePassword(data),
    onSuccess: () => {
      toast.success('Password changed successfully!')
      setShowPasswordForm(false)
      setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail?.message || error.message || 'Failed to change password')
    },
  })

  // Data export mutation
  const exportMutation = useMutation({
    mutationFn: securityService.requestDataExport,
    onSuccess: () => {
      toast.success('Your data export has been initiated. You will receive an email shortly.')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail?.message || error.message || 'Failed to export data')
    },
  })

  // Account deletion mutation
  const deleteMutation = useMutation({
    mutationFn: securityService.deleteAccount,
    onSuccess: () => {
      toast.success('Account deletion request submitted')
      setTimeout(() => navigate(ROUTES.HOME), 2000)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail?.message || error.message || 'Failed to delete account')
    },
  })

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      toast.error('New passwords do not match')
      return
    }

    if (passwordData.newPassword.length < 8) {
      toast.error('Password must be at least 8 characters')
      return
    }

    passwordMutation.mutate({
      current_password: passwordData.currentPassword,
      new_password: passwordData.newPassword,
    })
  }

  const handleDownloadData = async () => {
    exportMutation.mutate()
  }

  const handleDeleteAccount = async () => {
    deleteMutation.mutate()
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate(ROUTES.PATIENT_DASHBOARD)}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft size={20} className="mr-2" />
          Back to Dashboard
        </button>
        <h1 className="text-3xl font-bold text-gray-900">Privacy & Security</h1>
        <p className="text-gray-600 mt-2">
          Manage your privacy preferences and security settings
        </p>
      </div>

      <div className="space-y-6">
        {/* Password Section */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <Key className="text-primary-600 mr-3" size={24} />
              <div>
                <h3 className="text-lg font-semibold">Password</h3>
                <p className="text-sm text-gray-600">Change your account password</p>
              </div>
            </div>
            <button
              onClick={() => setShowPasswordForm(!showPasswordForm)}
              className="btn btn-secondary"
            >
              {showPasswordForm ? 'Cancel' : 'Change Password'}
            </button>
          </div>

          {showPasswordForm && (
            <form onSubmit={handleChangePassword} className="mt-4 space-y-4 border-t pt-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Current Password
                </label>
                <input
                  type="password"
                  value={passwordData.currentPassword}
                  onChange={(e) => setPasswordData({ ...passwordData, currentPassword: e.target.value })}
                  className="input"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  New Password
                </label>
                <input
                  type="password"
                  value={passwordData.newPassword}
                  onChange={(e) => setPasswordData({ ...passwordData, newPassword: e.target.value })}
                  className="input"
                  minLength={8}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Confirm New Password
                </label>
                <input
                  type="password"
                  value={passwordData.confirmPassword}
                  onChange={(e) => setPasswordData({ ...passwordData, confirmPassword: e.target.value })}
                  className="input"
                  required
                />
              </div>
              <button type="submit" className="btn btn-primary" disabled={passwordMutation.isPending}>
                {passwordMutation.isPending ? 'Updating...' : 'Update Password'}
              </button>
            </form>
          )}
        </div>

        {/* Encryption Status */}
        <div className="card">
          <div className="flex items-center">
            <Shield className="text-success-600 mr-3" size={24} />
            <div>
              <h3 className="text-lg font-semibold">Data Encryption</h3>
              <p className="text-sm text-gray-600">Your data is encrypted at rest and in transit</p>
              <div className="mt-2 flex items-center">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-success-100 text-success-800">
                  <Lock className="mr-1" size={12} />
                  Enabled
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Notification Preferences */}
        <div className="card">
          <div className="flex items-center mb-4">
            <Bell className="text-primary-600 mr-3" size={24} />
            <div>
              <h3 className="text-lg font-semibold">Notifications</h3>
              <p className="text-sm text-gray-600">Manage your notification preferences</p>
            </div>
          </div>
          <div className="space-y-3 border-t pt-4">
            <label className="flex items-center justify-between">
              <span className="text-sm text-gray-700">Email notifications for new reports</span>
              <input type="checkbox" className="toggle" defaultChecked />
            </label>
            <label className="flex items-center justify-between">
              <span className="text-sm text-gray-700">Appointment reminders</span>
              <input type="checkbox" className="toggle" defaultChecked />
            </label>
            <label className="flex items-center justify-between">
              <span className="text-sm text-gray-700">Educational content and tips</span>
              <input type="checkbox" className="toggle" />
            </label>
          </div>
        </div>

        {/* Data Export */}
        <div className="card">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Download className="text-primary-600 mr-3" size={24} />
              <div>
                <h3 className="text-lg font-semibold">Export Your Data</h3>
                <p className="text-sm text-gray-600">Download a copy of your personal data</p>
              </div>
            </div>
            <button onClick={handleDownloadData} className="btn btn-secondary" disabled={exportMutation.isPending}>
              {exportMutation.isPending ? 'Requesting...' : 'Request Export'}
            </button>
          </div>
        </div>

        {/* Delete Account */}
        <div className="card border-danger-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Trash2 className="text-danger-600 mr-3" size={24} />
              <div>
                <h3 className="text-lg font-semibold text-danger-900">Delete Account</h3>
                <p className="text-sm text-gray-600">Permanently delete your account and all data</p>
              </div>
            </div>
            <button
              onClick={() => setShowDeleteConfirm(true)}
              className="btn bg-danger-600 hover:bg-danger-700 text-white"
            >
              Delete Account
            </button>
          </div>

          {showDeleteConfirm && (
            <div className="mt-4 p-4 bg-danger-50 border border-danger-200 rounded-lg">
              <p className="text-sm text-danger-800 mb-4">
                <strong>Warning:</strong> This action cannot be undone. All your reports, appointments,
                and personal data will be permanently deleted.
              </p>
              <div className="flex space-x-3">
                <button
                  onClick={handleDeleteAccount}
                  className="btn bg-danger-600 hover:bg-danger-700 text-white"
                  disabled={deleteMutation.isPending}
                >
                  {deleteMutation.isPending ? 'Deleting...' : 'Yes, Delete My Account'}
                </button>
                <button
                  onClick={() => setShowDeleteConfirm(false)}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
