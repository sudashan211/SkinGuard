export interface PatientProfile {
  id: string
  user_id: string
  age: number
  fitzpatrick_scale: 'I' | 'II' | 'III' | 'IV' | 'V' | 'VI'
  family_history?: string
  created_at: string
  updated_at: string
}

export interface SymptomData {
  body_location: string
  sensations: string[]
  visual_changes: string[]
  duration?: string
  notes?: string
}

export interface MedicalReport {
  id: string
  user_id: string
  image_url: string
  thumbnail_url?: string
  predictions: CancerPredictions
  hotspots?: Hotspot[]
  risk_level: 'low' | 'medium' | 'high' | 'urgent'
  symptoms?: SymptomData
  status: 'pending' | 'reviewed' | 'urgent' | 'flagged'
  consultation_notes?: string
  created_at: string
  updated_at: string
}

export interface CancerPredictions {
  melanoma: number
  basal_cell_carcinoma: number
  squamous_cell_carcinoma: number
  actinic_keratosis: number
  benign_keratosis: number
  dermatofibroma: number
  vascular_lesion: number
}

export interface Hotspot {
  x: number
  y: number
  width: number
  height: number
  confidence: number
}

export interface AnalysisResult {
  report_id: string
  predictions: CancerPredictions
  hotspots: Hotspot[]
  risk_level: string
  processing_time: number
  message: string
}

export interface ReportComparison {
  report1: MedicalReport
  report2: MedicalReport
  changes: {
    size_change?: string
    color_change?: string
    risk_level_change?: string
    time_difference_days: number
  }
}
