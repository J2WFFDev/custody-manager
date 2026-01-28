import React, { useState, useEffect } from 'react';
import { itemService } from '../services/itemService';
import type { Item, ItemStatus, ItemType } from '../types/kitItem';

const Inventory: React.FC = () => {
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'available' | 'assigned'>('all');
  const [error, setError] = useState<string | null>(null);

  const loadItems = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const filters = filter === 'all' 
        ? undefined 
        : { assigned: filter === 'assigned' };
      
      const data = await itemService.getItems(filters);
      setItems(data);
    } catch (err) {
      console.error('Failed to load items:', err);
      setError('Failed to load inventory. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadItems();
  }, [filter]);

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'available':
        return 'bg-green-100 text-green-800';
      case 'assigned':
        return 'bg-blue-100 text-blue-800';
      case 'checked_out':
        return 'bg-yellow-100 text-yellow-800';
      case 'lost':
        return 'bg-red-100 text-red-800';
      case 'maintenance':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="container mx-auto px-6 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold text-gray-900">Master Inventory</h1>
          <p className="text-gray-600 mt-2">View and manage all inventory items</p>
        </div>
        <button
          onClick={() => window.location.href = '/inventory/new'}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
        >
          + Add New Item
        </button>
      </div>

      {/* Filter tabs */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'all'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          All Items ({items.length})
        </button>
        <button
          onClick={() => setFilter('available')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'available'
              ? 'bg-green-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Available (Unassigned)
        </button>
        <button
          onClick={() => setFilter('assigned')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            filter === 'assigned'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Assigned to Kits
        </button>
      </div>

      {/* Error message */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      {/* Loading state */}
      {loading && (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading inventory...</p>
        </div>
      )}

      {/* Empty state */}
      {!loading && items.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
            />
          </svg>
          <h3 className="mt-2 text-lg font-medium text-gray-900">No items found</h3>
          <p className="mt-1 text-gray-500">
            {filter === 'available' && 'No unassigned items in inventory.'}
            {filter === 'assigned' && 'No items are currently assigned to kits.'}
            {filter === 'all' && 'Get started by adding your first inventory item.'}
          </p>
        </div>
      )}

      {/* Items grid */}
      {!loading && items.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {items.map((item) => (
            <div
              key={item.id}
              className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6"
            >
              {/* Item header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">
                    {item.friendly_name || `${item.make || ''} ${item.model || ''}`.trim() || 'Unnamed Item'}
                  </h3>
                  <p className="text-sm text-gray-600">
                    {item.item_type}
                  </p>
                </div>
                <span
                  className={`px-2 py-1 text-xs font-medium rounded ${getStatusBadgeClass(
                    item.status
                  )}`}
                >
                  {item.status}
                </span>
              </div>

              {/* Item details */}
              <div className="space-y-2 text-sm">
                {item.make && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Make:</span>
                    <span className="font-medium">{item.make}</span>
                  </div>
                )}
                {item.model && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Model:</span>
                    <span className="font-medium">{item.model}</span>
                  </div>
                )}
                {item.serial_number && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Serial:</span>
                    <span className="font-medium font-mono text-xs">{item.serial_number}</span>
                  </div>
                )}
                {item.quantity && item.quantity > 1 && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Quantity:</span>
                    <span className="font-medium">{item.quantity}</span>
                  </div>
                )}
              </div>

              {/* Kit assignment info */}
              {item.current_kit_id && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <p className="text-sm text-gray-600">
                    Assigned to Kit ID: <span className="font-medium">{item.current_kit_id}</span>
                  </p>
                </div>
              )}

              {/* Actions */}
              <div className="mt-4 flex gap-2">
                <button
                  onClick={() => window.location.href = `/items/${item.id}`}
                  className="flex-1 bg-blue-600 text-white px-3 py-2 rounded hover:bg-blue-700 transition-colors text-sm font-medium"
                >
                  View Details
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Inventory;
