export interface Doctor {
  id: string
  userId: string
  licenseNo: string
  clinicName: string
  lat: number
  lng: number
  whatsappNo: string
  specialization?: string
  averageRating: number
  reviewCount: number
  verified: boolean
  createdAt: string
  updatedAt: string
  // Joined user profile data
  fullName?: string
  email?: string
}

export interface DoctorLocation {
  lat: number
  lng: number
}

export interface NearbyDoctorsParams {
  lat: number
  lng: number
  radius?: number // in kilometers
}
