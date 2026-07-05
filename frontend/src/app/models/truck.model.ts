export type TruckStatus =
  | 'at_warehouse'
  | 'loading'
  | 'ready'
  | 'on_route'
  | 'rerouted'
  | 'returning'
  | 'completed'
  | 'delayed'
  | 'in_transit';

export interface Truck {
  truck_id: string;
  truck_number: number | null;
  name: string;
  status: TruckStatus;
  current_lat: number | null;
  current_lng: number | null;
  current_stop_index: number;
  delay_reason: string | null;
  delay_duration_hours: number | null;
  current_route_id: string | null;
  package_count: number;
}

export interface TruckDetail {
  truck_id: string;
  truck_number: number | null;
  name: string;
  status: TruckStatus;
  current_lat: number | null;
  current_lng: number | null;
  delay_reason: string | null;
  delay_duration_hours: number | null;
  delay_started_at: string | null;
  current_route_id: string | null;
  current_stop_index: number;
  assigned_packages: AssignedPackageSummary[];
}

export interface AssignedPackageSummary {
  package_id: string;
  customer_name: string;
  status: string;
  stop_order: number;
}

export interface TruckLocation {
  truck_id: string;
  lat: number | null;
  lng: number | null;
  status: TruckStatus;
  updated_at: string | null;
}

export interface ViaPoint {
  id: number;
  name: string;
  lat: number;
  lng: number;
  reason: string;
  inserted_before_stop_order: number;
  inserted_at: string;
}

export interface RouteStop {
  stop_id: string;
  stop_order: number;
  customer_id: string;
  customer_name: string;
  estimated_arrival: string | null;
  arrived_at: string | null;
  is_completed: boolean;
}

export interface TruckRoute {
  route_id: string;
  truck_id: string;
  status: string;
  geometry: [number, number][];
  estimated_duration_minutes: number;
  current_waypoint_index: number;
  started_at: string | null;
  completed_at: string | null;
  stops: RouteStop[];
  via_points: ViaPoint[];
}

export interface AssignPackageRequest {
  package_id: string;
}

export interface RerouteRequest {
  location_id: number;
  reason: string;
}
