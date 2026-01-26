import React from 'react';

const Audit: React.FC = () => {
  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-4xl font-bold text-gray-800 mb-6">
        Audit Trail
      </h1>

      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <p className="text-gray-600 mb-4">
          View complete custody history and compliance logs.
        </p>
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
          <p className="text-yellow-700">
            <span className="font-semibold">Coming Soon:</span> Audit log viewer, CSV/JSON export, custody timeline, and event filtering.
          </p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-700">Recent Events</h2>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {/* Placeholder audit entries */}
            {[1, 2, 3, 4, 5].map((entry) => (
              <div key={entry} className="border-l-4 border-gray-300 pl-4 py-2">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-medium text-gray-700">Placeholder Event #{entry}</p>
                    <p className="text-sm text-gray-500">No events to display</p>
                  </div>
                  <span className="text-xs text-gray-400">Timestamp</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Audit;
