import { Injectable, signal, computed } from '@angular/core';
import { Employee, PersonaType } from '../models/employee.model';
import { PersonaProfile } from '../models/persona-profile';
import { PERSONA_PROFILES } from '../data/persona-profiles';

const STORAGE_KEY = 'dm_persona_id';

const PERSONA_LABELS: Record<PersonaType, string> = {
  manager: 'Regional Manager',
  sales: 'Sales',
  accounting: 'Accounting',
  warehouse: 'Warehouse',
};

// Mirrors backend app/persona/permissions.py PERSONA_PERMISSIONS
const ROLE_PERMISSIONS: Record<string, Set<string>> = {
  sales: new Set([
    'create_sale', 'view_sales', 'create_package', 'edit_package', 'edit_package_fields',
    'delete_package', 'cancel_package', 'manage_line_items', 'view_invoices',
    'create_complaint', 'update_complaint', 'close_complaint',
  ]),
  accounting: new Set([
    'view_sales', 'view_invoices', 'create_invoice',
    'create_complaint', 'update_complaint', 'close_complaint',
  ]),
  warehouse: new Set([
    'view_sales', 'edit_package', 'edit_package_fields', 'advance_lifecycle',
    'cancel_package', 'record_delay', 'record_damage', 'manage_line_items',
    'view_invoices', 'create_complaint', 'update_complaint', 'close_complaint',
    'assign_to_truck', 'dispatch_truck',
  ]),
  manager: new Set([
    'create_sale', 'view_sales', 'create_package', 'edit_package', 'edit_package_fields',
    'delete_package', 'advance_lifecycle', 'cancel_package', 'record_delay', 'record_damage',
    'manage_line_items', 'view_invoices', 'create_invoice', 'create_complaint',
    'update_complaint', 'close_complaint', 'assign_to_truck', 'dispatch_truck',
    'approve_reroute', 'override_priority',
    'mark_customer_unhappy', 'approve_return', 'approve_expensive_delivery',
    'force_truck_reassignment', 'trigger_demo_scenario', 'reset_demo', 'perform_manager_action',
  ]),
};

@Injectable({ providedIn: 'root' })
export class PersonaService {
  private _personaId = signal<string>(
    localStorage.getItem(STORAGE_KEY) ?? 'michael-scott'
  );
  private _employees = signal<Employee[]>([]);

  readonly currentPersonaId = this._personaId.asReadonly();

  readonly currentEmployee = computed(() =>
    this._employees().find(e => e.employee_id === this._personaId()) ?? null
  );

  readonly currentPersonaProfile = computed<PersonaProfile | null>(() =>
    PERSONA_PROFILES.find(p => p.employeeId === this._personaId()) ?? null
  );

  readonly isManager = computed(() =>
    this.currentEmployee()?.persona === 'manager'
  );

  readonly isSales = computed(() =>
    this.currentEmployee()?.persona === 'sales'
  );

  readonly isAccounting = computed(() =>
    this.currentEmployee()?.persona === 'accounting'
  );

  readonly isWarehouse = computed(() =>
    this.currentEmployee()?.persona === 'warehouse'
  );

  setPersona(employeeId: string): void {
    this._personaId.set(employeeId);
    localStorage.setItem(STORAGE_KEY, employeeId);
  }

  setEmployees(employees: Employee[]): void {
    this._employees.set(employees);
  }

  getPersonaLabel(persona: PersonaType): string {
    return PERSONA_LABELS[persona] ?? persona;
  }

  getRoleGroup(): string {
    const profile = this.currentPersonaProfile();
    if (profile) return profile.roleGroup;
    return this.currentEmployee()?.persona ?? 'general';
  }

  canPerform(operation: string): boolean {
    const emp = this.currentEmployee();
    if (!emp) return false;
    return ROLE_PERMISSIONS[emp.persona]?.has(operation) ?? false;
  }
}
