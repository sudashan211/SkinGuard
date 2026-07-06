import { useState, useEffect } from 'react'
import { AlertTriangle, Image as ImageIcon, Loader2 } from 'lucide-react'
import { adminService } from '@/services/admin'
import type { FlaggedReport } from '@/types/admin'
import { useToast } from '@/hooks/useToast'

export default function ContentModeration() {
  const [reports, setReports] = useState<FlaggedReport[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedImage, setSelectedImage] = useState<string | null>(null)
  const { showToast } = useToast()

  useEffect(() => {
    loadFlaggedReports()
  }, [])

  const loadFlaggedReports = async () => {
    try {
      setLoading(true)
      const data = await adminService.getFlaggedReports()
      setReports(data)
    } catch (error) {
      showToast('Failed to load flagged reports', 'error')
    } finally {
      setLoading(false)
    }
  }

  const getRiskLevel = (nsfwScore: number, nonSkinScore: number) => {
    if (nsfwScore > 0.7 || nonSkinScore > 0.9) return 'high'
    if (nsfwScore > 0.5 || nonSkinScore > 0.85) return 'medium'
    return 'low'
  }

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'high':
        return 'text-danger-600 bg-danger-50'
      case 'medium':
        return 'text-warning-600 bg-warning-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="animate-spin text-primary-600" size={32} />
      </div>
    )
  }

  if (reports.length === 0) {
    return (
      <div className="card text-center py-12">
        <p className="text-gray-600">No flagged reports</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold mb-6">Content Moderation</h2>

      {reports.map(report => {
        const riskLevel = getRiskLevel(report.nsfwScore, report.nonSkinScore)
        return (
          <div key={report.id} className="card">
            <div className="flex flex-col md:flex-row gap-4">
              {/* Image Preview */}
              <div className="flex-shrink-0">
                <div
                  className="w-full md:w-48 h-48 bg-gray-100 rounded-lg overflow-hidden cursor-pointer hover:opacity-90 transition-opacity"
                  onClick={() => setSelectedImage(report.imageUrl)}
                >
                  <img
                    src={report.imageUrl}
                    alt="Flagged content"
                    className="w-full h-full object-cover"
                  />
                </div>
              </div>

              {/* Report Details */}
              <div className="flex-1 space-y-3">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                      <AlertTriangle className="text-warning-600" size={20} />
                      Flagged Report
                    </h3>
                    <p className="text-sm text-gray-600">
                      Report ID: {report.id.slice(0, 8)}...
                    </p>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-medium ${getRiskColor(
                      riskLevel
                    )}`}
                  >
                    {riskLevel.toUpperCase()} RISK
                  </span>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-gray-500 mb-1">NSFW Score</p>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-danger-600 h-2 rounded-full"
                          style={{ width: `${report.nsfwScore * 100}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium">
                        {(report.nsfwScore * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>

                  <div>
                    <p className="text-xs text-gray-500 mb-1">Non-Skin Score</p>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-warning-600 h-2 rounded-full"
                          style={{ width: `${report.nonSkinScore * 100}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium">
                        {(report.nonSkinScore * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>

                <div>
                  <p className="text-xs text-gray-500 mb-1">Rejection Reason</p>
                  <p className="text-sm font-medium text-gray-900">
                    {report.rejectionReason}
                  </p>
                </div>

                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>Status: {report.status}</span>
                  <span>
                    Flagged: {new Date(report.createdAt).toLocaleString()}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )
      })}

      {/* Image Modal */}
      {selectedImage && (
        <div
          className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedImage(null)}
        >
          <div className="max-w-4xl max-h-full">
            <img
              src={selectedImage}
              alt="Full size"
              className="max-w-full max-h-[90vh] object-contain"
            />
          </div>
        </div>
      )}
    </div>
  )
}
