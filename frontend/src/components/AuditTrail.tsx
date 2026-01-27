import React, { useState, useEffect } from 'react';
import { eventsService, type EventTimelineResponse } from '../services';

interface AuditTrailProps {
  kitId?: number;
  userId?: number;
  showFilters?: boolean;
}

const AuditTrail: React.FC<AuditTrailProps> = ({ kitId, userId, showFilters = true }) => {
  const [timeline, setTimeline] = useState<EventTimelineResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [eventTypeFilter, setEventTypeFilter] = useState<string>('');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const loadEvents = async () => {
    try {
      setLoading(true);
      setError(null);

      let response: EventTimelineResponse;
      
      const params = {
        event_type: eventTypeFilter || undefined,
        sort_order: sortOrder,
        limit: 100,
      };

      if (kitId) {
        response = await eventsService.getKitEvents(kitId, params);
      } else if (userId) {
        response = await eventsService.getUserEvents(userId, params);
      } else {
        // If neither kitId nor userId is provided, we can't fetch events
        setTimeline(null);
        setLoading(false);
        return;
      }

      setTimeline(response);
    } catch (err) {
      console.error('Failed to load events:', err);
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to load events. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEvents();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [kitId, userId, eventTypeFilter, sortOrder]);

  const formatEventType = (eventType: string): string => {
    const typeMap: Record<string, string> = {
      'checkout_onprem': 'On-Premise Checkout',
      'checkout_offsite': 'Off-Site Checkout',
      'checkin': 'Check-In',
      'transfer': 'Custody Transfer',
      'lost': 'Reported Lost',
      'found': 'Reported Found',
      'open': 'Maintenance Opened',
      'close': 'Maintenance Closed',
    };
    return typeMap[eventType] || eventType;
  };

  const getEventColor = (eventType: string): string => {
    const colorMap: Record<string, string> = {
      'checkout_onprem': 'border-blue-500',
      'checkout_offsite': 'border-purple-500',
      'checkin': 'border-green-500',
      'transfer': 'border-yellow-500',
      'lost': 'border-red-500',
      'found': 'border-emerald-500',
      'open': 'border-orange-500',
      'close': 'border-teal-500',
    };
    return colorMap[eventType] || 'border-gray-500';
  };

  const getEventIcon = (eventType: string): string => {
    const iconMap: Record<string, string> = {
      'checkout_onprem': '📦',
      'checkout_offsite': '🚚',
      'checkin': '✅',
      'transfer': '🔄',
      'lost': '⚠️',
      'found': '🔍',
      'open': '🔧',
      'close': '✔️',
    };
    return iconMap[eventType] || '•';
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  const getActorInfo = (event: EventTimelineResponse['events'][0]): { actor: string; role: string } => {
    // For custody events
    if (event.initiated_by_name) {
      return {
        actor: event.initiated_by_name,
        role: event.custodian_name ? `→ ${event.custodian_name}` : 'Initiated',
      };
    }
    // For maintenance events
    if (event.opened_by_name) {
      // Check if this is a close event based on closed_by_name being present
      if (event.closed_by_name && event.event_type === 'close') {
        return {
          actor: event.closed_by_name,
          role: 'Closed maintenance',
        };
      }
      return {
        actor: event.opened_by_name,
        role: 'Opened maintenance',
      };
    }
    if (event.performed_by_name) {
      return {
        actor: event.performed_by_name,
        role: 'Performed',
      };
    }
    return { actor: 'Unknown', role: '' };
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-gray-600">Loading events...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border-l-4 border-red-400 p-4 rounded">
        <p className="text-red-700">{error}</p>
      </div>
    );
  }

  if (!timeline || timeline.events.length === 0) {
    return (
      <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded">
        <p className="text-yellow-700">No events found.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header with kit/user info */}
      {timeline.kit_name && (
        <div className="bg-blue-50 border-l-4 border-blue-400 p-4 rounded">
          <h3 className="font-semibold text-blue-900">
            {timeline.kit_name} ({timeline.kit_code})
          </h3>
          <p className="text-sm text-blue-700">Total events: {timeline.total}</p>
        </div>
      )}
      {timeline.user_name && (
        <div className="bg-blue-50 border-l-4 border-blue-400 p-4 rounded">
          <h3 className="font-semibold text-blue-900">{timeline.user_name}</h3>
          <p className="text-sm text-blue-700">Total events: {timeline.total}</p>
        </div>
      )}

      {/* Filters */}
      {showFilters && (
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <label htmlFor="eventType" className="block text-sm font-medium text-gray-700 mb-1">
                Event Type
              </label>
              <select
                id="eventType"
                value={eventTypeFilter}
                onChange={(e) => setEventTypeFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Events</option>
                <option value="checkout_onprem">On-Premise Checkout</option>
                <option value="checkout_offsite">Off-Site Checkout</option>
                <option value="checkin">Check-In</option>
                <option value="transfer">Transfer</option>
                <option value="lost">Lost</option>
                <option value="found">Found</option>
                <option value="open">Maintenance Open</option>
                <option value="close">Maintenance Close</option>
              </select>
            </div>
            <div className="flex-1">
              <label htmlFor="sortOrder" className="block text-sm font-medium text-gray-700 mb-1">
                Sort Order
              </label>
              <select
                id="sortOrder"
                value={sortOrder}
                onChange={(e) => setSortOrder(e.target.value as 'asc' | 'desc')}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="desc">Newest First</option>
                <option value="asc">Oldest First</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Timeline */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="divide-y divide-gray-200">
          {timeline.events.map((event) => {
            const actorInfo = getActorInfo(event);
            return (
              <div
                key={event.id}
                className={`border-l-4 ${getEventColor(event.event_type)} p-4 hover:bg-gray-50 transition-colors`}
              >
                <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-2xl" role="img" aria-label={event.event_type}>
                        {getEventIcon(event.event_type)}
                      </span>
                      <h4 className="font-semibold text-gray-900">
                        {formatEventType(event.event_type)}
                      </h4>
                    </div>
                    <div className="text-sm text-gray-600 space-y-1">
                      <p>
                        <span className="font-medium">{actorInfo.actor}</span>
                        {actorInfo.role && <span className="text-gray-500"> {actorInfo.role}</span>}
                      </p>
                      {event.location_type && (
                        <p className="text-gray-500">Location: {event.location_type}</p>
                      )}
                      {event.notes && (
                        <p className="text-gray-700 italic mt-2">"{event.notes}"</p>
                      )}
                      {event.parts_replaced && (
                        <p className="text-gray-700">Parts: {event.parts_replaced}</p>
                      )}
                      {event.round_count !== undefined && event.round_count !== null && (
                        <p className="text-gray-700">Round count: {event.round_count}</p>
                      )}
                      {event.expected_return_date && (
                        <p className="text-gray-700">Expected return: {event.expected_return_date}</p>
                      )}
                    </div>
                  </div>
                  <div className="text-xs text-gray-400 sm:text-right whitespace-nowrap">
                    {formatDate(event.created_at)}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default AuditTrail;
