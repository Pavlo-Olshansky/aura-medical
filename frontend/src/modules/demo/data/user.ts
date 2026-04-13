// Fixed demo user + ProfileData per Clarification Q4.
// Pinned to male so biomarker reference ranges are deterministic.

import type { User, ProfileData } from '@/types'

const DEMO_USER: User = {
  id: -1,
  username: 'demo',
  is_active: true,
  sex: 'male',
}

const DEMO_PROFILE: ProfileData = {
  sex: 'male',
  date_of_birth: '1990-01-01',
  height_cm: 178,
  weight_kg: 75,
  blood_type: 'O+',
  allergies: null,
  chronic_conditions: null,
  emergency_contact_name: 'Контакт екстреної допомоги',
  emergency_contact_phone: '+380 50 000 0000',
  weather_city: 'Київ',
  weather_city_auto: false,
}

export function getDemoUser(): User {
  return { ...DEMO_USER }
}

export function getDemoProfile(): ProfileData {
  return { ...DEMO_PROFILE }
}
