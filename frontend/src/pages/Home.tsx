import React from 'react';

const Home: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-4xl font-bold text-gray-800 mb-6">
        Welcome to WilcoSS Custody Manager
      </h1>
      
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-2xl font-semibold text-gray-700 mb-4">
          Secure Equipment & Firearm Management
        </h2>
        <p className="text-gray-600 mb-4">
          A comprehensive custody tracking system designed for youth shooting sports organizations.
          Manage firearm kits, equipment, and maintenance with full audit trails and QR-based operations.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="text-blue-600 text-3xl mb-3">🔒</div>
          <h3 className="text-xl font-semibold text-gray-700 mb-2">
            QR-Based Check-in/Check-out
          </h3>
          <p className="text-gray-600">
            Fast and secure equipment tracking with QR code scanning
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="text-blue-600 text-3xl mb-3">👥</div>
          <h3 className="text-xl font-semibold text-gray-700 mb-2">
            Role-Based Access
          </h3>
          <p className="text-gray-600">
            Controlled permissions for Admin, Armorer, Coach, Volunteer, and Parent roles
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="text-blue-600 text-3xl mb-3">📋</div>
          <h3 className="text-xl font-semibold text-gray-700 mb-2">
            Audit Trail
          </h3>
          <p className="text-gray-600">
            Complete custody history with append-only logging for compliance
          </p>
        </div>
      </div>

      <div className="mt-8 bg-blue-50 border-l-4 border-blue-600 p-6 rounded">
        <p className="text-gray-700">
          <span className="font-semibold">Getting Started:</span> Please log in to access the system features.
        </p>
      </div>
    </div>
  );
};

export default Home;
