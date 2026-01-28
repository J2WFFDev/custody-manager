// Item API service - Master inventory management

import { api } from './api';
import type { Item, ItemCreate, ItemUpdate, ItemAssignRequest, ItemStatus, ItemType } from '../types/kitItem';

export interface ItemFilters {
  status?: ItemStatus;
  item_type?: ItemType;
  assigned?: boolean;  // true=assigned to kit, false=unassigned
}

export const itemService = {
  /**
   * Get all items in master inventory with optional filters
   */
  async getItems(filters?: ItemFilters): Promise<Item[]> {
    const params = new URLSearchParams();
    
    if (filters?.status) {
      params.append('status', filters.status);
    }
    if (filters?.item_type) {
      params.append('item_type', filters.item_type);
    }
    if (filters?.assigned !== undefined) {
      params.append('assigned', String(filters.assigned));
    }
    
    const queryString = params.toString();
    const url = queryString ? `/items?${queryString}` : '/items';
    
    return api.get<Item[]>(url);
  },

  /**
   * Get items assigned to a specific kit
   */
  async getKitItems(kitId: number): Promise<Item[]> {
    return api.get<Item[]>(`/kits/${kitId}/items`);
  },

  /**
   * Get a single item by ID
   */
  async getItem(itemId: number): Promise<Item> {
    return api.get<Item>(`/items/${itemId}`);
  },

  /**
   * Create a new item in master inventory
   */
  async createItem(itemData: ItemCreate): Promise<Item> {
    return api.post<Item>('/items', itemData);
  },

  /**
   * Update an existing item
   */
  async updateItem(itemId: number, itemData: ItemUpdate): Promise<Item> {
    return api.put<Item>(`/items/${itemId}`, itemData);
  },

  /**
   * Assign an item to a kit
   */
  async assignItemToKit(itemId: number, assignData: ItemAssignRequest): Promise<Item> {
    return api.post<Item>(`/items/${itemId}/assign`, assignData);
  },

  /**
   * Unassign an item from its current kit
   */
  async unassignItem(itemId: number): Promise<Item> {
    return api.post<Item>(`/items/${itemId}/unassign`, {});
  },

  /**
   * Delete an item (only if unassigned)
   */
  async deleteItem(itemId: number): Promise<void> {
    await api.delete(`/items/${itemId}`);
  },
};
