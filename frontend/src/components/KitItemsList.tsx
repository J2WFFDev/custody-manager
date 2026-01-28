import React, { useState, useEffect } from 'react';
import { kitItemService } from '../services/kitItemService';
import type { KitItem } from '../types/kitItem';
import Modal from './Modal';
import KitItemForm from './KitItemForm';

interface KitItemsListProps {
  kitId: number;
}

const KitItemsList: React.FC<KitItemsListProps> = ({ kitId }) => {
  const [items, setItems] = useState<KitItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<KitItem | null>(null);

  const loadItems = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await kitItemService.getKitItems(kitId);
      setItems(data);
    } catch (err) {
      setError('Failed to load kit items');
      console.error('Error loading kit items:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadItems();
  }, [kitId]);

  const handleDelete = async (itemId: number) => {
    if (!confirm('Are you sure you want to remove this item from the kit?')) {
      return;
    }

    try {
      await kitItemService.deleteKitItem(kitId, itemId);
      await loadItems();
    } catch (err) {
      setError('Failed to delete item');
      console.error('Error deleting item:', err);
    }
  };

  const handleItemSaved = () => {
    setIsAddModalOpen(false);
    setEditingItem(null);
    loadItems();
  };

  const getStatusBadge = (status: string) => {
    const statusColors = {
      in_kit: 'bg-green-100 text-green-800',
      checked_out: 'bg-blue-100 text-blue-800',
      lost: 'bg-red-100 text-red-800',
      maintenance: 'bg-yellow-100 text-yellow-800',
    };
    
    const statusLabels = {
      in_kit: 'In Kit',
      checked_out: 'Checked Out',
      lost: 'Lost',
      maintenance: 'Maintenance',
    };

    return (
      <span className={`px-2 py-1 text-xs font-semibold rounded ${statusColors[status as keyof typeof statusColors]}`}>
        {statusLabels[status as keyof typeof statusLabels]}
      </span>
    );
  };

  if (loading) {
    return <div className="text-center py-8">Loading kit items...</div>;
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-800">Kit Components</h3>
        <button
          onClick={() => setIsAddModalOpen(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
        >
          Add Item
        </button>
      </div>

      {items.length === 0 ? (
        <div className="text-center py-8 bg-gray-50 rounded">
          <p className="text-gray-500">No items in this kit yet.</p>
          <button
            onClick={() => setIsAddModalOpen(true)}
            className="mt-2 text-blue-600 hover:text-blue-700"
          >
            Add your first item
          </button>
        </div>
      ) : (
        <div className="grid gap-4">
          {items.map((item) => (
            <div
              key={item.id}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h4 className="text-md font-semibold text-gray-800">
                      {item.friendly_name || `${item.make || ''} ${item.model || ''}`.trim() || item.item_type}
                    </h4>
                    {getStatusBadge(item.status)}
                  </div>
                  
                  <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
                    <div>
                      <span className="font-medium">Type:</span> {item.item_type}
                    </div>
                    {item.make && (
                      <div>
                        <span className="font-medium">Make:</span> {item.make}
                      </div>
                    )}
                    {item.model && (
                      <div>
                        <span className="font-medium">Model:</span> {item.model}
                      </div>
                    )}
                    {item.serial_number && (
                      <div>
                        <span className="font-medium">Serial #:</span> {item.serial_number}
                      </div>
                    )}
                    {item.quantity && item.quantity > 1 && (
                      <div>
                        <span className="font-medium">Quantity:</span> {item.quantity}
                      </div>
                    )}
                  </div>
                  
                  {item.notes && (
                    <div className="mt-2 text-sm text-gray-600">
                      <span className="font-medium">Notes:</span> {item.notes}
                    </div>
                  )}
                </div>

                <div className="flex gap-2 ml-4">
                  <button
                    onClick={() => setEditingItem(item)}
                    className="px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded transition-colors"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(item.id)}
                    className="px-3 py-1 text-sm text-red-600 hover:bg-red-50 rounded transition-colors"
                  >
                    Remove
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Item Modal */}
      <Modal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title="Add Item to Kit"
      >
        <KitItemForm
          kitId={kitId}
          onSuccess={handleItemSaved}
          onCancel={() => setIsAddModalOpen(false)}
        />
      </Modal>

      {/* Edit Item Modal */}
      {editingItem && (
        <Modal
          isOpen={!!editingItem}
          onClose={() => setEditingItem(null)}
          title="Edit Kit Item"
        >
          <KitItemForm
            kitId={kitId}
            item={editingItem}
            onSuccess={handleItemSaved}
            onCancel={() => setEditingItem(null)}
          />
        </Modal>
      )}
    </div>
  );
};

export default KitItemsList;
