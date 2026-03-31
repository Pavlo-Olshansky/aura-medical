export type BodyRegionKey =
  | 'head_cranium' | 'head_face' | 'eyes' | 'ears' | 'mouth_teeth'
  | 'neck_throat' | 'chest' | 'abdomen_upper' | 'abdomen_lower' | 'pelvis'
  | 'back_upper' | 'back_lower'
  | 'shoulder_left' | 'shoulder_right'
  | 'arm_left' | 'arm_right' | 'hand_left' | 'hand_right'
  | 'leg_left' | 'leg_right' | 'foot_left' | 'foot_right'
  | 'whole_body'

export interface BodyRegionSummary {
  visit_count: number
  active_treatment_count: number
  last_visit_date: string | null
  visits_last_year: number
}

export interface BodyMapSummaryResponse {
  regions: Record<string, BodyRegionSummary>
  unmapped_visit_count: number
  whole_body_visit_count: number
}

export interface BodyMapVisitItem {
  id: number
  date: string
  doctor: string | null
  position_name: string | null
  procedure_name: string | null
  clinic_name: string | null
  has_document: boolean
}

export interface BodyMapTreatmentItem {
  id: number
  name: string
  date_start: string
  days: number
  date_end: string
  status: 'active' | 'completed'
}

export interface BodyRegionDetailResponse {
  region: string
  label: string
  visits: BodyMapVisitItem[]
  treatments: BodyMapTreatmentItem[]
}

export type BodyMapView = 'front' | 'back' | 'face'

export interface PolygonData {
  region: BodyRegionKey
  points: string
  centerX: number
  centerY: number
}
