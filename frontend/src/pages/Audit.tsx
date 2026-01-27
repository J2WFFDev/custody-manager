import React, { useState } from 'react';
import AuditTrail from '../components/AuditTrail';

const Audit: React.FC = () => {
  const [viewMode, setViewMode] = useState<'system' | 'kit' | 'user'>('system');
  const [selectedKitId, setSelectedKitId] = useState<string>('');
  const [selectedUserId, setSelectedUserId] = useState<string>('');

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-4xl font-bold text-gray-800 mb-6">
        Audit Trail
      </h1>

      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <p className="text-gray-600 mb-4">
          View complete custody history and compliance logs for kits and users.
        </p>

        {/* View mode selector */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            View Mode
          </label>
          <div className="flex gap-2">
            <button
              onClick={() => {
                setViewMode('system');
                setSelectedKitId('');
                setSelectedUserId('');
              }}
              className={`px-4 py-2 rounded-md transition-colors ${
                viewMode === 'system'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              System-Wide
            </button>
            <button
              onClick={() => setViewMode('kit')}
              className={`px-4 py-2 rounded-md transition-colors ${
                viewMode === 'kit'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              By Kit
            </button>
            <button
              onClick={() => setViewMode('user')}
              className={`px-4 py-2 rounded-md transition-colors ${
                viewMode === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              By User
            </button>
          </div>
        </div>

        {/* Kit ID input */}
        {viewMode === 'kit' && (
          <div className="mb-4">
            <label htmlFor="kitId" className="block text-sm font-medium text-gray-700 mb-1">
              Kit ID
            </label>
            <input
              type="number"
              id="kitId"
              value={selectedKitId}
              onChange={(e) => setSelectedKitId(e.target.value)}
              placeholder="Enter kit ID to view its history"
              className="w-full sm:w-64 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        )}

        {/* User ID input */}
        {viewMode === 'user' && (
          <div className="mb-4">
            <label htmlFor="userId" className="block text-sm font-medium text-gray-700 mb-1">
              User ID
            </label>
            <input
              type="number"
              id="userId"
              value={selectedUserId}
              onChange={(e) => setSelectedUserId(e.target.value)}
              placeholder="Enter user ID to view their history"
              className="w-full sm:w-64 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        )}

        {viewMode === 'system' && (
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
            <p className="text-yellow-700">
              <span className="font-semibold">Coming Soon:</span> System-wide view, CSV/JSON export, and advanced filtering.
            </p>
            <p className="text-yellow-700 mt-2">
              For now, use "By Kit" or "By User" mode to view audit trails.
            </p>
          </div>
        )}
      </div>

      {/* Audit Trail Component */}
      {viewMode === 'kit' && selectedKitId && (
        <AuditTrail kitId={parseInt(selectedKitId, 10)} showFilters={true} />
      )}

      {viewMode === 'user' && selectedUserId && (
        <AuditTrail userId={parseInt(selectedUserId, 10)} showFilters={true} />
      )}

      {viewMode !== 'system' && !selectedKitId && !selectedUserId && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <p className="text-gray-600 text-center">
            Please enter a {viewMode === 'kit' ? 'Kit ID' : 'User ID'} to view the audit trail.
          </p>
        </div>
      )}
    </div>
  );
};

export default Audit;
