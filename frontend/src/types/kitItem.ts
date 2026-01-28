// Kit Item types and interfaces for frontend

export const KitItemStatus = {
  IN_KIT: "in_kit",
  CHECKED_OUT: "checked_out",
  LOST: "lost",
  MAINTENANCE: "maintenance"
} as const;

export type KitItemStatus = typeof KitItemStatus[keyof typeof KitItemStatus];

export interface KitItem {
  id: number;
  kit_id: number;
  item_type: string;
  make?: string;
  model?: string;
  serial_number?: string;
  friendly_name?: string;
  photo_url?: string;
  quantity?: number;
  status: KitItemStatus;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface KitItemCreate {
  item_type: string;
  make?: string;
  model?: string;
  serial_number?: string;
  friendly_name?: string;
  photo_url?: string;
  quantity?: number;
  notes?: string;
}

export interface KitItemUpdate {
  item_type?: string;
  make?: string;
  model?: string;
  serial_number?: string;
  friendly_name?: string;
  photo_url?: string;
  quantity?: number;
  status?: KitItemStatus;
  notes?: string;
}

export interface KitItemFormData {
  item_type: string;
  make: string;
  model: string;
  serial_number: string;
  friendly_name: string;
  photo_url: string;
  quantity: number;
  notes: string;
}
