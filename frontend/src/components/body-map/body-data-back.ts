import type { PolygonData } from './types'

/**
 * Back-view SVG polygon data for the human body silhouette.
 * ViewBox: 0 0 200 400
 * Mirror of front view with back-specific regions (upper back, lower back).
 */
export const BACK_POLYGONS: PolygonData[] = [
  // Head (rear)
  { region: 'head_cranium', points: '85,8 100,2 115,8 118,22 100,20 82,22' },
  { region: 'head_face', points: '82,22 100,20 118,22 118,40 112,48 100,50 88,48 82,40' },

  // Ears (visible from back)
  { region: 'ears', points: '78,28 82,22 80,36 78,28 118,22 122,28 120,36 118,22' },

  // Neck (rear)
  { region: 'neck_throat', points: '90,50 110,50 112,62 88,62' },

  // Shoulders (rear)
  { region: 'shoulder_left', points: '88,62 72,64 62,72 68,80 84,74 88,68' },
  { region: 'shoulder_right', points: '112,62 128,64 138,72 132,80 116,74 112,68' },

  // Upper Back
  { region: 'back_upper', points: '84,74 88,68 112,68 116,74 132,80 130,120 100,124 70,120 68,80' },

  // Lower Back
  { region: 'back_lower', points: '70,120 100,124 130,120 128,175 100,180 72,175' },

  // Arms (rear view)
  { region: 'arm_left', points: '62,72 54,90 46,120 42,150 50,152 56,125 64,95 68,80' },
  { region: 'arm_right', points: '138,72 146,90 154,120 158,150 150,152 144,125 136,95 132,80' },

  // Hands
  { region: 'hand_left', points: '42,150 50,152 52,168 48,178 38,180 34,172 36,160' },
  { region: 'hand_right', points: '158,150 150,152 148,168 152,178 162,180 166,172 164,160' },

  // Pelvis (rear)
  { region: 'pelvis', points: '72,175 100,180 128,175 128,205 100,210 72,205' },

  // Legs (rear)
  { region: 'leg_left', points: '72,205 100,210 96,215 90,250 86,300 78,340 70,340 74,300 76,250 74,215' },
  { region: 'leg_right', points: '100,210 128,205 126,215 124,250 126,300 130,340 122,340 114,300 110,250 104,215 96,215' },

  // Feet (rear)
  { region: 'foot_left', points: '70,340 78,340 80,360 82,375 74,380 64,378 62,365' },
  { region: 'foot_right', points: '122,340 130,340 138,365 136,378 126,380 118,375 120,360' },
]
