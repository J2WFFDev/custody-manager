// Events API service

import { api } from './api';

export interface EventTimelineResponse {
  events: Array<{
    id: number;
    event_type: string;
    kit_id?: number;
    initiated_by_id?: number;
    initiated_by_name?: string;
    custodian_id?: number;
    custodian_name?: string;
    performed_by_id?: number;
    performed_by_name?: string;
    opened_by_id?: number;
    opened_by_name?: string;
    closed_by_id?: number;
    closed_by_name?: string;
    notes?: string;
    location_type?: string;
    expected_return_date?: string;
    parts_replaced?: string;
    round_count?: number;
    is_open?: number;
    created_at: string;
    updated_at?: string;
  }>;
  total: number;
  kit_id?: number;
  kit_name?: string;
  kit_code?: string;
  user_id?: number;
  user_name?: string;
}

export const eventsService = {
  /**
   * Get event timeline for a specific kit
   */
  async getKitEvents(
    kitId: number,
    params?: {
      event_type?: string;
      start_date?: string;
      end_date?: string;
      sort_order?: 'asc' | 'desc';
      skip?: number;
      limit?: number;
    }
  ): Promise<EventTimelineResponse> {
    const queryParams = new URLSearchParams();
    if (params?.event_type) queryParams.set('event_type', params.event_type);
    if (params?.start_date) queryParams.set('start_date', params.start_date);
    if (params?.end_date) queryParams.set('end_date', params.end_date);
    if (params?.sort_order) queryParams.set('sort_order', params.sort_order);
    if (params?.skip !== undefined) queryParams.set('skip', params.skip.toString());
    if (params?.limit !== undefined) queryParams.set('limit', params.limit.toString());

    const query = queryParams.toString();
    const endpoint = `/events/kit/${kitId}${query ? `?${query}` : ''}`;
    
    return api.get<EventTimelineResponse>(endpoint);
  },

  /**
   * Get event timeline for a specific user
   */
  async getUserEvents(
    userId: number,
    params?: {
      event_type?: string;
      start_date?: string;
      end_date?: string;
      sort_order?: 'asc' | 'desc';
      skip?: number;
      limit?: number;
    }
  ): Promise<EventTimelineResponse> {
    const queryParams = new URLSearchParams();
    if (params?.event_type) queryParams.set('event_type', params.event_type);
    if (params?.start_date) queryParams.set('start_date', params.start_date);
    if (params?.end_date) queryParams.set('end_date', params.end_date);
    if (params?.sort_order) queryParams.set('sort_order', params.sort_order);
    if (params?.skip !== undefined) queryParams.set('skip', params.skip.toString());
    if (params?.limit !== undefined) queryParams.set('limit', params.limit.toString());

    const query = queryParams.toString();
    const endpoint = `/events/user/${userId}${query ? `?${query}` : ''}`;
    
    return api.get<EventTimelineResponse>(endpoint);
  },
};
