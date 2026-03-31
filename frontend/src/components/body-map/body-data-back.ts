import type { PolygonData } from './types'

/**
 * Back-view click zone polygons for the full body image (1400x763).
 * Coordinates are relative to the full image.
 * Back body figure occupies roughly x=472..721, y=40..710.
 */
export const BACK_POLYGONS: PolygonData[] = [
  // Upper Back
  { region: 'back_upper', points: '555,172 565,162 620,162 630,172 660,185 656,250 600,255 535,250 530,185', centerX: 596, centerY: 210 },

  // Lower Back
  { region: 'back_lower', points: '535,250 600,255 656,250 652,350 600,355 538,350', centerX: 596, centerY: 300 },

  // Shoulders (rear)
  { region: 'shoulder_left', points: '565,162 530,164 510,178 518,192 548,182 558,172', centerX: 538, centerY: 175 },
  { region: 'shoulder_right', points: '620,162 660,164 680,178 672,192 642,182 632,172', centerX: 652, centerY: 175 },

  // Legs (rear)
  { region: 'leg_left', points: '538,372 600,378 596,385 588,435 584,500 576,560 564,560 568,500 570,435 562,385', centerX: 578, centerY: 468 },
  { region: 'leg_right', points: '600,378 662,372 658,385 656,435 658,500 654,560 642,560 636,500 632,435 624,385 596,385', centerX: 636, centerY: 468 },

  // Feet (rear)
  { region: 'foot_left', points: '564,560 576,560 578,585 580,608 572,616 560,613 556,596', centerX: 570, centerY: 590 },
  { region: 'foot_right', points: '642,560 654,560 660,596 658,613 646,616 638,608 640,585', centerX: 648, centerY: 590 },
]
