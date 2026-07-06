export interface PendingDoctor {
  id: string
  userId: string
  fullName: string
  email: string
  licenseNo: string
  clinicName: string
  lat: number
  lng: number
  whatsappNo: string
  specialization?: string
  verified: boolean
  createdAt: string
}

export interface FlaggedReport {
  id: string
  patientId: string
  imageUrl: string
  nsfwScore: number
  nonSkinScore: number
  rejectionReason: string
  status: string
  createdAt: string
}

export interface AnalyticsData {
  dailyActiveUsers: number
  totalScreenings: number
  averageProcessingTime: number
  mostCommonCancerTypes: Array<{
    type: string
    count: number
  }>
  geographicDistribution: Array<{
    location: string
    count: number
  }>
}

export interface WikiArticle {
  id: string
  title: string
  content: string
  cancerType?: string
  version: number
  createdAt: string
  updatedAt: string
  author: string
}

export interface WikiVersion {
  version: number
  content: string
  updatedAt: string
  author: string
}
