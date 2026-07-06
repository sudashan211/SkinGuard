export const APP_NAME = 'SkinGuard'
export const APP_DESCRIPTION = 'AI-Powered Skin Cancer Screening Platform'

export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  SIGNUP: '/signup',
  HEALTH_PROFILE_SETUP: '/setup-profile',
  
  // Patient routes
  PATIENT_DASHBOARD: '/patient',
  PATIENT_UPLOAD: '/patient/upload',
  PATIENT_REPORTS: '/patient/reports',
  PATIENT_DOCTORS: '/patient/doctors',
  PATIENT_APPOINTMENTS: '/patient/appointments',
  PATIENT_PROFILE: '/patient/profile',
  
  // Doctor routes
  DOCTOR_DASHBOARD: '/doctor',
  DOCTOR_REPORTS: '/doctor/reports',
  DOCTOR_APPOINTMENTS: '/doctor/appointments',
  DOCTOR_PROFILE: '/doctor/profile',
  
  // Admin routes
  ADMIN_DASHBOARD: '/admin',
  ADMIN_DOCTORS: '/admin/doctors',
  ADMIN_REPORTS: '/admin/reports',
  ADMIN_ANALYTICS: '/admin/analytics',
  ADMIN_CONTENT: '/admin/content',
}

export const API_ENDPOINTS = {
  AUTH: {
    SIGNUP: '/api/auth/signup',
    LOGIN: '/api/auth/login',
    LOGOUT: '/api/auth/logout',
    ME: '/api/auth/me',
    REFRESH: '/api/auth/refresh',
  },
  PATIENT: {
    PROFILE: '/api/patient/profile',
  },
  REPORTS: {
    LIST: '/api/reports',
    DETAIL: (id: string) => `/api/reports/${id}`,
    ANALYZE: '/api/analyze-skin',
    COMPARE: (id: string, otherId: string) => `/api/reports/${id}/compare/${otherId}`,
  },
  DOCTORS: {
    NEARBY: '/api/doctors/nearby',
    REGISTER: '/api/doctors/register',
    DETAIL: (id: string) => `/api/doctors/${id}`,
    REVIEWS: (id: string) => `/api/doctors/${id}/reviews`,
  },
  APPOINTMENTS: {
    LIST: '/api/appointments',
    CREATE: '/api/appointments',
    UPDATE: (id: string) => `/api/appointments/${id}`,
    VIDEO_ROOM: (id: string) => `/api/appointments/${id}/video-room`,
  },
}

export const CANCER_TYPES = [
  'Melanoma',
  'Basal Cell Carcinoma',
  'Squamous Cell Carcinoma',
  'Actinic Keratosis',
  'Benign Keratosis',
  'Dermatofibroma',
  'Vascular Lesion',
]

export const FITZPATRICK_SCALE = ['I', 'II', 'III', 'IV', 'V', 'VI']

export const BODY_LOCATIONS = [
  'Face',
  'Scalp',
  'Neck',
  'Chest',
  'Back',
  'Abdomen',
  'Arms',
  'Hands',
  'Legs',
  'Feet',
]

export const SENSATIONS = [
  'Itching',
  'Pain',
  'Burning',
  'Numbness',
]

export const VISUAL_CHANGES = [
  'Color change',
  'Size increase',
  'Shape change',
  'Border irregularity',
]
