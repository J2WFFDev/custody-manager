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
