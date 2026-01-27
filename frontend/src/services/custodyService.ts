// Custody API service

import { api } from './api';
import type { CustodyCheckoutRequest, CustodyCheckoutResponse } from '../types/custody';

export const custodyService = {
  /**
   * Check out a kit on-premises
   */
  async checkoutKit(request: CustodyCheckoutRequest): Promise<CustodyCheckoutResponse> {
    return api.post<CustodyCheckoutResponse>('/custody/checkout', request);
  },
};
