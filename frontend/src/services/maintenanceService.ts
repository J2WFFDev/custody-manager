// Maintenance API service

import { api } from './api';
import type {
  MaintenanceEvent,
  MaintenanceOpenRequest,
  MaintenanceCloseRequest,
  MaintenanceOpenResponse,
  MaintenanceCloseResponse
} from '../types/maintenance';

export const maintenanceService = {
  /**
   * Open maintenance on a kit
   */
  async openMaintenance(request: MaintenanceOpenRequest): Promise<MaintenanceOpenResponse> {
    return api.post<MaintenanceOpenResponse>('/maintenance/open', request);
  },

  /**
   * Close maintenance on a kit
   */
  async closeMaintenance(request: MaintenanceCloseRequest): Promise<MaintenanceCloseResponse> {
    return api.post<MaintenanceCloseResponse>('/maintenance/close', request);
  },

  /**
   * Get maintenance history for a kit
   */
  async getKitMaintenanceHistory(kitId: number): Promise<MaintenanceEvent[]> {
    return api.get<MaintenanceEvent[]>(`/maintenance/kits/${kitId}/history`);
  },
};
