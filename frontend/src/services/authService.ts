// Authentication service for JWT token management

const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const USER_KEY = 'user';

export interface User {
  id: number;
  email: string;
  name: string;
  role: string;
  verified_adult: boolean;
  is_active: boolean;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
}

class AuthService {
  /**
   * Store authentication tokens and user data
   */
  setTokens(accessToken: string, refreshToken: string): void {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  }

  /**
   * Get access token from storage
   */
  getAccessToken(): string | null {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  }

  /**
   * Get refresh token from storage
   */
  getRefreshToken(): string | null {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  }

  /**
   * Store user data
   */
  setUser(user: User): void {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }

  /**
   * Get user data from storage
   */
  getUser(): User | null {
    const userData = localStorage.getItem(USER_KEY);
    return userData ? JSON.parse(userData) : null;
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!this.getAccessToken();
  }

  /**
   * Clear all auth data and logout
   */
  logout(): void {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }

  /**
   * Refresh access token using refresh token
   */
  async refreshAccessToken(): Promise<boolean> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      return false;
    }

    try {
      const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${refreshToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        this.logout();
        return false;
      }

      const data = await response.json();
      this.setTokens(data.access_token, refreshToken); // Keep same refresh token
      if (data.user) {
        this.setUser(data.user);
      }
      return true;
    } catch (error) {
      console.error('Failed to refresh token:', error);
      this.logout();
      return false;
    }
  }

  /**
   * Get current user from API
   */
  async getCurrentUser(): Promise<User | null> {
    const accessToken = this.getAccessToken();
    if (!accessToken) {
      return null;
    }

    try {
      const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });

      if (response.status === 401) {
        // Token expired, try to refresh
        const refreshed = await this.refreshAccessToken();
        if (refreshed) {
          // Retry with new token
          return this.getCurrentUser();
        }
        return null;
      }

      if (!response.ok) {
        return null;
      }

      const user = await response.json();
      this.setUser(user);
      return user;
    } catch (error) {
      console.error('Failed to get current user:', error);
      return null;
    }
  }
}

export const authService = new AuthService();
