export interface Appointment {
  id: string
  patientId: string
  doctorId: string
  reportId?: string
  scheduledAt: string
  status: 'pending' | 'confirmed' | 'completed' | 'cancelled'
  consultationType: 'in_person' | 'video'
  videoRoomUrl?: string
  createdAt: string
  updatedAt: string
}

export interface AppointmentCreateRequest {
  doctorId: string
  reportId?: string
  scheduledAt: string
  consultationType: 'in_person' | 'video'
}

export interface AppointmentUpdateRequest {
  status: 'pending' | 'confirmed' | 'completed' | 'cancelled'
}
