/**
 * Types for Educational Content (Skin-Wiki)
 * Requirements: 16.1, 16.2, 16.3, 16.4, 16.5
 */

export interface SkinWikiArticle {
  id: string;
  title: string;
  slug: string;
  cancer_type: CancerType;
  summary: string;
  content: string;
  image_url?: string;
  risk_factors: string[];
  symptoms: string[];
  treatments: string[];
  prevention_tips: string[];
  published: boolean;
  version: number;
  created_by: string;
  updated_by: string;
  created_at: string;
  updated_at: string;
}

export type CancerType =
  | 'melanoma'
  | 'basal_cell_carcinoma'
  | 'squamous_cell_carcinoma'
  | 'actinic_keratosis'
  | 'benign_keratosis'
  | 'dermatofibroma'
  | 'vascular_lesion';

export interface BodyMapRegion {
  id: string;
  name: string;
  description: string;
  commonLesions: string[];
}

export interface PreventionTip {
  id: string;
  category: 'uv_protection' | 'early_detection' | 'lifestyle' | 'self_examination';
  title: string;
  description: string;
  icon?: string;
}

export interface SelfExaminationGuide {
  id: string;
  title: string;
  steps: ExaminationStep[];
  frequency: string;
  bodyMap: BodyMapRegion[];
}

export interface ExaminationStep {
  stepNumber: number;
  title: string;
  description: string;
  imageUrl?: string;
  tips: string[];
}

export const CANCER_TYPE_LABELS: Record<CancerType, string> = {
  melanoma: 'Melanoma',
  basal_cell_carcinoma: 'Basal Cell Carcinoma',
  squamous_cell_carcinoma: 'Squamous Cell Carcinoma',
  actinic_keratosis: 'Actinic Keratosis',
  benign_keratosis: 'Benign Keratosis',
  dermatofibroma: 'Dermatofibroma',
  vascular_lesion: 'Vascular Lesion',
};

export const CANCER_TYPE_COLORS: Record<CancerType, string> = {
  melanoma: 'bg-red-100 text-red-800 border-red-300',
  basal_cell_carcinoma: 'bg-orange-100 text-orange-800 border-orange-300',
  squamous_cell_carcinoma: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  actinic_keratosis: 'bg-amber-100 text-amber-800 border-amber-300',
  benign_keratosis: 'bg-green-100 text-green-800 border-green-300',
  dermatofibroma: 'bg-blue-100 text-blue-800 border-blue-300',
  vascular_lesion: 'bg-purple-100 text-purple-800 border-purple-300',
};
