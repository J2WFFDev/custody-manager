// Custody event types and interfaces for frontend

export const CustodyEventType = {
  CHECKOUT_ONPREM: "checkout_onprem",
  CHECKOUT_OFFSITE: "checkout_offsite",
  CHECKIN: "checkin",
  TRANSFER: "transfer",
  LOST: "lost"
} as const;

export type CustodyEventType = typeof CustodyEventType[keyof typeof CustodyEventType];

export const ApprovalStatus = {
  PENDING: "pending",
  APPROVED: "approved",
  DENIED: "denied"
} as const;

export type ApprovalStatus = typeof ApprovalStatus[keyof typeof ApprovalStatus];

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

// Off-site checkout types
export interface OffSiteCheckoutRequest {
  kit_code: string;
  custodian_name: string;
  custodian_id?: number;
  notes?: string;
  // Attestation fields (CUSTODY-012)
  attestation_signature: string;
  attestation_accepted: boolean;
}

export interface ApprovalRequest {
  id: number;
  kit_id: number;
  kit_name: string;
  kit_code: string;
  requester_id: number;
  requester_name: string;
  custodian_id?: number;
  custodian_name: string;
  status: ApprovalStatus;
  approver_id?: number;
  approver_name?: string;
  approver_role?: string;
  notes?: string;
  denial_reason?: string;
  created_at: string;
  updated_at: string;
  // Attestation fields (CUSTODY-012)
  attestation_text?: string;
  attestation_signature?: string;
  attestation_timestamp?: string;
  attestation_ip_address?: string;
}

export interface OffSiteCheckoutResponse {
  message: string;
  approval_request: ApprovalRequest;
}

export interface ApprovalDecisionRequest {
  approval_request_id: number;
  approve: boolean;
  denial_reason?: string;
}

export interface ApprovalDecisionResponse {
  message: string;
  approval_request: ApprovalRequest;
  custody_event?: CustodyEvent;
}

// Attestation response (CUSTODY-012)
export interface AttestationTextResponse {
  attestation_text: string;
}
