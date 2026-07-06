import api from './api'
import type { Doctor, NearbyDoctorsParams } from '@/types/doctor'
import { API_ENDPOINTS } from '@/utils/constants'

export const doctorService = {
  /**
   * Get nearby verified doctors based on location
   */
  async getNearbyDoctors(params: NearbyDoctorsParams): Promise<Doctor[]> {
    const response = await api.get<Doctor[]>(API_ENDPOINTS.DOCTORS.NEARBY, {
      params: {
        lat: params.lat,
        lng: params.lng,
        radius: params.radius || 50, // Default 50km radius
      },
    })
    return response.data
  },

  /**
   * Get doctor details by ID
   */
  async getDoctorById(id: string): Promise<Doctor> {
    const response = await api.get<Doctor>(API_ENDPOINTS.DOCTORS.DETAIL(id))
    return response.data
  },

  /**
   * Generate WhatsApp contact URL
   */
  generateWhatsAppUrl(whatsappNo: string): string {
    const message = encodeURIComponent('I would like to share my Derman Report')
    return `https://wa.me/${whatsappNo}?text=${message}`
  },
}
