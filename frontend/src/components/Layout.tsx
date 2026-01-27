import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import UserProfile from './UserProfile';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  // Mock user data - in a real app, this would come from auth context
  const [currentUser] = useState({
    name: 'John Doe',
    email: 'john.doe@example.com',
    role: 'admin',
    verifiedAdult: true
  });

  const isLoggedIn = true; // Mock login status

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header/Navigation */}
      <nav className="bg-blue-600 text-white shadow-lg">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="text-xl font-bold">
              WilcoSS Custody Manager
            </Link>
            <div className="flex items-center gap-6">
              <div className="flex gap-4">
                <Link to="/" className="hover:text-blue-200 transition-colors">
                  Home
                </Link>
                <Link to="/kits" className="hover:text-blue-200 transition-colors">
                  Kits
                </Link>
                <Link to="/users" className="hover:text-blue-200 transition-colors">
                  Users
                </Link>
                <Link to="/audit" className="hover:text-blue-200 transition-colors">
                  Audit
                </Link>
                {!isLoggedIn && (
                  <Link to="/login" className="hover:text-blue-200 transition-colors">
                    Login
                  </Link>
                )}
              </div>
              {isLoggedIn && (
                <UserProfile 
                  name={currentUser.name}
                  role={currentUser.role}
                  verifiedAdult={currentUser.verifiedAdult}
                />
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-4 mt-auto">
        <div className="container mx-auto px-4 text-center">
          <p className="text-sm">
            &copy; 2026 WilcoSS Custody Manager. Built for youth shooting sports safety and accountability.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
