// Item types and interfaces for frontend

// Item status enum - tracks item availability and assignment status
export const ItemStatus = {
  AVAILABLE: "available",        // Not assigned to any kit
  ASSIGNED: "assigned",          // Assigned to a kit (in storage)
  CHECKED_OUT: "checked_out",    // Currently checked out with kit
  LOST: "lost",                  // Reported lost
  MAINTENANCE: "maintenance"     // Under maintenance
} as const;

export type ItemStatus = typeof ItemStatus[keyof typeof ItemStatus];

// Item type enum - categorizes inventory items
export const ItemType = {
  FIREARM: "firearm",
  OPTIC: "optic",
  CASE: "case",
  MAGAZINE: "magazine",
  TOOL: "tool",
  ACCESSORY: "accessory",
  OTHER: "other"
} as const;

export type ItemType = typeof ItemType[keyof typeof ItemType];

// Main Item interface
export interface Item {
  id: number;
  current_kit_id?: number;  // Nullable - item can be unassigned
  item_type: string;
  make?: string;
  model?: string;
  serial_number?: string;
  friendly_name?: string;
  photo_url?: string;
  quantity?: number;
  status: ItemStatus;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface ItemCreate {
  item_type: string;
  make?: string;
  model?: string;
  serial_number?: string;
  friendly_name?: string;
  photo_url?: string;
  quantity?: number;
  current_kit_id?: number;  // Optional - can assign on creation
  notes?: string;
}

export interface ItemUpdate {
  item_type?: string;
  make?: string;
  model?: string;
  serial_number?: string;
  friendly_name?: string;
  photo_url?: string;
  quantity?: number;
  status?: ItemStatus;
  notes?: string;
}

export interface ItemAssignRequest {
  kit_id: number;
  notes?: string;
}

export interface ItemFormData {
  item_type: string;
  make: string;
  model: string;
  serial_number: string;
  friendly_name: string;
  photo_url: string;
  quantity: number;
  notes: string;
}

// Backward compatibility - alias KitItem to Item
export const KitItemStatus = {
  IN_KIT: "in_kit",
  CHECKED_OUT: "checked_out",
  LOST: "lost",
  MAINTENANCE: "maintenance"
} as const;

export type KitItemStatus = typeof KitItemStatus[keyof typeof KitItemStatus];

// KitItem interface for backward compatibility with existing code
export interface KitItem extends Omit<Item, 'current_kit_id' | 'status'> {
  kit_id: number;  // Alias for current_kit_id for backward compatibility
  status: KitItemStatus | ItemStatus;  // Allow both status types
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

