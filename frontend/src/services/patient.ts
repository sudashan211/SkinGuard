import api from './api'
import type { PatientProfile, MedicalReport, AnalysisResult, ReportComparison } from '@/types/patient'

export const patientService = {
  // Profile management
  async getProfile(): Promise<PatientProfile> {
    const response = await api.get('/api/patient/profile')
    return response.data
  },

  async createProfile(data: Partial<PatientProfile>): Promise<PatientProfile> {
    const response = await api.post('/api/patient/profile', data)
    return response.data
  },

  async updateProfile(data: Partial<PatientProfile>): Promise<PatientProfile> {
    const response = await api.put('/api/patient/profile', data)
    return response.data
  },

  // Image analysis
  async analyzeSkin(formData: FormData): Promise<AnalysisResult> {
    const response = await api.post('/api/analyze-skin', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 60000, // 60 seconds for AI processing
    })
    
    // Transform backend response to match frontend expectations
    const backendData = response.data
    
    // Convert predictions array to object format
    const predictionsObj: any = {}
    if (backendData.ai_prediction?.predictions && Array.isArray(backendData.ai_prediction.predictions)) {
      backendData.ai_prediction.predictions.forEach((pred: any) => {
        // Handle both formats: {cancer_type: "X", probability: Y} or {type: "X", probability: Y}
        const cancerType = pred.cancer_type || pred.type
        if (cancerType) {
          // Convert cancer type to snake_case key
          const key = cancerType.toLowerCase().replace(/\s+/g, '_')
          predictionsObj[key] = pred.probability
        }
      })
    }
    
    return {
      report_id: backendData.id,
      predictions: predictionsObj,
      hotspots: backendData.ai_prediction?.hotspots || [],
      risk_level: backendData.risk_level,
      processing_time: backendData.ai_prediction?.processing_time || 0,
      message: backendData.ai_prediction?.disclaimer || 'Analysis complete'
    }
  },

  // Reports
  async getReports(): Promise<MedicalReport[]> {
    const response = await api.get('/api/reports')
    return response.data
  },

  async getReport(reportId: string): Promise<MedicalReport> {
    const response = await api.get(`/api/reports/${reportId}`)
    return response.data
  },

  async compareReports(reportId1: string, reportId2: string): Promise<ReportComparison> {
    const response = await api.post(`/api/reports/${reportId1}/compare/${reportId2}`)
    return response.data
  },
}
