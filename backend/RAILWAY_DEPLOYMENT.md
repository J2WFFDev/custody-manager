# Railway Deployment Guide

## Prerequisites
- Railway account (https://railway.app)
- GitHub repository connected to Railway
- PostgreSQL database provisioned on Railway

## Quick Start

### 1. Create Railway Project

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose `J2WFFDev/custody-manager`
5. Railway will detect the backend automatically

### 2. Add PostgreSQL Database

1. In your Railway project, click "+ New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically provision a PostgreSQL instance
4. The `DATABASE_URL` environment variable is automatically set

### 3. Configure Environment Variables

In Railway project settings → Variables, add:

#### Required Variables:
```bash
# Application
DEBUG=False
ENVIRONMENT=production
APP_NAME=WilcoSS Custody Manager API

# Frontend (update with your Vercel URL)
FRONTEND_URL=https://custody-manager.vercel.app
BACKEND_CORS_ORIGINS=["https://custody-manager.vercel.app","https://*.vercel.app"]

# Security - CRITICAL: Must be persistent across deployments for OAuth to work
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
# Must be at least 32 characters long
# IMPORTANT: Set this BEFORE first deployment to avoid OAuth session issues
SECRET_KEY=
```

**⚠️ CRITICAL: SECRET_KEY Configuration**

The `SECRET_KEY` is essential for OAuth authentication to work correctly:
- It encrypts session data used during OAuth flows
- If it changes between deployments, users will get "mismatching_state" CSRF errors
- Must be set as a persistent environment variable in Railway
- Generate once and keep it the same across all deployments

Generate a secure key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Configure Build Settings

Railway should auto-detect settings from `railway.json`, but verify:

- **Root Directory**: `backend`
- **Build Command**: Automatic (Nixpacks)
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Healthcheck Path**: `/health`

### 5. Run Database Migrations

After first deployment, run migrations:

1. Go to Railway project → Backend service
2. Click "Settings" → "Deploy"
3. Add a custom deploy command (one-time):
   ```bash
   alembic upgrade head
   ```
4. Or use Railway CLI:
   ```bash
   railway run alembic upgrade head
   ```

### 6. Update OAuth Redirect URIs

Update your OAuth provider settings with production URLs:

**Google Cloud Console:**
- Authorized redirect URI: `https://your-backend.railway.app/api/v1/auth/google/callback`

**Microsoft Azure Portal:**
- Redirect URI: `https://your-backend.railway.app/api/v1/auth/microsoft/callback`

## Automatic Deployments

Railway automatically deploys when you push to `main` branch:

1. Push code to GitHub `main` branch
2. Railway detects changes
3. Builds and deploys automatically
4. Runs health check at `/health`
5. Routes traffic to new deployment

## Custom Domain (Optional)

1. In Railway project, go to "Settings" → "Domains"
2. Click "Generate Domain" (gets you `*.railway.app`)
3. Or add custom domain and configure DNS:
   - CNAME: `your-api.yourdomain.com` → `your-project.railway.app`

## Monitoring

### View Logs
```bash
railway logs
```

### Check Deployment Status
- Railway Dashboard shows deployment status
- Health check endpoint: `https://your-backend.railway.app/health`
- API docs: `https://your-backend.railway.app/api/v1/docs`

### Database Access
```bash
# Connect to production database (Railway CLI)
railway connect postgres

# Or use connection string
psql $DATABASE_URL
```

## Rollback

If a deployment fails:
1. Go to Railway Dashboard → Deployments
2. Select a previous successful deployment
3. Click "Redeploy"

## Environment-Specific Configuration

Railway sets `RAILWAY_ENVIRONMENT` automatically. Use it to conditionally configure:

```python
import os

if os.getenv("RAILWAY_ENVIRONMENT") == "production":
    # Production-specific settings
    pass
```

## Troubleshooting

### Database Connection Issues
- Verify `DATABASE_URL` is set correctly
- Check if database service is running
- Ensure migrations have been run

### OAuth Redirect Errors
- **"mismatching_state" CSRF errors**: Verify SECRET_KEY is set and persistent in Railway environment variables
- Verify redirect URIs match exactly in OAuth provider settings
- Check `FRONTEND_URL` environment variable
- Ensure CORS origins include your frontend domain
- For Railway: Make sure SECRET_KEY doesn't change between deployments

### Application Won't Start
- Check logs: `railway logs`
- Verify all required environment variables are set
- Test locally with production-like settings

## Cost Optimization

Railway has a free tier with limitations:
- $5 free credit per month
- Shared resources
- Sleep after inactivity (can be disabled)

For production:
- Upgrade to Pro plan ($20/month)
- Dedicated resources
- No sleep mode
- Custom domains

## Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` (min 32 characters)
- [ ] Database credentials secured (use Railway's auto-generated)
- [ ] OAuth secrets stored as environment variables
- [ ] CORS origins limited to your frontend domain
- [ ] HTTPS enabled (automatic on Railway)
- [ ] Environment variables never committed to Git

## Useful Railway CLI Commands

```bash
# Login
railway login

# Link to project
railway link

# View logs
railway logs

# Run command in Railway environment
railway run <command>

# Open Railway dashboard
railway open

# View environment variables
railway variables

# Add environment variable
railway variables set KEY=value
```

## Next Steps

After deployment:
1. Verify health endpoint: `https://your-backend.railway.app/health`
2. Test API documentation: `https://your-backend.railway.app/api/v1/docs`
3. Update frontend environment variables with Railway backend URL
4. Configure OAuth providers with production redirect URIs
5. Run database migrations
6. Monitor first few deployments for any issues

## Support

- Railway Documentation: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- GitHub Issues: https://github.com/J2WFFDev/custody-manager/issues
