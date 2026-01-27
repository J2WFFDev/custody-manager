import { Navigate } from 'react-router-dom';
import { authService } from '../services/authService';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

/**
 * ProtectedRoute component that redirects to login if user is not authenticated
 */
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  if (!authService.isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
