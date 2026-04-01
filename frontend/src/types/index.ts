export interface User {
  id: number
  username: string
  is_active: boolean
  sex: string
}

export interface ProfileData {
  sex: string
  date_of_birth: string
  height_cm: number | null
  weight_kg: number | null
  blood_type: string | null
  allergies: string | null
  chronic_conditions: string | null
  emergency_contact_name: string | null
  emergency_contact_phone: string | null
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface Reference {
  id: number
  name: string
  created: string
  updated: string
}

export interface Visit {
  id: number
  date: string
  position: Reference | null
  doctor: string | null
  procedure: Reference | null
  procedure_details: string | null
  clinic: Reference | null
  city: Reference | null
  document: string | null
  has_document?: boolean
  body_region: string | null
  link: string | null
  comment: string | null
  price: number | null
  created: string
  updated: string
}

export interface Treatment {
  id: number
  date_start: string
  name: string
  days: number
  receipt: string
  status: 'active' | 'completed'
  body_region: string | null
  created: string
  updated: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export interface BiomarkerReference {
  id: number
  name: string
  abbreviation: string | null
  unit: string
  category: string
  ref_min: number | null
  ref_max: number | null
  ref_min_male: number | null
  ref_max_male: number | null
  ref_min_female: number | null
  ref_max_female: number | null
  sort_order: number
  created: string
  updated: string
}

export interface MetricType {
  id: number
  name: string
  unit: string
  has_secondary_value: boolean
  ref_min: number | null
  ref_max: number | null
  ref_min_secondary: number | null
  ref_max_secondary: number | null
  sort_order: number
  created: string
  updated: string
}

export interface LabTestEntry {
  id: number
  biomarker_id: number | null
  biomarker_name: string
  value: number
  unit: string
  ref_min: number | null
  ref_max: number | null
  is_normal: boolean | null
}

export interface LabResult {
  id: number
  visit_id: number | null
  date: string
  notes: string | null
  entries: LabTestEntry[]
  entries_count?: number
  out_of_range_count?: number
  visit_date?: string
  visit_procedure?: string
  created: string
  updated: string
}

export interface HealthMetric {
  id: number
  metric_type_id: number
  metric_type: MetricType
  date: string
  value: number
  secondary_value: number | null
  notes: string | null
  created: string
  updated: string
}

export interface Vaccination {
  id: number
  date: string
  vaccine_name: string
  manufacturer: string | null
  lot_number: string | null
  dose_number: number
  next_due_date: string | null
  notes: string | null
  has_document: boolean
  status: 'upcoming' | 'overdue' | 'completed'
  created: string
  updated: string
}

export interface TimelineEvent {
  event_type: 'visit' | 'treatment' | 'lab_result' | 'vaccination'
  event_id: number
  date: string
  title: string
  subtitle: string
  body_region: string | null
  route: string
}

export interface DashboardData {
  recent_visits: Visit[]
  active_treatments: Treatment[]
  total_visits: number
  total_treatments: number
  active_treatments_count: number
  treatment_regions: string[]
  upcoming_vaccinations?: Vaccination[]
  overdue_vaccinations?: Vaccination[]
  expenses_year?: number
  expenses_total?: number
}
