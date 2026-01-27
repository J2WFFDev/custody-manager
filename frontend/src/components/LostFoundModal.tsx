import React, { useState } from 'react';
import { custodyService } from '../services/custodyService';
import type { LostFoundResponse } from '../types/custody';

interface LostFoundModalProps {
  onClose: () => void;
  onSuccess: (response: LostFoundResponse) => void;
  kitCode?: string;  // Optional pre-filled kit code from selection
  mode: 'lost' | 'found';
}

const LostFoundModal: React.FC<LostFoundModalProps> = ({ onClose, onSuccess, kitCode: initialKitCode, mode }) => {
  const [kitCode, setKitCode] = useState(initialKitCode || '');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!kitCode.trim()) {
      setError('Kit code is required');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const request = {
        kit_code: kitCode.trim(),
        notes: notes.trim() || undefined
      };

      const response = mode === 'lost' 
        ? await custodyService.reportLost(request)
        : await custodyService.reportFound(request);
      
      onSuccess(response);
    } catch (err) {
      console.error(`Report ${mode} failed:`, err);
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError(`Failed to report kit as ${mode}. Please try again.`);
      }
    } finally {
      setLoading(false);
    }
  };

  const title = mode === 'lost' ? 'Report Kit as Lost' : 'Report Kit as Found';
  const submitButtonText = mode === 'lost' ? 'Report Lost' : 'Report Found';
  const notesPlaceholder = mode === 'lost' 
    ? 'Where was it last seen? Any additional details...'
    : 'Where was it found? In what condition?';

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-md w-full p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-800">{title}</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-4">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {/* Kit Code Input */}
          <div className="mb-4">
            <label htmlFor="kitCode" className="block text-sm font-medium text-gray-700 mb-2">
              Kit Code *
            </label>
            <input
              type="text"
              id="kitCode"
              value={kitCode}
              onChange={(e) => setKitCode(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter kit code"
              required
              disabled={!!initialKitCode}
            />
          </div>

          {/* Notes Input */}
          <div className="mb-6">
            <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-2">
              Notes
            </label>
            <textarea
              id="notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder={notesPlaceholder}
              rows={4}
            />
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className={`px-4 py-2 text-white rounded-md transition-colors ${
                mode === 'lost'
                  ? 'bg-red-600 hover:bg-red-700'
                  : 'bg-green-600 hover:bg-green-700'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              {loading ? 'Processing...' : submitButtonText}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default LostFoundModal;
