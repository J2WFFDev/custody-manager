// Maintenance event types and interfaces for frontend

export interface MaintenanceEvent {
  id: number;
  kit_id: number;
  opened_by_id: number;
  opened_by_name: string;
  closed_by_id?: number;
  closed_by_name?: string;
  notes?: string;
  parts_replaced?: string;
  round_count?: number;
  is_open: number;
  created_at: string;
  updated_at: string;
}

export interface MaintenanceOpenRequest {
  kit_code: string;
  notes?: string;
  parts_replaced?: string;
  round_count?: number;
}

export interface MaintenanceCloseRequest {
  kit_code: string;
  notes?: string;
  parts_replaced?: string;
  round_count?: number;
}

export interface MaintenanceOpenResponse {
  message: string;
  event: MaintenanceEvent;
  kit_name: string;
  kit_code: string;
}

export interface MaintenanceCloseResponse {
  message: string;
  event: MaintenanceEvent;
  kit_name: string;
  kit_code: string;
}
