# OAuth Setup Guide

## Overview

This application uses **stateless OAuth** implementation that is compatible with serverless and containerized environments (e.g., Railway, Vercel, AWS Lambda). The OAuth flow does not rely on server-side sessions, making it reliable across container restarts and load-balanced deployments.

## Key Features

✅ **Stateless OAuth** - No session cookies required  
✅ **Encrypted State Tokens** - CSRF protection via signed state parameters  
✅ **Railway/Vercel Compatible** - Works in any stateless environment  
✅ **10-Minute State Expiration** - Automatic timeout for security  
✅ **Container Restart Safe** - No server-side state to lose

## Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Google Identity** or **People API** (Note: Google+ API has been deprecated)
4. Go to Credentials → Create Credentials → OAuth 2.0 Client ID
5. Application type: Web application
6. Authorized redirect URIs:
   - Development: `http://localhost:8000/api/v1/auth/google/callback`
   - Production: `https://your-backend.railway.app/api/v1/auth/google/callback`
7. Copy Client ID and Client Secret to `.env`

## Microsoft OAuth Setup

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to Azure Active Directory → App registrations
3. Click "New registration"
4. Name: WilcoSS Custody Manager
5. Supported account types: Accounts in any organizational directory and personal Microsoft accounts
6. Redirect URI: 
   - Development: `http://localhost:8000/api/v1/auth/microsoft/callback`
   - Production: `https://your-backend.railway.app/api/v1/auth/microsoft/callback`
7. After creation, go to Certificates & secrets → New client secret
8. Copy Application (client) ID and client secret value to `.env`

## Environment Variables

Add to your `.env` file:

```bash
# Required: Secret key for state token encryption (32+ characters)
SECRET_KEY=your-secret-key-here  # Generate with: python -c 'import secrets; print(secrets.token_urlsafe(32))'

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here
GOOGLE_REDIRECT_URI=https://your-backend.railway.app/api/v1/auth/google/callback

# Microsoft OAuth
MICROSOFT_CLIENT_ID=your-microsoft-client-id-here
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret-here
MICROSOFT_REDIRECT_URI=https://your-backend.railway.app/api/v1/auth/microsoft/callback
MICROSOFT_TENANT_ID=common  # or your specific tenant ID

# Frontend URL (for redirect after authentication)
FRONTEND_URL=https://your-frontend.vercel.app
```

## Testing

### Development

1. Start backend: `uvicorn app.main:app --reload`
2. Navigate to: `http://localhost:8000/api/v1/auth/google/login`
3. Or: `http://localhost:8000/api/v1/auth/microsoft/login`
4. Complete OAuth flow
5. You'll be redirected to frontend with JWT tokens in URL fragment

### Production (Railway)

The stateless OAuth implementation is production-ready and requires no additional configuration beyond environment variables.

## API Endpoints

- `GET /api/v1/auth/google/login` - Initiate Google OAuth (returns redirect to Google)
- `GET /api/v1/auth/google/callback` - Google OAuth callback (automatic)
- `GET /api/v1/auth/microsoft/login` - Initiate Microsoft OAuth (returns redirect to Microsoft)
- `GET /api/v1/auth/microsoft/callback` - Microsoft OAuth callback (automatic)
- `GET /api/v1/auth/me` - Get current authenticated user (requires Bearer token)
- `POST /api/v1/auth/refresh` - Refresh access token using refresh token

## OAuth Flow (Stateless)

1. **User clicks "Login with Google"** → Frontend redirects to `/api/v1/auth/google/login`
2. **Backend generates encrypted state token** → Contains provider name and timestamp
3. **User redirected to Google** → With state parameter in URL
4. **User authenticates with Google** → Google redirects back with `code` and `state`
5. **Backend validates state** → Decrypts and validates timestamp (10 min max age)
6. **Backend exchanges code for token** → Direct API call to Google (no session)
7. **Backend fetches user info** → From Google's userinfo endpoint
8. **Backend creates/updates user** → In database
9. **Backend generates JWT tokens** → Access token + refresh token
10. **User redirected to frontend** → With tokens in URL fragment (#access_token=...)

## Security Notes

### State Token Security
- State tokens are encrypted using `itsdangerous.URLSafeTimedSerializer`
- Signed with `SECRET_KEY` to prevent tampering
- 10-minute expiration to limit replay attack window
- Contains provider name to prevent token reuse across providers

### Token Delivery
- JWT tokens are passed via URL fragments (#token=...) rather than query parameters
- Tokens are not logged in server logs or browser history when using fragments
- Frontend must extract token from URL fragment (window.location.hash)

### CSRF Protection
- Encrypted state parameter provides CSRF protection
- No session cookies means no CSRF vulnerability from cookies
- State token validates the entire round-trip

## Troubleshooting

### "State expired - please try logging in again"
- The OAuth flow took more than 10 minutes
- User should retry the login

### "Invalid state - possible CSRF attack"
- State token was tampered with or corrupted
- Check that `SECRET_KEY` is consistent across requests
- Ensure the state parameter is not being modified in transit

### "Failed to exchange code for token"
- Check that `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are correct
- Verify redirect URI matches exactly what's configured in Google Console
- Check network connectivity to Google's token endpoint

### "Failed to get user info"
- Token exchange succeeded but userinfo retrieval failed
- Check network connectivity to Google's userinfo endpoint
- Verify OAuth scopes include "openid email profile"

## Migration from Session-Based OAuth

If you're upgrading from the previous session-based implementation:

1. ✅ No code changes needed in frontend
2. ✅ No changes to OAuth provider configuration
3. ✅ SessionMiddleware can remain (for other features) or be removed
4. ✅ Works immediately in production without additional setup

The stateless implementation is a drop-in replacement that maintains the same API contract.
