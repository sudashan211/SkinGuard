import api from './api'
import type { Appointment, AppointmentCreateRequest, AppointmentUpdateRequest } from '@/types/appointment'
import { API_ENDPOINTS } from '@/utils/constants'

export const appointmentService = {
  /**
   * Create a new appointment
   */
  async createAppointment(data: AppointmentCreateRequest): Promise<Appointment> {
    const response = await api.post<Appointment>(API_ENDPOINTS.APPOINTMENTS.CREATE, data)
    return response.data
  },

  /**
   * Get user's appointments
   */
  async getAppointments(): Promise<Appointment[]> {
    const response = await api.get<Appointment[]>(API_ENDPOINTS.APPOINTMENTS.LIST)
    return response.data
  },

  /**
   * Update appointment status
   */
  async updateAppointmentStatus(
    id: string,
    data: AppointmentUpdateRequest
  ): Promise<Appointment> {
    const response = await api.put<Appointment>(API_ENDPOINTS.APPOINTMENTS.UPDATE(id), data)
    return response.data
  },

  /**
   * Create video room for appointment
   */
  async createVideoRoom(id: string): Promise<{ videoRoomUrl: string }> {
    const response = await api.post<{ videoRoomUrl: string }>(
      API_ENDPOINTS.APPOINTMENTS.VIDEO_ROOM(id)
    )
    return response.data
  },
}
