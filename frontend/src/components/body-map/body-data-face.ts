import type { PolygonData } from './types'

/**
 * Face close-up click zone polygons for the full body image (1400x763).
 * Coordinates are relative to the full image.
 * Face occupies roughly x=835..1377, y=25..696.
 * Only the RIGHT ear is visible (face is turned 3/4 left).
 */
export const FACE_POLYGONS: PolygonData[] = [
  // Cranium (forehead and top of head)
  { region: 'head_cranium', points: '930,40 1050,25 1180,35 1230,80 1220,160 1080,145 960,150 900,130 895,80', centerX: 1060, centerY: 90 },

  // Face (cheeks, nose, jaw — excludes eyes, mouth, ear)
  { region: 'head_face', points: '900,130 960,150 1080,145 1220,160 1240,240 1235,340 1210,420 1170,480 1100,510 1020,490 960,450 910,380 890,300 885,220', centerX: 1060, centerY: 320 },

  // Eyes
  { region: 'eyes', points: '940,175 1020,165 1020,210 940,210 940,175 1100,165 1210,175 1210,210 1100,210 1100,165', centerX: 1070, centerY: 190 },

  // Right ear only (visible on the right side of the face)
  { region: 'ears', points: '1230,160 1265,175 1280,230 1270,290 1250,310 1240,240 1230,160', centerX: 1258, centerY: 235 },

  // Mouth and teeth
  { region: 'mouth_teeth', points: '980,380 1100,375 1150,400 1140,445 1100,470 1030,465 975,430', centerX: 1060, centerY: 420 },
]
