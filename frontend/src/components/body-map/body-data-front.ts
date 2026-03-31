import type { PolygonData } from './types'

/**
 * Front-view click zone polygons for the full body image (1400x763).
 * Coordinates are relative to the full image.
 * Front body figure occupies roughly x=75..373, y=35..710.
 */
export const FRONT_POLYGONS: PolygonData[] = [
  // Neck
  { region: 'neck_throat', points: '200,130 245,130 248,155 197,155', centerX: 222, centerY: 142 },

  // Shoulders
  { region: 'shoulder_left', points: '197,155 168,158 148,170 155,185 185,178 197,168', centerX: 175, centerY: 168 },
  { region: 'shoulder_right', points: '248,155 277,158 297,170 290,185 260,178 248,168', centerX: 270, centerY: 168 },

  // Chest
  { region: 'chest', points: '185,178 197,168 248,168 260,178 290,185 286,230 222,234 158,230 155,185', centerX: 222, centerY: 205 },

  // Arms
  { region: 'arm_left', points: '148,170 135,195 120,230 112,275 122,278 132,240 142,205 155,185', centerX: 132, centerY: 225 },
  { region: 'arm_right', points: '297,170 310,195 325,230 333,275 323,278 313,240 303,205 290,185', centerX: 313, centerY: 225 },

  // Hands
  { region: 'hand_left', points: '112,275 122,278 126,300 122,315 110,320 102,312 105,290', centerX: 114, centerY: 298 },
  { region: 'hand_right', points: '333,275 323,278 319,300 323,315 335,320 343,312 340,290', centerX: 331, centerY: 298 },

  // Abdomen
  { region: 'abdomen_upper', points: '158,230 222,234 286,230 284,280 222,284 160,280', centerX: 222, centerY: 257 },
  { region: 'abdomen_lower', points: '160,280 222,284 284,280 282,330 222,335 162,330', centerX: 222, centerY: 307 },

  // Pelvis
  { region: 'pelvis', points: '162,330 222,335 282,330 284,365 222,372 160,365', centerX: 222, centerY: 350 },

  // Legs
  { region: 'leg_left', points: '160,365 222,372 218,380 210,430 206,500 198,560 186,560 190,500 192,430 185,380', centerX: 200, centerY: 465 },
  { region: 'leg_right', points: '222,372 284,365 280,380 278,430 280,500 274,560 262,560 256,500 252,430 244,380 218,380', centerX: 260, centerY: 465 },

  // Feet
  { region: 'foot_left', points: '186,560 198,560 200,585 202,610 194,618 182,615 178,598', centerX: 192, centerY: 592 },
  { region: 'foot_right', points: '262,560 274,560 280,598 278,615 266,618 258,610 260,585', centerX: 268, centerY: 592 },
]
