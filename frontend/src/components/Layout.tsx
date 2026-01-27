import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import UserProfile from './UserProfile';
import { authService } from '../services/authService';
import type { User } from '../services/authService';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [currentUser, setCurrentUser] = useState<User | null>(null);

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
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="text-xl font-bold">
              WilcoSS Custody Manager
            </Link>
            <div className="flex items-center gap-6">
              {isLoggedIn && (
                <div className="flex gap-4">
                  <Link to="/" className="hover:text-blue-200 transition-colors">
                    Home
                  </Link>
                  <Link to="/kits" className="hover:text-blue-200 transition-colors">
                    Kits
                  </Link>
                  <Link to="/approvals" className="hover:text-blue-200 transition-colors">
                    Approvals
                  </Link>
                  <Link to="/users" className="hover:text-blue-200 transition-colors">
                    Users
                  </Link>
                  <Link to="/audit" className="hover:text-blue-200 transition-colors">
                    Audit
                  </Link>
                </div>
              )}
              {!isLoggedIn && (
                <Link to="/login" className="hover:text-blue-200 transition-colors">
                  Login
                </Link>
              )}
              {isLoggedIn && currentUser && (
                <div className="flex items-center gap-4">
                  <UserProfile 
                    name={currentUser.name}
                    role={currentUser.role}
                    verifiedAdult={currentUser.verified_adult}
                  />
                  <button
                    onClick={handleLogout}
                    className="px-3 py-1 text-sm bg-blue-700 hover:bg-blue-800 rounded transition-colors"
                  >
                    Logout
                  </button>
                </div>
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
