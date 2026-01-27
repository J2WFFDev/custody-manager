import React, { useState, useEffect, useCallback } from 'react';
import { maintenanceService } from '../services/maintenanceService';
import type { MaintenanceEvent } from '../types/maintenance';

interface MaintenanceTimelineProps {
  kitId: number;
  kitName?: string;
}

const MaintenanceTimeline: React.FC<MaintenanceTimelineProps> = ({ kitId, kitName }) => {
  const [events, setEvents] = useState<MaintenanceEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadMaintenanceHistory = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const history = await maintenanceService.getKitMaintenanceHistory(kitId);
      setEvents(history);
    } catch (err) {
      console.error('Failed to load maintenance history:', err);
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to load maintenance history. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  }, [kitId]);

  useEffect(() => {
    loadMaintenanceHistory();
  }, [loadMaintenanceHistory]);

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getCurrentMaintenanceStatus = (): { isInMaintenance: boolean; currentEvent?: MaintenanceEvent } => {
    const openEvent = events.find(event => event.is_open === 1);
    return {
      isInMaintenance: !!openEvent,
      currentEvent: openEvent
    };
  };

  const status = getCurrentMaintenanceStatus();

  if (loading) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="flex items-center gap-2 text-gray-600">
          <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>Loading maintenance history...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border-l-4 border-red-500 p-4">
        <div className="flex items-center">
          <svg className="w-5 h-5 text-red-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
          <p className="text-red-700">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header with Kit Name and Current Status */}
      <div className="mb-6">
        {kitName && (
          <h3 className="text-lg font-semibold text-gray-800 mb-2">
            Maintenance History: {kitName}
          </h3>
        )}
        
        {/* Current Maintenance Status Banner */}
        <div className={`p-4 rounded-lg border-2 ${
          status.isInMaintenance 
            ? 'bg-yellow-50 border-yellow-400' 
            : 'bg-green-50 border-green-400'
        }`}>
          <div className="flex items-center gap-2">
            {status.isInMaintenance ? (
              <>
                <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <div>
                  <p className="font-semibold text-yellow-800">Currently in Maintenance</p>
                  {status.currentEvent && (
                    <p className="text-sm text-yellow-700">
                      Opened by {status.currentEvent.opened_by_name} on {formatDate(status.currentEvent.created_at)}
                    </p>
                  )}
                </div>
              </>
            ) : (
              <>
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <p className="font-semibold text-green-800">Operational - No Active Maintenance</p>
                  {events.length > 0 && (
                    <p className="text-sm text-green-700">
                      Last maintenance: {formatDate(events[0].updated_at)}
                    </p>
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Empty State */}
      {events.length === 0 && (
        <div className="text-center py-8 bg-gray-50 rounded-lg border border-gray-200">
          <svg className="w-12 h-12 mx-auto text-gray-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <p className="text-gray-600 font-medium">No maintenance history</p>
          <p className="text-sm text-gray-500 mt-1">This kit has not undergone any maintenance yet.</p>
        </div>
      )}

      {/* Timeline */}
      {events.length > 0 && (
        <div className="relative">
          {/* Timeline Line */}
          <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-300 md:left-6" aria-hidden="true"></div>
          
          {/* Events */}
          <div className="space-y-6">
            {events.map((event) => (
              <div key={event.id} className="relative pl-10 md:pl-14">
                {/* Timeline Dot */}
                <div className={`absolute left-0 md:left-2 w-8 h-8 rounded-full flex items-center justify-center ${
                  event.is_open === 1 
                    ? 'bg-yellow-500 ring-4 ring-yellow-100' 
                    : 'bg-green-500 ring-4 ring-green-100'
                }`}>
                  {event.is_open === 1 ? (
                    <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                  ) : (
                    <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </div>

                {/* Event Card */}
                <div className={`bg-white rounded-lg shadow-md p-4 border-l-4 ${
                  event.is_open === 1 ? 'border-yellow-500' : 'border-green-500'
                }`}>
                  {/* Event Header */}
                  <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2 mb-3">
                    <div>
                      <h4 className={`font-semibold ${
                        event.is_open === 1 ? 'text-yellow-800' : 'text-green-800'
                      }`}>
                        {event.is_open === 1 ? 'Maintenance Opened' : 'Maintenance Closed'}
                      </h4>
                      <p className="text-sm text-gray-600">
                        Opened by: <span className="font-medium">{event.opened_by_name}</span>
                      </p>
                      {event.closed_by_name && (
                        <p className="text-sm text-gray-600">
                          Closed by: <span className="font-medium">{event.closed_by_name}</span>
                        </p>
                      )}
                    </div>
                    <div className="text-sm text-gray-500 sm:text-right">
                      <p className="font-medium">{formatDate(event.created_at)}</p>
                      {event.is_open === 0 && event.updated_at !== event.created_at && (
                        <p className="text-xs">Closed: {formatDate(event.updated_at)}</p>
                      )}
                    </div>
                  </div>

                  {/* Event Details */}
                  <div className="space-y-2">
                    {/* Notes */}
                    {event.notes && (
                      <div className="bg-gray-50 rounded p-3">
                        <p className="text-xs font-semibold text-gray-700 uppercase mb-1">Notes</p>
                        <p className="text-sm text-gray-800 whitespace-pre-wrap">{event.notes}</p>
                      </div>
                    )}

                    {/* Parts Replaced */}
                    {event.parts_replaced && (
                      <div className="bg-blue-50 rounded p-3">
                        <p className="text-xs font-semibold text-blue-700 uppercase mb-1">Parts Replaced</p>
                        <p className="text-sm text-blue-900 whitespace-pre-wrap">{event.parts_replaced}</p>
                      </div>
                    )}

                    {/* Round Count */}
                    {event.round_count !== null && event.round_count !== undefined && (
                      <div className="bg-purple-50 rounded p-3">
                        <p className="text-xs font-semibold text-purple-700 uppercase mb-1">Round Count</p>
                        <p className="text-sm text-purple-900 font-mono">{event.round_count.toLocaleString()} rounds</p>
                      </div>
                    )}
                  </div>

                  {/* Duration for closed events */}
                  {event.is_open === 0 && event.updated_at !== event.created_at && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <p className="text-xs text-gray-600">
                        Duration: {calculateDuration(event.created_at, event.updated_at)}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Helper function to calculate duration between dates
function calculateDuration(startDate: string, endDate: string): string {
  const start = new Date(startDate);
  const end = new Date(endDate);
  const diffMs = end.getTime() - start.getTime();
  
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);
  
  if (diffDays > 0) {
    const hours = diffHours % 24;
    return `${diffDays} day${diffDays !== 1 ? 's' : ''}${hours > 0 ? `, ${hours} hour${hours !== 1 ? 's' : ''}` : ''}`;
  } else if (diffHours > 0) {
    const mins = diffMins % 60;
    return `${diffHours} hour${diffHours !== 1 ? 's' : ''}${mins > 0 ? `, ${mins} min${mins !== 1 ? 's' : ''}` : ''}`;
  } else {
    return `${diffMins} minute${diffMins !== 1 ? 's' : ''}`;
  }
}

export default MaintenanceTimeline;
