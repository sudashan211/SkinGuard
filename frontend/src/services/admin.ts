import api from './api'
import type { PendingDoctor, FlaggedReport, AnalyticsData, WikiArticle, WikiVersion } from '@/types/admin'

export const adminService = {
  // Doctor Verification
  async getPendingDoctors(): Promise<PendingDoctor[]> {
    const response = await api.get('/api/admin/doctors/pending')
    return response.data
  },

  async verifyDoctor(doctorId: string, approved: boolean): Promise<void> {
    await api.put(`/api/admin/doctors/${doctorId}/verify`, { approved })
  },

  // Content Moderation
  async getFlaggedReports(): Promise<FlaggedReport[]> {
    const response = await api.get('/api/admin/reports/flagged')
    return response.data
  },

  // Analytics
  async getAnalytics(): Promise<AnalyticsData> {
    const response = await api.get('/api/admin/analytics')
    // Transform snake_case to camelCase
    return {
      dailyActiveUsers: response.data.daily_active_users || 0,
      totalScreenings: response.data.total_screenings || 0,
      averageProcessingTime: response.data.average_processing_time || 0,
      mostCommonCancerTypes: (response.data.most_common_cancer_types || []).map((item: any) => ({
        type: item.cancer_type,
        count: item.count
      })),
      geographicDistribution: response.data.geographic_distribution || []
    }
  },

  // Skin-Wiki Management
  async getWikiArticles(): Promise<WikiArticle[]> {
    const response = await api.get('/api/admin/wiki/articles')
    return response.data
  },

  async getWikiArticle(articleId: string): Promise<WikiArticle> {
    const response = await api.get(`/api/admin/wiki/articles/${articleId}`)
    return response.data
  },

  async createWikiArticle(data: {
    title: string
    content: string
    cancerType?: string
  }): Promise<WikiArticle> {
    const response = await api.post('/api/admin/wiki/articles', data)
    return response.data
  },

  async updateWikiArticle(
    articleId: string,
    data: { title?: string; content?: string; cancerType?: string }
  ): Promise<WikiArticle> {
    const response = await api.put(`/api/admin/wiki/articles/${articleId}`, data)
    return response.data
  },

  async deleteWikiArticle(articleId: string): Promise<void> {
    await api.delete(`/api/admin/wiki/articles/${articleId}`)
  },

  async getArticleVersions(articleId: string): Promise<WikiVersion[]> {
    const response = await api.get(`/api/admin/wiki/articles/${articleId}/versions`)
    return response.data
  },
}
