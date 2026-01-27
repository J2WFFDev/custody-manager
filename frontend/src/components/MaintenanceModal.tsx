import React, { useState } from 'react';
import { maintenanceService } from '../services/maintenanceService';
import type { MaintenanceOpenResponse, MaintenanceCloseResponse } from '../types/maintenance';
import Modal from './Modal';

interface MaintenanceModalProps {
  kitCode: string;
  kitName: string;
  isOpen: boolean;
  mode: 'open' | 'close';  // Whether opening or closing maintenance
  onClose: () => void;
  onSuccess: (response: MaintenanceOpenResponse | MaintenanceCloseResponse) => void;
}

const MaintenanceModal: React.FC<MaintenanceModalProps> = ({ 
  kitCode, 
  kitName, 
  isOpen, 
  mode, 
  onClose, 
  onSuccess 
}) => {
  const [notes, setNotes] = useState('');
  const [partsReplaced, setPartsReplaced] = useState('');
  const [roundCount, setRoundCount] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setError(null);
      
      const request = {
        kit_code: kitCode,
        notes: notes.trim() || undefined,
        parts_replaced: partsReplaced.trim() || undefined,
        round_count: roundCount ? parseInt(roundCount) : undefined
      };

      let response;
      if (mode === 'open') {
        response = await maintenanceService.openMaintenance(request);
      } else {
        response = await maintenanceService.closeMaintenance(request);
      }
      
      onSuccess(response);
      
      // Reset form
      setNotes('');
      setPartsReplaced('');
      setRoundCount('');
    } catch (err) {
      console.error('Maintenance operation failed:', err);
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError(`Failed to ${mode} maintenance. Please try again.`);
      }
    } finally {
      setLoading(false);
    }
  };

  const title = mode === 'open' ? 'Open Maintenance' : 'Close Maintenance';
  const submitButtonText = mode === 'open' ? 'Open Maintenance' : 'Close Maintenance';
  const submitButtonColor = mode === 'open' ? 'bg-yellow-600 hover:bg-yellow-700' : 'bg-green-600 hover:bg-green-700';

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title}>
      <div className="mb-4">
        <p className="text-gray-600">
          Kit: <strong className="text-gray-800">{kitName}</strong> ({kitCode})
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-4">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        {/* Notes */}
        <div className="mb-4">
          <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-2">
            Notes
          </label>
          <textarea
            id="notes"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder={mode === 'open' ? "Describe the maintenance issue..." : "Describe what was done..."}
            rows={3}
            disabled={loading}
          />
        </div>

        {/* Parts Replaced */}
        <div className="mb-4">
          <label htmlFor="partsReplaced" className="block text-sm font-medium text-gray-700 mb-2">
            Parts {mode === 'open' ? 'to Replace' : 'Replaced'}
          </label>
          <textarea
            id="partsReplaced"
            value={partsReplaced}
            onChange={(e) => setPartsReplaced(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="List parts (e.g., trigger assembly, spring, sight)"
            rows={2}
            disabled={loading}
          />
        </div>

        {/* Round Count */}
        <div className="mb-6">
          <label htmlFor="roundCount" className="block text-sm font-medium text-gray-700 mb-2">
            Round Count
          </label>
          <input
            type="number"
            id="roundCount"
            value={roundCount}
            onChange={(e) => setRoundCount(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Enter round count"
            min="0"
            disabled={loading}
          />
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3 justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            disabled={loading}
          >
            Cancel
          </button>
          <button
            type="submit"
            className={`px-4 py-2 text-white rounded-lg transition-colors flex items-center gap-2 ${submitButtonColor}`}
            disabled={loading}
          >
            {loading && (
              <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            )}
            {submitButtonText}
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default MaintenanceModal;
