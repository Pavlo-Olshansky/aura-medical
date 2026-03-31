import type { BodyRegionKey } from './types'

export const BODY_REGION_LABELS: Record<BodyRegionKey, string> = {
  head_cranium: 'Голова (черепна частина)',
  head_face: 'Обличчя',
  eyes: 'Очі',
  ears: 'Вуха',
  nose: 'Ніс',
  mouth_teeth: 'Рот і зуби',
  neck_throat: 'Шия / горло',
  chest: 'Грудна клітка',
  abdomen_upper: 'Верхня частина живота',
  abdomen_lower: 'Нижня частина живота',
  pelvis: 'Таз',
  back_upper: 'Верхня частина спини',
  back_lower: 'Нижня частина спини',
  shoulder_left: 'Ліве плече',
  shoulder_right: 'Праве плече',
  arm_left: 'Ліва рука',
  arm_right: 'Права рука',
  hand_left: 'Ліва кисть',
  hand_right: 'Права кисть',
  leg_left: 'Ліва нога',
  leg_right: 'Права нога',
  foot_left: 'Ліва стопа',
  foot_right: 'Права стопа',
  whole_body: 'Все тіло',
}

export const BODY_REGION_KEYS: BodyRegionKey[] = Object.keys(BODY_REGION_LABELS) as BodyRegionKey[]

/** Keys excluding whole_body — the selectable regions on the body map */
export const SELECTABLE_REGION_KEYS: BodyRegionKey[] = BODY_REGION_KEYS.filter(k => k !== 'whole_body')

/** Dropdown options for forms (includes whole_body) */
export const BODY_REGION_OPTIONS = BODY_REGION_KEYS.map(key => ({
  value: key,
  label: BODY_REGION_LABELS[key],
}))

/** Color tiers for visit density */
export const DENSITY_COLORS = {
  0: '#E8E8E8',
  1: '#B3D4FC',
  3: '#6BA3E8',
  6: '#2E6FC2',
  11: '#1A3D7C',
} as const

export const ACTIVE_TREATMENT_STROKE = '#F59E0B'
export const SELECTED_STROKE = '#FFFFFF'
export const HOVER_FILTER = 'brightness(1.15)'

export function getDensityColor(visitCount: number): string {
  if (visitCount >= 11) return DENSITY_COLORS[11]
  if (visitCount >= 6) return DENSITY_COLORS[6]
  if (visitCount >= 3) return DENSITY_COLORS[3]
  if (visitCount >= 1) return DENSITY_COLORS[1]
  return DENSITY_COLORS[0]
}

export const SPECIALTY_REGION_MAP: Record<string, string[]> = {
  'Кардіолог': ['chest'],
  'Офтальмолог': ['eyes'],
  'Стоматолог': ['mouth_teeth'],
  'Отоларинголог': ['ears', 'nose', 'neck_throat', 'head_face'],
  'ЛОР': ['ears', 'nose', 'neck_throat', 'head_face'],
  'Гастроентеролог': ['abdomen_upper', 'abdomen_lower'],
  'Невролог': ['head_cranium', 'neck_throat', 'back_upper', 'back_lower'],
  'Пульмонолог': ['chest', 'back_upper'],
  'Ендокринолог': ['neck_throat'],
  'Уролог': ['abdomen_lower', 'pelvis'],
  'Гінеколог': ['pelvis', 'abdomen_lower'],
  'Мамолог': ['chest'],
  'Нефролог': ['back_lower', 'abdomen_lower'],
  'Психіатр': ['head_cranium'],
}
