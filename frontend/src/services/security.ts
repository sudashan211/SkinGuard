import api from './api'

export interface ChangePasswordRequest {
  current_password: string
  new_password: string
}

export interface DataExportResponse {
  message: string
  export_id: string
}

export interface AccountDeletionResponse {
  message: string
  deletion_scheduled_at: string
}

export const securityService = {
  /**
   * Change user password
   */
  async changePassword(data: ChangePasswordRequest): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>('/api/auth/change-password', data)
    return response.data
  },

  /**
   * Request data export
   */
  async requestDataExport(): Promise<DataExportResponse> {
    const response = await api.post<DataExportResponse>('/api/auth/export-data')
    return response.data
  },

  /**
   * Delete account
   */
  async deleteAccount(): Promise<AccountDeletionResponse> {
    const response = await api.delete<AccountDeletionResponse>('/api/auth/account')
    return response.data
  },
}
