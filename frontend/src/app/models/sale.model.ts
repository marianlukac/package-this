export interface Sale {
  id: number;
  sale_id: string;
  customer_id: string;
  salesperson_id: string;
  notes: string | null;
  created_at: string;
}

export interface OperationalSummary {
  total_packages: number;
  active_packages: number;
  in_transit: number;
  delayed: number;
  open_complaints: number;
  active_trucks: number;
  backorder_count?: number;
  order_created_count?: number;
  customer_unhappy_count?: number;
}
