import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import type { Kit } from '../types/kit';
import { kitService } from '../services/kitService';
import KitItemsList from '../components/KitItemsList';
import { KitStatus } from '../types/kit';

const KitDetails: React.FC = () => {
  const { kitId } = useParams<{ kitId: string }>();
  const navigate = useNavigate();
  const [kit, setKit] = useState<Kit | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (kitId) {
      loadKit(parseInt(kitId));
    }
  }, [kitId]);

  const loadKit = async (id: number) => {
    try {
      setLoading(true);
      setError(null);
      const data = await kitService.getKit(id);
      setKit(data);
    } catch (err) {
      setError('Failed to load kit details');
      console.error('Error loading kit:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadgeColor = (status: KitStatus) => {
    switch (status) {
      case KitStatus.AVAILABLE:
        return 'bg-green-100 text-green-800';
      case KitStatus.CHECKED_OUT:
        return 'bg-blue-100 text-blue-800';
      case KitStatus.IN_MAINTENANCE:
        return 'bg-yellow-100 text-yellow-800';
      case KitStatus.LOST:
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatStatus = (status: KitStatus) => {
    return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="text-center py-12">Loading kit details...</div>
      </div>
    );
  }

  if (error || !kit) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error || 'Kit not found'}
        </div>
        <button
          onClick={() => navigate('/kits')}
          className="mt-4 text-blue-600 hover:text-blue-700"
        >
          ← Back to Kits
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/kits')}
          className="text-blue-600 hover:text-blue-700 mb-4 flex items-center gap-1"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Kits
        </button>
        
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-4xl font-bold text-gray-800 mb-2">
              {kit.name}
            </h1>
            <p className="text-gray-600">
              Code: <strong>{kit.code}</strong>
            </p>
          </div>
          <span className={`px-3 py-2 rounded text-sm font-semibold ${getStatusBadgeColor(kit.status)}`}>
            {formatStatus(kit.status)}
          </span>
        </div>
      </div>

      {/* Kit Information */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Kit Information</h2>
        
        <div className="grid grid-cols-2 gap-4 text-sm">
          {kit.description && (
            <div className="col-span-2">
              <span className="font-medium text-gray-700">Description:</span>
              <p className="text-gray-600 mt-1">{kit.description}</p>
            </div>
          )}
          
          {kit.current_custodian_name && (
            <div>
              <span className="font-medium text-gray-700">Current Custodian:</span>
              <p className="text-gray-600">{kit.current_custodian_name}</p>
            </div>
          )}
          
          {kit.expected_return_date && (
            <div>
              <span className="font-medium text-gray-700">Expected Return:</span>
              <p className="text-gray-600">{new Date(kit.expected_return_date).toLocaleDateString()}</p>
            </div>
          )}
          
          {kit.next_maintenance_date && (
            <div>
              <span className="font-medium text-gray-700">Next Maintenance:</span>
              <p className="text-gray-600">{new Date(kit.next_maintenance_date).toLocaleDateString()}</p>
            </div>
          )}
          
          <div>
            <span className="font-medium text-gray-700">Created:</span>
            <p className="text-gray-600">{new Date(kit.created_at).toLocaleDateString()}</p>
          </div>
          
          <div>
            <span className="font-medium text-gray-700">Last Updated:</span>
            <p className="text-gray-600">{new Date(kit.updated_at).toLocaleDateString()}</p>
          </div>
        </div>
      </div>

      {/* Kit Items Section */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <KitItemsList kitId={kit.id} />
      </div>
    </div>
  );
};

export default KitDetails;
