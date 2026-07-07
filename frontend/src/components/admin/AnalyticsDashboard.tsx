import { useState, useEffect } from 'react'
import { Users, FileText, Clock, TrendingUp, MapPin, Loader2 } from 'lucide-react'
import { adminService } from '@/services/admin'
import type { AnalyticsData } from '@/types/admin'
import { useToast } from '@/hooks/useToast'

export default function AnalyticsDashboard() {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)
  const { showToast } = useToast()

  useEffect(() => {
    loadAnalytics()
  }, [])

  const loadAnalytics = async () => {
    try {
      setLoading(true)
      const data = await adminService.getAnalytics()
      setAnalytics(data)
    } catch (error) {
      showToast('Failed to load analytics', 'error')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="animate-spin text-primary-600" size={32} />
      </div>
    )
  }

  if (!analytics) {
    return (
      <div className="card text-center py-12">
        <p className="text-gray-600">No analytics data available</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Analytics Dashboard</h2>

      {/* Key Metrics */}
      <div className="grid md:grid-cols-3 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Active Users (30 Days)</p>
              <p className="text-3xl font-bold text-primary-600">
                {analytics.dailyActiveUsers.toLocaleString()}
              </p>
            </div>
            <div className="p-3 bg-primary-50 rounded-lg">
              <Users className="text-primary-600" size={24} />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Total Screenings</p>
              <p className="text-3xl font-bold text-primary-600">
                {analytics.totalScreenings.toLocaleString()}
              </p>
            </div>
            <div className="p-3 bg-primary-50 rounded-lg">
              <FileText className="text-primary-600" size={24} />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Avg Processing Time</p>
              <p className="text-3xl font-bold text-primary-600">
                {analytics.averageProcessingTime.toFixed(2)}s
              </p>
            </div>
            <div className="p-3 bg-primary-50 rounded-lg">
              <Clock className="text-primary-600" size={24} />
            </div>
          </div>
        </div>
      </div>

      {/* Most Common Cancer Types */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="text-primary-600" size={20} />
          <h3 className="text-lg font-semibold">Most Common Cancer Types</h3>
        </div>

        {analytics.mostCommonCancerTypes.length === 0 ? (
          <p className="text-gray-600 text-sm">No data available</p>
        ) : (
          <div className="space-y-3">
            {analytics.mostCommonCancerTypes.map((item, index) => {
              const maxCount = Math.max(
                ...analytics.mostCommonCancerTypes.map(t => t.count)
              )
              const percentage = (item.count / maxCount) * 100

              return (
                <div key={index}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-700">
                      {item.type}
                    </span>
                    <span className="text-sm text-gray-600">{item.count}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full transition-all"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Geographic Distribution */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <MapPin className="text-primary-600" size={20} />
          <h3 className="text-lg font-semibold">Geographic Distribution</h3>
        </div>

        {analytics.geographicDistribution.length === 0 ? (
          <p className="text-gray-600 text-sm">No data available</p>
        ) : (
          <div className="space-y-3">
            {analytics.geographicDistribution.map((item, index) => {
              const maxCount = Math.max(
                ...analytics.geographicDistribution.map(g => g.count)
              )
              const percentage = (item.count / maxCount) * 100

              return (
                <div key={index}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-700">
                      {item.location}
                    </span>
                    <span className="text-sm text-gray-600">{item.count}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full transition-all"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
