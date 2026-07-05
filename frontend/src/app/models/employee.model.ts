export type PersonaType = 'manager' | 'sales' | 'accounting' | 'warehouse';

export interface Employee {
  id: number;
  employee_id: string;
  name: string;
  persona: PersonaType;
  title: string | null;
  email: string | null;
  is_active: boolean;
}
