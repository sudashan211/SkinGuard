import api from './api'

export interface HealthProfile {
  id: string
  user_id: string
  age: number
  skin_type: string
  family_history: string
  created_at: string
  updated_at: string
}

export interface HealthProfileCreate {
  age: number
  skin_type: string
  family_history?: string
}

export interface HealthProfileUpdate {
  age?: number
  skin_type?: string
  family_history?: string
}

export const healthProfileService = {
  /**
   * Get current user's health profile
   */
  async getProfile(): Promise<HealthProfile> {
    const response = await api.get<HealthProfile>('/api/patient/profile')
    return response.data
  },

  /**
   * Create health profile
   */
  async createProfile(data: HealthProfileCreate): Promise<HealthProfile> {
    const response = await api.post<HealthProfile>('/api/patient/profile', data)
    return response.data
  },

  /**
   * Update health profile
   */
  async updateProfile(data: HealthProfileUpdate): Promise<HealthProfile> {
    const response = await api.put<HealthProfile>('/api/patient/profile', data)
    return response.data
  },
}
