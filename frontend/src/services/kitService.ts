// Kit API service

import { api, API_URL } from './api';
import type { Kit, KitCreate } from '../types/kit';

export const kitService = {
  /**
   * Get all kits
   */
  async getAllKits(): Promise<Kit[]> {
    return api.get<Kit[]>('/kits/');
  },

  /**
   * Get a single kit by ID
   */
  async getKit(kitId: number): Promise<Kit> {
    return api.get<Kit>(`/kits/${kitId}`);
  },

  /**
   * Create a new kit
   */
  async createKit(kitData: KitCreate): Promise<Kit> {
    return api.post<Kit>('/kits/', kitData);
  },

  /**
   * Get QR code image URL for a kit
   */
  getQrCodeUrl(kitId: number, format: 'png' | 'svg' = 'png'): string {
    return `${API_URL}/kits/${kitId}/qr-image?format=${format}`;
  },
};
