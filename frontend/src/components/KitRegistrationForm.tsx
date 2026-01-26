import React, { useState } from 'react';
import { kitService } from '../services/kitService';
import type { KitFormData } from '../types/kit';

interface KitRegistrationFormProps {
  onSuccess: (kitId: number) => void;
  onCancel: () => void;
}

const KitRegistrationForm: React.FC<KitRegistrationFormProps> = ({ onSuccess, onCancel }) => {
  const [formData, setFormData] = useState<KitFormData>({
    name: '',
    description: '',
    code: '',
    storage_location: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const kitData = {
        code: formData.code,
        name: formData.name,
        description: formData.description || undefined,
      };

      const newKit = await kitService.createKit(kitData);
      
      // Success! Show the QR code
      onSuccess(newKit.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create kit');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-4">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Kit Code */}
      <div>
        <label htmlFor="code" className="block text-sm font-medium text-gray-700 mb-1">
          Kit Code <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="code"
          name="code"
          value={formData.code}
          onChange={handleChange}
          required
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="e.g., KIT-001, ABC-1234-5678"
        />
        <p className="mt-1 text-sm text-gray-500">
          Unique identifier for this kit
        </p>
      </div>

      {/* Kit Name */}
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
          Kit Name <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          required
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="e.g., Air Rifle Kit #1"
        />
      </div>

      {/* Description */}
      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
          Description
        </label>
        <textarea
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter kit description, equipment included, etc."
        />
      </div>

      {/* Storage Location */}
      <div>
        <label htmlFor="storage_location" className="block text-sm font-medium text-gray-700 mb-1">
          Initial Storage Location
        </label>
        <input
          type="text"
          id="storage_location"
          name="storage_location"
          value={formData.storage_location}
          onChange={handleChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="e.g., Armory Shelf A3, Range Storage Locker 12"
        />
        <p className="mt-1 text-sm text-gray-500">
          Where this kit will be initially stored
        </p>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3 pt-4">
        <button
          type="submit"
          disabled={loading}
          className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? 'Creating Kit...' : 'Register Kit & Generate QR'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          disabled={loading}
          className="flex-1 bg-gray-200 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Cancel
        </button>
      </div>
    </form>
  );
};

export default KitRegistrationForm;
