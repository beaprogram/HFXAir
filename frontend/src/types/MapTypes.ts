export type POIType = 'gate' | 'restroom' | 'shop' | 'charging' | 'restaurant' | 'info' | 'security';

export interface PointOfInterest {
  id: string;
  name: string;
  type: POIType;
  latitude: number;
  longitude: number;
  description?: string;
  floor?: number;
}

export interface MapRegion {
  latitude: number;
  longitude: number;
  latitudeDelta: number;
  longitudeDelta: number;
}