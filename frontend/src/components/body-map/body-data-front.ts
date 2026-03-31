import type { PolygonData } from './types'

/**
 * Front-view SVG polygon data for the human body silhouette.
 * ViewBox: 0 0 200 400
 * Polygons are simplified anatomical regions, not individual muscles.
 * Sources grouped from react-native-body-highlighter (MIT) with custom additions.
 */
export const FRONT_POLYGONS: PolygonData[] = [
  // Head & Face
  { region: 'head_cranium', points: '85,8 100,2 115,8 118,22 100,18 82,22' },
  { region: 'head_face', points: '82,22 100,18 118,22 120,40 112,48 100,50 88,48 80,40' },
  { region: 'eyes', points: '88,28 96,26 96,32 88,32 88,28 104,26 112,28 112,32 104,32 104,26' },
  { region: 'ears', points: '78,28 82,22 80,36 78,28 118,22 122,28 120,36 118,22' },
  { region: 'mouth_teeth', points: '92,40 108,40 108,46 100,48 92,46' },

  // Neck
  { region: 'neck_throat', points: '90,50 110,50 112,62 88,62' },

  // Shoulders
  { region: 'shoulder_left', points: '88,62 72,64 62,72 68,80 84,74 88,68' },
  { region: 'shoulder_right', points: '112,62 128,64 138,72 132,80 116,74 112,68' },

  // Chest
  { region: 'chest', points: '84,74 88,68 112,68 116,74 132,80 130,110 100,115 70,110 68,80' },

  // Arms
  { region: 'arm_left', points: '62,72 54,90 46,120 42,150 50,152 56,125 64,95 68,80' },
  { region: 'arm_right', points: '138,72 146,90 154,120 158,150 150,152 144,125 136,95 132,80' },

  // Hands
  { region: 'hand_left', points: '42,150 50,152 52,168 48,178 38,180 34,172 36,160' },
  { region: 'hand_right', points: '158,150 150,152 148,168 152,178 162,180 166,172 164,160' },

  // Abdomen
  { region: 'abdomen_upper', points: '70,110 100,115 130,110 128,145 100,148 72,145' },
  { region: 'abdomen_lower', points: '72,145 100,148 128,145 126,175 100,180 74,175' },

  // Pelvis
  { region: 'pelvis', points: '74,175 100,180 126,175 128,200 100,205 72,200' },

  // Legs
  { region: 'leg_left', points: '72,200 100,205 96,210 90,250 86,300 78,340 70,340 74,300 76,250 74,210' },
  { region: 'leg_right', points: '100,205 128,200 126,210 124,250 126,300 130,340 122,340 114,300 110,250 104,210 96,210' },

  // Feet
  { region: 'foot_left', points: '70,340 78,340 80,360 82,375 74,380 64,378 62,365' },
  { region: 'foot_right', points: '122,340 130,340 138,365 136,378 126,380 118,375 120,360' },
]
