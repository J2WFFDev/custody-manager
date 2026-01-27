// Kit types and interfaces for frontend

export const KitStatus = {
  AVAILABLE: "available",
  CHECKED_OUT: "checked_out",
  IN_MAINTENANCE: "in_maintenance",
  LOST: "lost"
} as const;

export type KitStatus = typeof KitStatus[keyof typeof KitStatus];

export interface Kit {
  id: number;
  code: string;
  name: string;
  description?: string;
  status: KitStatus;
  current_custodian_id?: number;
  current_custodian_name?: string;
  created_at: string;
  updated_at: string;
  next_maintenance_date?: string;
  // Warning information (CUSTODY-008, CUSTODY-014, MAINT-002)
  has_warning?: boolean;
  overdue_return?: boolean;
  extended_custody?: boolean;
  days_overdue?: number;
  days_checked_out?: number;
  expected_return_date?: string;
  overdue_maintenance?: boolean;
  days_maintenance_overdue?: number;
}

export interface KitCreate {
  code: string;
  name: string;
  description?: string;
}

export interface KitFormData {
  name: string;
  description: string;
  code: string;
}
