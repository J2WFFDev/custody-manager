# OAuth Authentication - Testing Guide

## Quick Start

The OAuth authentication system has been successfully implemented and is ready for testing.

## Prerequisites

1. Python 3.11+ installed
2. PostgreSQL 14+ running
3. Virtual environment activated

## Installation

```bash
cd backend
pip install -r requirements.txt
```

## Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Update `.env` with your OAuth credentials:
   ```
   # Google OAuth (see docs/OAUTH_SETUP.md for setup instructions)
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   
   # Microsoft OAuth (see docs/OAUTH_SETUP.md for setup instructions)
   MICROSOFT_CLIENT_ID=your-microsoft-client-id
   MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
   ```

3. Set up database:
   ```bash
   createdb custody_manager
   alembic upgrade head
   ```

## Running the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API Root: http://localhost:8000
- Swagger Docs: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## Testing OAuth Flows

### Without OAuth Credentials (Testing Structure)

You can test the application structure without setting up OAuth:

```bash
# Run tests
pytest tests/test_security.py tests/test_schemas.py -v

# Verify app starts
python -c "from app.main import app; print('✅ App OK')"
```

### With OAuth Credentials (Full Integration)

1. **Google OAuth Flow:**
   - Navigate to: http://localhost:8000/api/v1/auth/google/login
   - Complete Google sign-in
   - You'll be redirected to frontend with token in URL fragment

2. **Microsoft OAuth Flow:**
   - Navigate to: http://localhost:8000/api/v1/auth/microsoft/login
   - Complete Microsoft sign-in
   - You'll be redirected to frontend with token in URL fragment

3. **Test /auth/me endpoint:**
   - Extract token from URL fragment: `#token=<your-jwt-token>`
   - Make request to `/api/v1/auth/me` with header:
     ```
     Authorization: Bearer <your-jwt-token>
     ```
   - Should return your user information

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/auth/google/login` | Initiate Google OAuth flow |
| GET | `/api/v1/auth/google/callback` | Google OAuth callback (automatic) |
| GET | `/api/v1/auth/microsoft/login` | Initiate Microsoft OAuth flow |
| GET | `/api/v1/auth/microsoft/callback` | Microsoft OAuth callback (automatic) |
| GET | `/api/v1/auth/me` | Get current authenticated user (requires Bearer token) |

## Using cURL to Test

```bash
# Get user info (replace <token> with actual JWT)
curl -H "Authorization: Bearer <token>" \
     http://localhost:8000/api/v1/auth/me
```

## Expected Responses

### Successful Authentication
After OAuth callback, user is redirected to:
```
http://localhost:5173/auth/callback#token=<jwt-token>
```

### GET /auth/me (with valid token)
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "role": "parent",
  "verified_adult": false,
  "is_active": true,
  "created_at": "2026-01-26T23:05:00.000Z"
}
```

### Errors

**401 Unauthorized** (missing or invalid token):
```json
{
  "detail": "Not authenticated"
}
```

**400 Bad Request** (OAuth failed):
```json
{
  "detail": "Authentication failed"
}
```

## Security Features

✅ JWT tokens delivered via URL fragments (not query params)  
✅ Tokens not logged in server logs or browser history  
✅ Secure token expiration (30 minutes default)  
✅ OAuth state validation  
✅ Session middleware for OAuth flow  

## Database Schema

After running migrations, the `users` table will have:
- `id` - Primary key
- `email` - User email (unique, indexed)
- `name` - User full name
- `oauth_provider` - 'google' or 'microsoft'
- `oauth_id` - OAuth provider's user ID (indexed)
- `role` - User role: 'admin', 'armorer', 'coach', 'parent'
- `verified_adult` - Boolean (default: false)
- `is_active` - Boolean (default: true)
- `created_at` - Timestamp
- `updated_at` - Timestamp

## Troubleshooting

### OAuth Redirect Error
- Verify redirect URIs match exactly in OAuth provider settings
- Check GOOGLE_REDIRECT_URI and MICROSOFT_REDIRECT_URI in .env

### Token Invalid
- Token may have expired (30 min default)
- Re-authenticate to get new token

### Database Connection Failed
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env

## Next Steps

1. Set up OAuth credentials (see `docs/OAUTH_SETUP.md`)
2. Implement frontend OAuth callback handler
3. Add protected routes using JWT authentication
4. Configure role-based access control

## Support

For detailed OAuth setup instructions, see:
- `backend/docs/OAUTH_SETUP.md` - OAuth provider configuration
- `backend/README.md` - General backend documentation
