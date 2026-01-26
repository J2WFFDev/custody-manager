# OAuth Setup Guide

## Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Google Identity** or **People API** (Note: Google+ API has been deprecated)
4. Go to Credentials → Create Credentials → OAuth 2.0 Client ID
5. Application type: Web application
6. Authorized redirect URIs: `http://localhost:8000/api/v1/auth/google/callback`
7. Copy Client ID and Client Secret to `.env`

## Microsoft OAuth Setup

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to Azure Active Directory → App registrations
3. Click "New registration"
4. Name: WilcoSS Custody Manager
5. Supported account types: Accounts in any organizational directory and personal Microsoft accounts
6. Redirect URI: Web - `http://localhost:8000/api/v1/auth/microsoft/callback`
7. After creation, go to Certificates & secrets → New client secret
8. Copy Application (client) ID and client secret value to `.env`

## Environment Variables

Add to your `.env` file:

```
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here

MICROSOFT_CLIENT_ID=your-microsoft-client-id-here
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret-here
```

## Testing

1. Start backend: `uvicorn app.main:app --reload`
2. Navigate to: `http://localhost:8000/api/v1/auth/google/login`
3. Or: `http://localhost:8000/api/v1/auth/microsoft/login`
4. Complete OAuth flow
5. You'll be redirected to frontend with JWT token in URL fragment

## API Endpoints

- `GET /api/v1/auth/google/login` - Initiate Google OAuth
- `GET /api/v1/auth/google/callback` - Google OAuth callback
- `GET /api/v1/auth/microsoft/login` - Initiate Microsoft OAuth
- `GET /api/v1/auth/microsoft/callback` - Microsoft OAuth callback
- `GET /api/v1/auth/me` - Get current authenticated user (requires Bearer token)

## Security Notes

- JWT tokens are passed via URL fragments (#token=...) rather than query parameters for better security
- Tokens are not logged in server logs or browser history when using fragments
- Frontend must extract token from URL fragment (window.location.hash)
