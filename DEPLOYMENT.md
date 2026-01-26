# Deployment Guide

This guide covers the deployment process for the WilcoSS Custody & Equipment Manager application.

## Overview

The application uses a split deployment strategy:
- **Frontend**: Deployed on [Vercel](https://vercel.com) (React + Vite)
- **Backend**: Deployed on [Railway](https://railway.app) (FastAPI + PostgreSQL)

## Frontend Deployment (Vercel)

### Initial Setup

#### 1. Connect GitHub Repository to Vercel

1. Visit [Vercel](https://vercel.com) and sign in with your GitHub account
2. Click "Add New Project"
3. Import the `J2WFFDev/custody-manager` repository
4. Vercel will automatically detect the Vite configuration

#### 2. Configure Build Settings

The repository includes a `vercel.json` configuration file that sets:
- **Framework**: Vite
- **Build Command**: `cd frontend && npm run build`
- **Install Command**: `cd frontend && npm install`
- **Output Directory**: `frontend/dist`

These settings are automatically applied when you import the project.

#### 3. Set Environment Variables

In the Vercel project settings, add the following environment variables:

| Variable Name | Description | Example Value |
|--------------|-------------|---------------|
| `VITE_API_URL` | Backend API URL | `https://your-backend.railway.app` |

**Steps to add environment variables:**
1. Go to your Vercel project dashboard
2. Navigate to **Settings** → **Environment Variables**
3. Add each variable with appropriate values for:
   - **Production** (for main branch deployments)
   - **Preview** (for PR deployments - can use staging backend)
   - **Development** (optional)

#### 4. Enable Preview Deployments

Preview deployments are **automatically enabled** for all pull requests. Each PR will get a unique preview URL.

**Configuration:**
- Preview deployments are triggered on every push to a PR
- Comments with preview URLs are automatically added to PRs
- Preview deployments use the same environment variables as Production (unless overridden)

**To customize preview deployment behavior:**
1. Go to **Settings** → **Git**
2. Configure:
   - Which branches trigger deployments
   - Auto-alias settings
   - Deployment protection rules

### Deployment Process

#### Automatic Deployments

**Production Deployments:**
- Triggered automatically when code is merged to the `main` branch
- Deployed to: `https://your-project.vercel.app`
- Build logs available in Vercel dashboard

**Preview Deployments:**
- Triggered automatically for every pull request
- Each commit to a PR triggers a new deployment
- Preview URL format: `https://custody-manager-<hash>.vercel.app`
- Vercel bot comments on PR with deployment status and URL

#### Manual Deployments

You can trigger manual deployments from:
1. **Vercel Dashboard**: Click "Redeploy" on any deployment
2. **Vercel CLI**:
   ```bash
   npm install -g vercel
   vercel login
   vercel --prod  # Deploy to production
   vercel         # Deploy preview
   ```

### Monitoring Deployments

#### View Deployment Status

1. **GitHub**: Check the PR "Checks" tab for Vercel deployment status
2. **Vercel Dashboard**: View all deployments at `vercel.com/<team>/custody-manager`
3. **Deployment Logs**: Click on any deployment to view build logs

#### Common Build Issues

**Build fails with "Module not found":**
- Ensure `package.json` includes all dependencies
- Check that imports use correct casing (case-sensitive in production)

**Environment variables not working:**
- Verify variables are prefixed with `VITE_`
- Check variables are set in Vercel project settings
- Redeploy after adding new environment variables

**Build timeout:**
- Default timeout is 10 minutes (should be sufficient for this project)
- If needed, upgrade Vercel plan for longer build times

### Rollback

To rollback to a previous deployment:
1. Go to the Vercel dashboard
2. Navigate to **Deployments**
3. Find the working deployment
4. Click **⋯** → **Promote to Production**

### Custom Domain (Optional)

To use a custom domain:
1. Go to **Settings** → **Domains**
2. Add your domain (e.g., `custody.yourdomain.com`)
3. Configure DNS records as shown in Vercel
4. SSL certificates are automatically provisioned

## Backend Deployment (Railway)

### Initial Setup

#### 1. Connect GitHub Repository to Railway

1. Visit [Railway](https://railway.app) and sign in
2. Create a new project
3. Select "Deploy from GitHub repo"
4. Choose `J2WFFDev/custody-manager`
5. Configure the service to use the `backend` directory

#### 2. Add PostgreSQL Database

1. In your Railway project, click "New Service"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically provision a database and set the `DATABASE_URL` variable

#### 3. Configure Environment Variables

In Railway project settings, add:

| Variable Name | Description | Required |
|--------------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Auto-set by Railway |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | Yes |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | Yes |
| `MICROSOFT_CLIENT_ID` | Microsoft OAuth client ID | Yes |
| `MICROSOFT_CLIENT_SECRET` | Microsoft OAuth client secret | Yes |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | Yes (generate strong key) |
| `FRONTEND_URL` | Vercel frontend URL | Yes (for CORS) |

**Generate JWT secret:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### 4. Configure Build and Start Commands

Railway should auto-detect the Python app. Verify settings:
- **Root Directory**: `backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Deployment Process

- **Automatic**: Deployments trigger on push to `main` branch
- **Manual**: Click "Deploy" in Railway dashboard
- **Rollback**: Use Railway's deployment history to rollback

## Integration Between Frontend and Backend

### CORS Configuration

Ensure the backend allows requests from the Vercel frontend:

```python
# In backend/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL")],  # Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### OAuth Redirect URIs

Update OAuth application settings:

**Google Cloud Console:**
- Authorized redirect URIs: `https://your-backend.railway.app/auth/google/callback`

**Microsoft Azure Portal:**
- Redirect URIs: `https://your-backend.railway.app/auth/microsoft/callback`

## Monitoring and Maintenance

### Health Checks

- **Frontend**: Visit `https://your-project.vercel.app`
- **Backend**: Visit `https://your-backend.railway.app/health`

### Logs

- **Vercel**: View build and function logs in dashboard
- **Railway**: View application logs in real-time in dashboard

### Analytics

- **Vercel**: Provides built-in analytics for page views, performance
- **Railway**: Provides metrics for CPU, memory, network usage

## Security Best Practices

1. **Never commit secrets**: Use environment variables for all sensitive data
2. **Rotate secrets regularly**: Update OAuth secrets and JWT keys periodically
3. **Use HTTPS only**: Both Vercel and Railway provide SSL by default
4. **Enable deployment protection**: Require approval for production deployments (optional)
5. **Monitor logs**: Regularly review logs for suspicious activity

## Troubleshooting

### Frontend Issues

**"Failed to fetch" errors:**
- Check that `VITE_API_URL` is correctly set
- Verify backend CORS configuration includes frontend URL
- Check browser console for specific error messages

**Blank page after deployment:**
- Check Vercel build logs for errors
- Verify all routes are configured correctly
- Check browser console for errors

### Backend Issues

**Database connection errors:**
- Verify `DATABASE_URL` is set correctly
- Check Railway database service is running
- Review connection pool settings

**OAuth errors:**
- Verify redirect URIs match deployed backend URL
- Check OAuth credentials are set correctly
- Ensure OAuth apps are not in development/testing mode

## CI/CD Pipeline

The complete deployment flow:

1. **Developer** creates a branch and makes changes
2. **Developer** opens a pull request
3. **Vercel** automatically deploys a preview
4. **Team** reviews code and preview deployment
5. **Developer** merges PR to `main`
6. **Vercel** deploys frontend to production
7. **Railway** deploys backend to production
8. **Team** verifies production deployment

## Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Railway Documentation](https://docs.railway.app)
- [Vite Deployment Guide](https://vitejs.dev/guide/static-deploy.html)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

## Support

For deployment issues:
1. Check this documentation first
2. Review platform-specific documentation (Vercel/Railway)
3. Contact the development team
4. Create an issue in the GitHub repository

---

**Last Updated**: January 2026  
**Maintained By**: J2WFFDev Team
