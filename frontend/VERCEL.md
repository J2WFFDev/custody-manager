# Vercel Deployment

This frontend is configured for automatic deployment to Vercel.

## Quick Start

1. **Import Project to Vercel**
   - Visit [vercel.com/new](https://vercel.com/new)
   - Import `J2WFFDev/custody-manager`
   - Vercel auto-detects Vite configuration

2. **Set Environment Variables**
   - Go to Project Settings → Environment Variables
   - Add: `VITE_API_URL` = `https://your-backend.railway.app`

3. **Deploy**
   - Production: Merge to `main` branch
   - Preview: Open a pull request

## Configuration

The project uses:
- **Framework**: Vite (auto-detected)
- **Build Command**: `cd frontend && npm run build` (set in root `vercel.json`)
- **Output Directory**: `frontend/dist` (set in root `vercel.json`)
- **Install Command**: `cd frontend && npm install` (set in root `vercel.json`)

All configuration is in `/vercel.json` at the repository root.

## Environment Variables

Required environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `https://api.yourdomain.com` |

> **Note**: All environment variables for Vite must be prefixed with `VITE_` to be exposed to the browser.

## Local Testing

Test the production build locally:

```bash
npm run build
npm run preview
```

The preview server runs at `http://localhost:4173`

## Preview Deployments

Every pull request automatically gets a unique preview URL:
- Format: `https://custody-manager-git-[branch]-[team].vercel.app`
- Vercel bot comments on PR with deployment URL
- Preview deployments use the same environment variables as production

## Troubleshooting

**Build fails:**
- Check build logs in Vercel dashboard
- Ensure all dependencies are in `package.json`
- Verify TypeScript compilation succeeds locally

**Environment variables not working:**
- Ensure they're prefixed with `VITE_`
- Variables must be set in Vercel project settings
- Redeploy after adding new variables

**CORS errors:**
- Verify backend allows requests from Vercel domain
- Check `VITE_API_URL` is set correctly

## More Information

See the main [DEPLOYMENT.md](../DEPLOYMENT.md) for complete deployment documentation.
