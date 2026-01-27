# JWT Authentication Flow

This document describes the JWT-based authentication system implemented for the WilcoSS Custody Manager.

## Overview

The application uses OAuth 2.0 (Google and Microsoft) for user authentication, combined with JWT tokens for session management. This provides:

- Secure user authentication via trusted OAuth providers
- Stateless session management using JWT tokens
- Automatic token refresh for seamless user experience
- Protected API endpoints that require authentication

## Architecture

### Backend Components

1. **OAuth Integration** (`app/services/oauth.py`)
   - Google OAuth provider
   - Microsoft OAuth provider
   - Configured via environment variables

2. **JWT Token Management** (`app/core/security.py`)
   - `create_access_token()`: Creates short-lived access tokens (30 minutes)
   - `create_refresh_token()`: Creates long-lived refresh tokens (7 days)
   - `verify_token()`: Validates and decodes JWT tokens

3. **Auth Endpoints** (`app/api/v1/endpoints/auth.py`)
   - `GET /auth/google/login`: Initiates Google OAuth flow
   - `GET /auth/google/callback`: Handles Google OAuth callback
   - `GET /auth/microsoft/login`: Initiates Microsoft OAuth flow
   - `GET /auth/microsoft/callback`: Handles Microsoft OAuth callback
   - `GET /auth/me`: Returns current user information
   - `POST /auth/refresh`: Refreshes access token using refresh token

### Frontend Components

1. **Auth Service** (`frontend/src/services/authService.ts`)
   - Stores tokens in localStorage
   - Manages user session state
   - Handles token refresh automatically
   - Provides logout functionality

2. **API Client** (`frontend/src/services/api.ts`)
   - Automatically includes JWT in Authorization header
   - Handles 401 errors by refreshing tokens
   - Redirects to login on authentication failure

3. **Protected Routes** (`frontend/src/components/ProtectedRoute.tsx`)
   - Wrapper component for authenticated pages
   - Redirects unauthenticated users to login

4. **Auth Callback** (`frontend/src/pages/AuthCallback.tsx`)
   - Handles OAuth redirect from backend
   - Extracts and stores JWT tokens
   - Fetches user information
   - Redirects to application

## Authentication Flow

### Initial Login

1. User clicks "Sign in with Google" or "Sign in with Microsoft"
2. Frontend redirects to `/api/v1/auth/{provider}/login`
3. Backend redirects to OAuth provider login page
4. User authenticates with OAuth provider
5. OAuth provider redirects to `/api/v1/auth/{provider}/callback`
6. Backend:
   - Validates OAuth response
   - Creates or retrieves user from database
   - Generates access and refresh tokens
   - Redirects to frontend callback with tokens in URL hash
7. Frontend callback page:
   - Extracts tokens from URL
   - Stores tokens in localStorage
   - Fetches user information
   - Redirects to home page

### API Requests

1. Frontend makes API request
2. API client automatically includes access token in Authorization header
3. Backend validates token
4. If valid: Process request and return response
5. If expired (401):
   - Frontend automatically calls `/auth/refresh` with refresh token
   - Backend validates refresh token and issues new access token
   - Frontend retries original request with new access token

### Token Refresh

Access tokens expire after 30 minutes. When this happens:

1. API request returns 401 Unauthorized
2. Frontend auth service calls `/auth/refresh` endpoint
3. Backend validates refresh token
4. If valid: Issues new access token
5. If invalid: User is redirected to login page

### Logout

1. User clicks logout button
2. Frontend clears all auth data from localStorage
3. User is redirected to login page

## Configuration

### Backend Environment Variables

```bash
# JWT Settings
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# OAuth - Google
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback

# OAuth - Microsoft
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
MICROSOFT_TENANT_ID=common
MICROSOFT_REDIRECT_URI=http://localhost:8000/api/v1/auth/microsoft/callback

# Frontend URL
FRONTEND_URL=http://localhost:5173
```

### Frontend Environment Variables

```bash
VITE_API_URL=http://localhost:8000
```

## Security Features

1. **Token Type Validation**: Refresh tokens cannot be used as access tokens
2. **Automatic Token Refresh**: Seamless user experience with transparent token renewal
3. **Secure Token Storage**: Tokens stored in localStorage (consider httpOnly cookies for production)
4. **Protected Routes**: Unauthenticated users automatically redirected to login
5. **OAuth Integration**: Leverages trusted identity providers (Google, Microsoft)

## Testing

The JWT authentication system includes comprehensive tests:

- **Token Creation and Validation** (`tests/test_security.py`):
  - Access token generation
  - Refresh token generation
  - Token verification
  - Token expiration validation

- **Auth Endpoints** (`tests/test_auth_endpoints.py`):
  - Current user retrieval
  - Token refresh flow
  - Authentication validation
  - Error handling

Run tests with:
```bash
cd backend
pytest tests/test_security.py tests/test_auth_endpoints.py -v
```

## Future Improvements

1. **HTTP-only Cookies**: Move from localStorage to HTTP-only cookies for enhanced security
2. **Token Revocation**: Implement token blacklist for logout
3. **Multi-factor Authentication**: Add optional MFA for enhanced security
4. **Session Management**: Track active sessions and allow users to revoke access
5. **Rate Limiting**: Add rate limiting to prevent brute force attacks on auth endpoints
