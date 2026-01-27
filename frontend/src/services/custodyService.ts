// Custody API service

import { api } from './api';
import type { 
  CustodyCheckoutRequest, 
  CustodyCheckoutResponse,
  OffSiteCheckoutRequest,
  OffSiteCheckoutResponse,
  ApprovalDecisionRequest,
  ApprovalDecisionResponse,
  ApprovalRequest,
  AttestationTextResponse,
  CustodyTransferRequest,
  CustodyTransferResponse
} from '../types/custody';

export const custodyService = {
  /**
   * Check out a kit on-premises
   */
  async checkoutKit(request: CustodyCheckoutRequest): Promise<CustodyCheckoutResponse> {
    return api.post<CustodyCheckoutResponse>('/custody/checkout', request);
  },

  /**
   * Request off-site checkout approval
   */
  async requestOffSiteCheckout(request: OffSiteCheckoutRequest): Promise<OffSiteCheckoutResponse> {
    return api.post<OffSiteCheckoutResponse>('/custody/offsite-request', request);
  },

  /**
   * Approve or deny an off-site checkout request
   */
  async approveOrDenyOffSite(request: ApprovalDecisionRequest): Promise<ApprovalDecisionResponse> {
    return api.post<ApprovalDecisionResponse>('/custody/offsite-approve', request);
  },

  /**
   * Get pending approval requests
   */
  async getPendingApprovals(): Promise<ApprovalRequest[]> {
    return api.get<ApprovalRequest[]>('/custody/pending-approvals');
  },

  /**
   * Get responsibility attestation text (CUSTODY-012)
   */
  async getAttestationText(): Promise<AttestationTextResponse> {
    return api.get<AttestationTextResponse>('/custody/attestation-text');
  },

  /**
   * Transfer custody of a kit to a new custodian (CUSTODY-005)
   */
  async transferKitCustody(request: CustodyTransferRequest): Promise<CustodyTransferResponse> {
    return api.post<CustodyTransferResponse>('/custody/transfer', request);
  },
};
