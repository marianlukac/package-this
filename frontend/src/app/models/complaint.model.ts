export type ComplaintStatus = 'open' | 'closed';

export interface Complaint {
  id: number;
  complaint_id: string;
  sale_id: string;
  description: string;
  status: ComplaintStatus;
  created_by_id: string;
  created_by_name: string;
  package_ids: string[];
  created_at: string;
  updated_at: string;
  closed_at: string | null;
  source: string | null;
}
