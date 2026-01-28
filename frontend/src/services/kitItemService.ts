// Kit Item API service

import { api } from './api';
import type { KitItem, KitItemCreate, KitItemUpdate } from '../types/kitItem';

export const kitItemService = {
  /**
   * Get all items in a kit
   */
  async getKitItems(kitId: number): Promise<KitItem[]> {
    return api.get<KitItem[]>(`/kits/${kitId}/items`);
  },

  /**
   * Get a single kit item by ID
   */
  async getKitItem(kitId: number, itemId: number): Promise<KitItem> {
    return api.get<KitItem>(`/kits/${kitId}/items/${itemId}`);
  },

  /**
   * Add a new item to a kit
   */
  async createKitItem(kitId: number, itemData: KitItemCreate): Promise<KitItem> {
    return api.post<KitItem>(`/kits/${kitId}/items`, itemData);
  },

  /**
   * Update an existing kit item
   */
  async updateKitItem(kitId: number, itemId: number, itemData: KitItemUpdate): Promise<KitItem> {
    return api.put<KitItem>(`/kits/${kitId}/items/${itemId}`, itemData);
  },

  /**
   * Remove an item from a kit
   */
  async deleteKitItem(kitId: number, itemId: number): Promise<void> {
    await api.delete(`/kits/${kitId}/items/${itemId}`);
  },
};
