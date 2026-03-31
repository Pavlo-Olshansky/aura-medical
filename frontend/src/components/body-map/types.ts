export type BodyRegionKey =
  | 'head_cranium' | 'head_face' | 'eyes' | 'ears' | 'nose' | 'mouth_teeth'
  | 'neck_throat' | 'chest' | 'abdomen_upper' | 'abdomen_lower' | 'pelvis'
  | 'back_upper' | 'back_lower'
  | 'shoulder_left' | 'shoulder_right'
  | 'arm_left' | 'arm_right' | 'hand_left' | 'hand_right'
  | 'leg_left' | 'leg_right' | 'foot_left' | 'foot_right'
  | 'whole_body'

export type BodyMapView = 'front' | 'back' | 'face'

export interface HotspotData {
  region: BodyRegionKey
  top: string
  left: string
  width: string
  height: string
}
