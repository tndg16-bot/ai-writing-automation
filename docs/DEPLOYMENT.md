# Production Deployment Guide

## Deploying AI Writing Automation to Production

This guide covers deploying to **Vercel (frontend)** and **Railway (backend)**.

---

## Prerequisites

- GitHub account
- Vercel account (sign up at https://vercel.com)
- Railway account (sign up at https://railway.app)
- Required API keys:
  - `OPENAI_API_KEY`
  - Optional: Google API keys for Docs integration

---

## Part 1: Backend Deployment (Railway)

### Step 1: Create Railway Project

1. Go to https://railway.app
2. Click "New Project"
3. Click "Deploy from GitHub repo"
4. Select `tndg16-bot/ai-writing-automation`
5. Railway will detect Python automatically

### Step 2: Configure Build Settings

1. Select the detected service
2. Configure root directory: `.`
3. Build command:
   ```bash
   pip install -e ".[dev]"
   ```
4. Start command:
   ```bash
   python -m uvicorn api.main:app --host 0.0.0.0 --port $PORT
   ```

### Step 3: Add Environment Variables

Add these environment variables in Railway:

| Variable | Value | Required |
|----------|--------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |
| `DATABASE_URL` | `sqlite:///./data/history.db` | No (default) |
| `PORT` | `8000` | No (auto) |

To add variables:
1. Go to your service in Railway
2. Click "Variables" tab
3. Add each variable

### Step 4: Deploy

1. Click "Deploy" button
2. Wait for deployment to complete
3. Railway will provide a URL like: `https://your-app-name.railway.app`

### Step 5: Get Railway URL

1. Note your Railway URL
2. Example: `https://ai-writing-api.railway.app`

---

## Part 2: Frontend Deployment (Vercel)

### Step 1: Install Vercel CLI

```bash
npm i -g vercel
```

### Step 2: Deploy to Vercel

From the project root:

```bash
cd frontend
vercel
```

Follow the prompts:
1. Link to existing project or create new
2. Set project name (e.g., `ai-writing-automation`)
3. Override settings? **No** (use defaults)

### Step 3: Configure Environment Variables

After initial deployment, configure the API URL:

1. Go to https://vercel.com
2. Select your project
3. Go to **Settings** → **Environment Variables**
4. Add variable:
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: Your Railway URL (e.g., `https://your-api.railway.app`)
   - Environments: Production, Preview, Development

### Step 4: Redeploy

1. Go to **Deployments** in Vercel
2. Click the three dots (...) on latest deployment
3. Click "Redeploy"
4. Wait for redeployment to complete

### Step 5: Get Vercel URL

Vercel will provide a URL like: `https://your-project-name.vercel.app`

---

## Part 3: Update CORS (if needed)

If you experience CORS issues, update `api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-project-name.vercel.app",  # Your Vercel domain
        "http://localhost:3000",  # For local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then push changes and redeploy Railway.

---

## Part 4: Verify Deployment

### Test API (Railway)

```bash
curl https://your-api.railway.app/health
```

Expected response:
```json
{"status": "ok"}
```

### Test Frontend (Vercel)

1. Visit your Vercel URL
2. Check dashboard loads
3. Try creating a generation

### Check Connectivity

1. Open browser DevTools (F12)
2. Go to Network tab
3. Try creating content
4. Verify API requests succeed (status 200)

---

## Part 5: Custom Domain (Optional)

### Vercel Custom Domain

1. Go to Vercel project **Settings**
2. Go to **Domains**
3. Add your domain (e.g., `ai-writing.yourdomain.com`)
4. Follow DNS instructions

### Railway Custom Domain

1. Go to Railway service **Settings**
2. Go to **Networking**
3. Click "Generate Domain" or "Custom Domain"
4. Follow DNS instructions

---

## Troubleshooting

### Issue: CORS Error

**Symptom**: Browser shows CORS error in console

**Solution**:
1. Verify `NEXT_PUBLIC_API_URL` in Vercel
2. Update CORS origins in `api/main.py`
3. Redeploy Railway

### Issue: API Not Found

**Symptom**: 404 error when calling API

**Solution**:
1. Check Railway service is running
2. Verify PORT is set correctly
3. Check Railway logs for errors

### Issue: Build Fails

**Symptom**: Vercel or Railway build fails

**Solution**:
1. Check build logs
2. Verify all dependencies are in requirements.txt
3. Ensure Python/Node versions are compatible

### Issue: WebSocket Not Connecting

**Symptom**: Progress page doesn't show updates

**Solution**:
1. Check Railway supports WebSockets (enabled by default)
2. Verify WebSocket URL is correct
3. Check browser console for errors

---

## Monitoring

### Vercel

- **Deployments**: https://vercel.com/dashboard
- **Analytics**: https://vercel.com/analytics
- **Logs**: https://vercel.com/dashboard → Your Project → Logs

### Railway

- **Deployments**: https://railway.app/dashboard
- **Metrics**: Railway service → Metrics
- **Logs**: Railway service → Logs

---

## Cost Estimate

### Vercel (Free Tier)
- 100GB bandwidth/month
- Unlimited deployments
- Edge network
- **Cost**: $0/month

### Railway (Free Tier)
- 500 hours/month
- 512MB RAM
- Shared CPU
- **Cost**: $0/month (plus $5/month for Hobby tier)

Total estimated cost: **$0-$5/month**

---

## Next Steps

1. Deploy both services
2. Test end-to-end functionality
3. Set up monitoring/alerts
4. Configure custom domains (optional)
5. Set up backups (recommended)

---

## Support

- **Vercel Docs**: https://vercel.com/docs
- **Railway Docs**: https://docs.railway.app
- **GitHub Issues**: https://github.com/tndg16-bot/ai-writing-automation/issues
