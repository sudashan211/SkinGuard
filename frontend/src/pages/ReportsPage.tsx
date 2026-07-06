import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Loader2 } from 'lucide-react'
import ReportHistory from '@/components/patient/ReportHistory'
import ComparisonView from '@/components/patient/ComparisonView'
import { patientService } from '@/services/patient'
import { useToast } from '@/hooks/useToast'
import { ROUTES } from '@/utils/constants'
import type { ReportComparison } from '@/types/patient'

export default function ReportsPage() {
  const navigate = useNavigate()
  const toast = useToast()
  const [comparison, setComparison] = useState<ReportComparison | null>(null)
  const [isComparing, setIsComparing] = useState(false)

  // Fetch reports
  const { data: reports, isLoading, error } = useQuery({
    queryKey: ['reports'],
    queryFn: () => patientService.getReports(),
  })

  const handleViewReport = (reportId: string) => {
    navigate(`${ROUTES.PATIENT_REPORTS}/${reportId}`)
  }

  const handleCompareReports = async (reportId1: string, reportId2: string) => {
    setIsComparing(true)
    try {
      const comparisonData = await patientService.compareReports(reportId1, reportId2)
      setComparison(comparisonData)
    } catch (error: any) {
      toast.error(error.message || 'Failed to compare reports')
    } finally {
      setIsComparing(false)
    }
  }

  const handleCloseComparison = () => {
    setComparison(null)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Loader2 className="animate-spin mx-auto mb-4 text-primary-600" size={48} />
          <p className="text-gray-600">Loading your reports...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card text-center py-12">
        <p className="text-danger-600 mb-4">Failed to load reports</p>
        <button
          onClick={() => window.location.reload()}
          className="btn btn-primary"
        >
          Try Again
        </button>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate(ROUTES.PATIENT_DASHBOARD)}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft size={20} className="mr-2" />
          Back to Dashboard
        </button>
        
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">My Reports</h1>
            <p className="text-gray-600">
              View and compare your skin screening history
            </p>
          </div>
          <button
            onClick={() => navigate(ROUTES.PATIENT_UPLOAD)}
            className="btn btn-primary"
          >
            New Screening
          </button>
        </div>
      </div>

      {/* Content */}
      {comparison ? (
        <ComparisonView
          comparison={comparison}
          onClose={handleCloseComparison}
        />
      ) : (
        <ReportHistory
          reports={reports || []}
          onViewReport={handleViewReport}
          onCompareReports={handleCompareReports}
        />
      )}

      {/* Comparing Loader */}
      {isComparing && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 text-center">
            <Loader2 className="animate-spin mx-auto mb-4 text-primary-600" size={48} />
            <p className="text-lg font-medium">Comparing reports...</p>
          </div>
        </div>
      )}
    </div>
  )
}
