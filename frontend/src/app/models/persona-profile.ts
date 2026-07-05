export type RoleGroup = 'manager' | 'sales' | 'accounting' | 'warehouse' | 'general';

export interface PersonaProfile {
  employeeId: string;
  name: string;
  role: string;
  roleGroup: RoleGroup;
  initials: string;
  themeColor: string;
  description: string;
}
