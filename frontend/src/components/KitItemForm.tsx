import React, { useState, useEffect } from 'react';
import { kitItemService } from '../services/kitItemService';
import type { KitItem, KitItemCreate, KitItemUpdate } from '../types/kitItem';

interface KitItemFormProps {
  kitId: number;
  item?: KitItem;
  onSuccess: () => void;
  onCancel: () => void;
}

const KitItemForm: React.FC<KitItemFormProps> = ({ kitId, item, onSuccess, onCancel }) => {
  const [formData, setFormData] = useState({
    item_type: item?.item_type || '',
    make: item?.make || '',
    model: item?.model || '',
    serial_number: item?.serial_number || '',
    friendly_name: item?.friendly_name || '',
    photo_url: item?.photo_url || '',
    quantity: item?.quantity || 1,
    status: item?.status || 'in_kit',
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
        const updateData: KitItemUpdate = {
          item_type: formData.item_type,
          make: formData.make || undefined,
          model: formData.model || undefined,
          serial_number: formData.serial_number || undefined,
          friendly_name: formData.friendly_name || undefined,
          photo_url: formData.photo_url || undefined,
          quantity: formData.quantity,
          status: formData.status as any,
          notes: formData.notes || undefined,
        };
        await kitItemService.updateKitItem(kitId, item.id, updateData);
      } else {
        // Create new item
        const createData: KitItemCreate = {
          item_type: formData.item_type,
          make: formData.make || undefined,
          model: formData.model || undefined,
          serial_number: formData.serial_number || undefined,
          friendly_name: formData.friendly_name || undefined,
          photo_url: formData.photo_url || undefined,
          quantity: formData.quantity,
          notes: formData.notes || undefined,
        };
        await kitItemService.createKitItem(kitId, createData);
      }
      onSuccess();
    } catch (err) {
      setError(item ? 'Failed to update item' : 'Failed to create item');
      console.error('Error saving kit item:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
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
          <option value="cleaning_kit">Cleaning Kit</option>
          <option value="ammunition">Ammunition</option>
          <option value="accessory">Accessory</option>
          <option value="other">Other</option>
        </select>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Make/Manufacturer
          </label>
          <input
            type="text"
            name="make"
            value={formData.make}
            onChange={handleChange}
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
            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
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
          placeholder="e.g., 'Primary Rifle' or 'Magazine #1'"
          className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
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
          className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <p className="mt-1 text-xs text-gray-500">
          Serial numbers are encrypted in the database
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4">
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
        </div>

        {item && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              name="status"
              value={formData.status}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="in_kit">In Kit</option>
              <option value="checked_out">Checked Out</option>
              <option value="lost">Lost</option>
              <option value="maintenance">Maintenance</option>
            </select>
          </div>
        )}
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
          className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div className="flex justify-end gap-3 pt-4 border-t">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 text-gray-700 border border-gray-300 rounded hover:bg-gray-50 transition-colors"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={loading || !formData.item_type}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? 'Saving...' : (item ? 'Update Item' : 'Add Item')}
        </button>
      </div>
    </form>
  );
};

export default KitItemForm;
