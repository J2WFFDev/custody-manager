// Custody event types and interfaces for frontend

export const CustodyEventType = {
  CHECKOUT_ONPREM: "checkout_onprem",
  CHECKOUT_OFFSITE: "checkout_offsite",
  CHECKIN: "checkin",
  TRANSFER: "transfer",
  LOST: "lost"
} as const;

export type CustodyEventType = typeof CustodyEventType[keyof typeof CustodyEventType];

export interface CustodyEvent {
  id: number;
  event_type: CustodyEventType;
  kit_id: number;
  initiated_by_id: number;
  initiated_by_name: string;
  custodian_id?: number;
  custodian_name: string;
  notes?: string;
  location_type: string;
  created_at: string;
}

export interface CustodyCheckoutRequest {
  kit_code: string;
  custodian_name: string;
  custodian_id?: number;
  notes?: string;
}

export interface CustodyCheckoutResponse {
  message: string;
  event: CustodyEvent;
  kit_name: string;
  kit_code: string;
}
