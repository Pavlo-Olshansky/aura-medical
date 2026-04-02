export interface HealthMetricPayload {
  metric_type_id: number
  date: string
  value: number
  secondary_value?: number | null
  notes?: string | null
}

export interface MetricTypePayload {
  name: string
  unit: string
  has_secondary_value?: boolean
  ref_min?: number | null
  ref_max?: number | null
  ref_min_secondary?: number | null
  ref_max_secondary?: number | null
  sort_order?: number
}

export interface LabResultPayload {
  visit_id?: number | null
  date: string
  notes?: string | null
  entries: LabTestEntryPayload[]
}

export interface LabTestEntryPayload {
  biomarker_id?: number | null
  biomarker_name: string
  value: number
  unit: string
  ref_min?: number | null
  ref_max?: number | null
}

export interface BiomarkerReferencePayload {
  name: string
  abbreviation?: string | null
  unit: string
  category: string
  ref_min?: number | null
  ref_max?: number | null
  ref_min_male?: number | null
  ref_max_male?: number | null
  ref_min_female?: number | null
  ref_max_female?: number | null
  sort_order?: number
}

export interface VaccinationPayload {
  date: string
  vaccine_name: string
  manufacturer?: string | null
  lot_number?: string | null
  dose_number?: number
  next_due_date?: string | null
  notes?: string | null
}
