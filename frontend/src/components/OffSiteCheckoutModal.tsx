import React, { useState } from 'react';
import { custodyService } from '../services/custodyService';
import type { OffSiteCheckoutResponse } from '../types/custody';

interface OffSiteCheckoutModalProps {
  onClose: () => void;
  onSuccess: (response: OffSiteCheckoutResponse) => void;
  kitCode?: string;  // Optional pre-filled kit code from QR scan
}

const OffSiteCheckoutModal: React.FC<OffSiteCheckoutModalProps> = ({ 
  onClose, 
  onSuccess, 
  kitCode: initialKitCode 
}) => {
  const [kitCode, setKitCode] = useState(initialKitCode || '');
  const [custodianName, setCustodianName] = useState('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [useScanner, setUseScanner] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!kitCode.trim()) {
      setError('Kit code is required');
      return;
    }
    
    if (!custodianName.trim()) {
      setError('Custodian name is required');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const response = await custodyService.requestOffSiteCheckout({
        kit_code: kitCode.trim(),
        custodian_name: custodianName.trim(),
        notes: notes.trim() || undefined
      });
      
      onSuccess(response);
    } catch (err) {
      console.error('Off-site checkout request failed:', err);
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to submit off-site checkout request. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-md w-full p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-800">Request Off-Site Checkout</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="mb-4 p-4 bg-blue-50 border-l-4 border-blue-500">
          <p className="text-sm text-blue-700">
            <strong>Note:</strong> Off-site checkout requires approval from an Armorer or Coach. 
            You must be a verified adult to submit this request.
          </p>
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
            <div className="flex gap-2">
              <input
                type="text"
                id="kitCode"
                value={kitCode}
                onChange={(e) => setKitCode(e.target.value)}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter or scan kit code"
                required
                disabled={loading}
              />
              <button
                type="button"
                onClick={() => setUseScanner(!useScanner)}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex items-center gap-2"
                disabled={loading}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z" />
                </svg>
                {useScanner ? 'Cancel' : 'Scan'}
              </button>
            </div>
          </div>

          {/* QR Scanner Placeholder */}
          {useScanner && (
            <div className="mb-4 p-4 bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg text-center">
              <p className="text-gray-600 mb-2">QR Scanner</p>
              <p className="text-sm text-gray-500 mb-4">
                Camera access will be requested. Scan a kit QR code to auto-fill the code field.
              </p>
              <div className="bg-gray-200 h-48 rounded-lg flex items-center justify-center">
                <svg className="w-16 h-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Note: QR scanning requires additional library installation. For now, use manual entry.
              </p>
            </div>
          )}

          {/* Custodian Name Input */}
          <div className="mb-4">
            <label htmlFor="custodianName" className="block text-sm font-medium text-gray-700 mb-2">
              Custodian Name (e.g., Your Child) *
            </label>
            <input
              type="text"
              id="custodianName"
              value={custodianName}
              onChange={(e) => setCustodianName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter name of person taking kit off-site"
              required
              disabled={loading}
            />
          </div>

          {/* Notes Input */}
          <div className="mb-6">
            <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-2">
              Notes (Optional)
            </label>
            <textarea
              id="notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="E.g., Competition at XYZ, weekend practice"
              rows={3}
              disabled={loading}
            />
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-blue-300 disabled:cursor-not-allowed"
              disabled={loading}
            >
              {loading ? 'Submitting...' : 'Request Approval'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default OffSiteCheckoutModal;
