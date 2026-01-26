import React from 'react';

const Kits: React.FC = () => {
  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-4xl font-bold text-gray-800 mb-6">
        Kit Management
      </h1>

      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <p className="text-gray-600 mb-4">
          This page will display and manage firearm kits and equipment.
        </p>
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
          <p className="text-yellow-700">
            <span className="font-semibold">Coming Soon:</span> Kit listing, QR code generation, check-in/check-out functionality, and maintenance scheduling.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Placeholder cards for kits */}
        {[1, 2, 3].map((kit) => (
          <div key={kit} className="bg-white rounded-lg shadow-md p-6 border-2 border-dashed border-gray-300">
            <h3 className="text-xl font-semibold text-gray-700 mb-2">
              Kit #{kit}
            </h3>
            <p className="text-gray-500 text-sm mb-4">Placeholder</p>
            <div className="space-y-2">
              <p className="text-sm text-gray-600">Status: <span className="font-medium">Available</span></p>
              <p className="text-sm text-gray-600">Last Check: <span className="font-medium">N/A</span></p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Kits;
