export type LocationType = 'warehouse' | 'customer' | 'food' | 'donut';

export interface MapLocation {
  id: number;
  name: string;
  location_type: LocationType;
  lat: number;
  lng: number;
  description: string | null;
}
