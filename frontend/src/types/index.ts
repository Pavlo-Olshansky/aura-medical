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

export interface DashboardData {
  recent_visits: Visit[]
  active_treatments: Treatment[]
  total_visits: number
  total_treatments: number
  active_treatments_count: number
}
