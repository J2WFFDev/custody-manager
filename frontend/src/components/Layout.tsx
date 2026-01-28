import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { authService } from '../services/authService';
import type { User } from '../services/authService';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadUser = async () => {
      if (authService.isAuthenticated()) {
        const user = authService.getUser();
        if (user) {
          setCurrentUser(user);
        } else {
          // Fetch user from API if not in storage
          const fetchedUser = await authService.getCurrentUser();
          setCurrentUser(fetchedUser);
        }
      }
      setLoading(false);
    };

    loadUser();
  }, [location.pathname]);

  const handleLogout = () => {
    authService.logout();
    setCurrentUser(null);
    navigate('/login');
  };

  const isLoggedIn = authService.isAuthenticated();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header/Navigation */}
      <nav className="bg-blue-600 text-white shadow-lg">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <Link to="/" className="text-xl font-bold">
                WilcoSS Custody Manager
              </Link>
              {isLoggedIn && (
                <div className="flex items-center gap-4">
                  <Link to="/" className="hover:underline">
                    Home
                  </Link>
                  <span className="text-gray-300">|</span>
                  <Link to="/kits" className="hover:underline">
                    Kits
                  </Link>
                  <span className="text-gray-300">|</span>
                  <Link to="/inventory" className="hover:underline">
                    Inventory
                  </Link>
                  <span className="text-gray-300">|</span>
                  <Link to="/approvals" className="hover:underline">
                    Approvals
                  </Link>
                  <span className="text-gray-300">|</span>
                  <Link to="/users" className="hover:underline">
                    Users
                  </Link>
                  <span className="text-gray-300">|</span>
                  <Link to="/audit" className="hover:underline">
                    Audit
                  </Link>
                </div>
              )}
            </div>
            <div className="flex items-center gap-4">
              {!isLoggedIn && (
                <Link to="/login" className="hover:text-blue-200 transition-colors">
                  Login
                </Link>
              )}
              {isLoggedIn && currentUser && (
                <>
                  <span className="text-sm">
                    {currentUser.name} <span className="text-gray-300">({currentUser.role})</span>
                  </span>
                  <button
                    onClick={handleLogout}
                    className="px-4 py-2 bg-white text-blue-600 rounded hover:bg-gray-100"
                  >
                    Logout
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-gray-600">Loading...</div>
          </div>
        ) : (
          children
        )}
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
