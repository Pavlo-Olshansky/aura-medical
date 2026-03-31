/**
 * Maps source muscle-group IDs from react-native-body-highlighter
 * to our composite body regions.
 *
 * Our 22 regions are anatomical areas; the source provides finer muscle groups.
 * Some of our regions (eyes, ears, mouth, hands, feet) have custom polygon data
 * since the source focuses on muscle groups and doesn't cover these.
 *
 * This file documents the mapping for traceability.
 */

export const SOURCE_TO_REGION_MAP: Record<string, string> = {
  // Head
  'head': 'head_cranium',

  // Neck
  'neck': 'neck_throat',

  // Torso - Front
  'chest': 'chest',
  'abs': 'abdomen_upper', // upper portion
  'obliques': 'abdomen_lower',
  'adductor': 'pelvis',

  // Torso - Back
  'trapezius': 'back_upper',
  'upper-back': 'back_upper',
  'lower-back': 'back_lower',
  'gluteal': 'pelvis',

  // Shoulders
  'deltoids-left': 'shoulder_left',
  'deltoids-right': 'shoulder_right',

  // Arms
  'biceps-left': 'arm_left',
  'biceps-right': 'arm_right',
  'triceps-left': 'arm_left',
  'triceps-right': 'arm_right',
  'forearm-left': 'arm_left',
  'forearm-right': 'arm_right',

  // Legs
  'quadriceps-left': 'leg_left',
  'quadriceps-right': 'leg_right',
  'hamstring-left': 'leg_left',
  'hamstring-right': 'leg_right',
  'calves-left': 'leg_left',
  'calves-right': 'leg_right',
  'abductors-left': 'leg_left',
  'abductors-right': 'leg_right',
}

/**
 * Regions with custom polygon data (not from the source library):
 * - eyes: small regions on face
 * - ears: side regions on head
 * - mouth_teeth: lower face region
 * - hand_left, hand_right: beyond forearm tips
 * - foot_left, foot_right: beyond calf tips
 * - head_face: lower portion of head (distinct from cranium)
 */
export const CUSTOM_REGIONS = [
  'eyes', 'ears', 'mouth_teeth',
  'head_face',
  'hand_left', 'hand_right',
  'foot_left', 'foot_right',
] as const
