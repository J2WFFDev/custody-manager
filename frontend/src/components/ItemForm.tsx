import React, { useState } from 'react';
import { itemService } from '../services/itemService';
import type { Item, ItemCreate, ItemUpdate } from '../types/kitItem';

interface ItemFormProps {
  item?: Item;  // If editing existing item
  onSuccess: () => void;
  onCancel: () => void;
}

const ItemForm: React.FC<ItemFormProps> = ({ item, onSuccess, onCancel }) => {
  const [formData, setFormData] = useState({
    item_type: item?.item_type || '',
    make: item?.make || '',
    model: item?.model || '',
    serial_number: item?.serial_number || '',
    friendly_name: item?.friendly_name || '',
    photo_url: item?.photo_url || '',
    quantity: item?.quantity || 1,
    notes: item?.notes || '',
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'quantity' ? parseInt(value) || 1 : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (item) {
        // Update existing item
        const updateData: ItemUpdate = {
          item_type: formData.item_type || undefined,
          make: formData.make || undefined,
          model: formData.model || undefined,
          serial_number: formData.serial_number || undefined,
          friendly_name: formData.friendly_name || undefined,
          photo_url: formData.photo_url || undefined,
          quantity: formData.quantity,
          notes: formData.notes || undefined,
        };
        await itemService.updateItem(item.id, updateData);
      } else {
        // Create new item
        const createData: ItemCreate = {
          item_type: formData.item_type,
          make: formData.make || undefined,
          model: formData.model || undefined,
          serial_number: formData.serial_number || undefined,
          friendly_name: formData.friendly_name || undefined,
          photo_url: formData.photo_url || undefined,
          quantity: formData.quantity,
          notes: formData.notes || undefined,
        };
        await itemService.createItem(createData);
      }
      onSuccess();
    } catch (err) {
      setError(item ? 'Failed to update item' : 'Failed to create item');
      console.error('Error saving item:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-4">
          {item ? 'Edit Item' : 'Add New Item'}
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Item Type *
            </label>
            <select
              name="item_type"
              value={formData.item_type}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select type...</option>
              <option value="firearm">Firearm</option>
              <option value="optic">Optic/Sight</option>
              <option value="case">Case</option>
              <option value="magazine">Magazine</option>
              <option value="tool">Tool</option>
              <option value="accessory">Accessory</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Make
              </label>
              <input
                type="text"
                name="make"
                value={formData.make}
                onChange={handleChange}
                placeholder="e.g., Ruger, Vortex"
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Model
              </label>
              <input
                type="text"
                name="model"
                value={formData.model}
                onChange={handleChange}
                placeholder="e.g., 10/22, Crossfire II"
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Serial Number
            </label>
            <input
              type="text"
              name="serial_number"
              value={formData.serial_number}
              onChange={handleChange}
              placeholder="Encrypted at rest"
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">Serial numbers are encrypted for security</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Friendly Name
            </label>
            <input
              type="text"
              name="friendly_name"
              value={formData.friendly_name}
              onChange={handleChange}
              placeholder="e.g., Red dot sight, Junior rifle #1"
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Quantity
            </label>
            <input
              type="number"
              name="quantity"
              value={formData.quantity}
              onChange={handleChange}
              min="1"
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">For magazines, tools, or accessories</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Photo URL
            </label>
            <input
              type="url"
              name="photo_url"
              value={formData.photo_url}
              onChange={handleChange}
              placeholder="https://..."
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Notes
            </label>
            <textarea
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              rows={3}
              placeholder="Additional information..."
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition-colors disabled:bg-gray-400"
            >
              {loading ? 'Saving...' : (item ? 'Update Item' : 'Create Item')}
            </button>
            <button
              type="button"
              onClick={onCancel}
              className="flex-1 bg-gray-200 text-gray-800 py-2 px-4 rounded hover:bg-gray-300 transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ItemForm;
