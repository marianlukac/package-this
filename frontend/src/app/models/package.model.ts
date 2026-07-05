export type PackageStatus =
  | 'order_created'
  | 'backorder'
  | 'packaged'
  | 'ready_for_shipping'
  | 'shipped'
  | 'in_transit'
  | 'delivered'
  | 'cancelled'
  | 'damaged'
  | 'returned';

export type PackagePriority = 'standard' | 'express' | 'urgent';

export const TERMINAL_STATUSES: PackageStatus[] = ['delivered', 'cancelled', 'damaged', 'returned'];

export const STATUS_LABELS: Record<PackageStatus, string> = {
  order_created: 'Order Created',
  backorder: 'Backorder',
  packaged: 'Packaged',
  ready_for_shipping: 'Ready for Shipping',
  shipped: 'Shipped',
  in_transit: 'In Transit',
  delivered: 'Delivered',
  cancelled: 'Cancelled',
  damaged: 'Damaged',
  returned: 'Returned',
};

export interface LineItem {
  id: number;
  package_id: string;
  product_name: string;
  product_category: string | null;
  quantity: number;
  unit_description: string | null;
  product_type: 'paper' | 'office_supply';
  fragile: boolean;
}

export interface PackageListItem {
  package_id: string;
  sale_id: string;
  invoice_id: string;
  customer_id: string;
  customer_name: string;
  salesperson_id: string;
  salesperson_name: string;
  invoicing_employee_id: string | null;
  invoicing_employee_name: string | null;
  status: PackageStatus;
  priority: PackagePriority;
  fragile: boolean;
  contents_summary: string | null;
  current_location: string | null;
  truck_id: string | null;
  delay_reason: string | null;
  expected_delivery: string | null;
  created_at: string;
  updated_at: string;
}

export interface Package extends PackageListItem {
  invoicing_employee_id: string | null;
  invoicing_employee_name: string | null;
  destination: string | null;
  delay_duration_hours: number | null;
  line_items: LineItem[];
  open_complaint_count: number;
}

export interface PackageHistoryEntry {
  id: number;
  package_id: string;
  event_type: string;
  actor_id: string | null;
  actor_name: string | null;
  timestamp: string;
  source: string | null;
  entity_type: string | null;
  entity_id: string | null;
  previous_value: string | null;
  new_value: string | null;
  reason: string | null;
  correlation_id: string | null;
}

export interface PackageHistoryResponse {
  package_id: string;
  history: PackageHistoryEntry[];
}

export interface PackageListResponse {
  items: PackageListItem[];
  total: number;
  limit: number;
  offset: number;
}
