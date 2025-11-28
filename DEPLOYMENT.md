# Vercel Deployment Guide for NutrifyKE

## Overview
This guide will walk you through deploying NutrifyKE to Vercel for public access.

## Prerequisites
- Vercel account ([Sign up here](https://vercel.com/signup))
- Google Gemini API key
- Git repository (optional but recommended)

---

## Deployment Steps

### Step 1: Install Vercel CLI (Optional)
```bash
npm install -g vercel
```

### Step 2: Prepare Your Project

All configuration files have been created:
- ✅ `vercel.json` - Vercel configuration
- ✅ `.env.production` - Production environment placeholder
- ✅ `main.py` - Updated for production mode
- ✅ `requirements.txt` - Includes gunicorn

### Step 3: Deploy to Vercel

#### Option A: Deploy via Vercel Dashboard (Recommended)

1. **Go to [Vercel Dashboard](https://vercel.com/dashboard)**

2. **Click "Add New Project"**

3. **Import Your Repository**
   - If using Git: Connect your GitHub/GitLab/Bitbucket account and select the NutrifyKE repository
   - If not using Git: Use "Deploy from local directory" option

4. **Configure Project Settings**
   - **Framework Preset**: Other
   - **Root Directory**: `./` (leave as default)
   - **Build Command**: Leave empty
   - **Output Directory**: Leave empty

5. **Add Environment Variables**
   - Click "Environment Variables"
   - Add the following:
     - **Name**: `GEMINI_API_KEY`
     - **Value**: Your Google Gemini API key
     - **Environment**: Production, Preview, Development (select all)

6. **Click "Deploy"**
   - Vercel will build and deploy your application
   - Wait for deployment to complete (usually 1-2 minutes)

7. **Get Your Live URL**
   - Once deployed, you'll receive a URL like: `https://nutrifyke.vercel.app`
   - Share this URL with users!

#### Option B: Deploy via CLI

1. **Login to Vercel**
   ```bash
   vercel login
   ```

2. **Navigate to Project Directory**
   ```bash
   cd C:\Users\Churchill\Desktop\NutrifyKE
   ```

3. **Set Environment Variable**
   ```bash
   vercel env add GEMINI_API_KEY
   ```
   - When prompted, paste your API key
   - Select: Production, Preview, Development

4. **Deploy**
   ```bash
   vercel --prod
   ```

5. **Follow Prompts**
   - Set up and deploy: Yes
   - Which scope: Select your account
   - Link to existing project: No
   - Project name: nutrifyke (or your preferred name)
   - Directory: `./`
   - Override settings: No

---

## Post-Deployment

### Verify Deployment

1. **Visit Your URL**
   - Open the Vercel-provided URL in your browser

2. **Test Features**
   - ✅ Page loads correctly
   - ✅ Food dropdown populates
   - ✅ Manual entry works
   - ✅ AI scanning works (most important!)

3. **Check Logs**
   - Go to Vercel Dashboard → Your Project → Logs
   - Monitor for any errors

### Common Issues & Solutions

#### Issue 1: "GEMINI_API_KEY not found"
**Solution**: 
- Go to Vercel Dashboard → Project Settings → Environment Variables
- Ensure `GEMINI_API_KEY` is set for Production environment
- Redeploy the project

#### Issue 2: AI Scanning Not Working
**Solution**:
- Check browser console for errors
- Verify API key is valid and has quota remaining
- Check Vercel function logs for backend errors

#### Issue 3: 404 Errors on Routes
**Solution**:
- Verify `vercel.json` is in the root directory
- Ensure routes configuration is correct
- Redeploy

#### Issue 4: Slow Response Times
**Solution**:
- Vercel serverless functions have cold starts (first request may be slow)
- Subsequent requests will be faster
- Consider upgrading to Vercel Pro for better performance

---

## Custom Domain (Optional)

### Add Your Own Domain

1. **Go to Project Settings → Domains**

2. **Add Domain**
   - Enter your domain (e.g., `nutrifyke.com`)
   - Follow DNS configuration instructions

3. **Update DNS Records**
   - Add the provided DNS records to your domain registrar
   - Wait for propagation (can take up to 48 hours)

---

## Updating Your Deployment

### Method 1: Automatic (Git-based)
If you connected a Git repository:
- Push changes to your repository
- Vercel automatically redeploys

### Method 2: Manual (CLI)
```bash
cd C:\Users\Churchill\Desktop\NutrifyKE
vercel --prod
```

### Method 3: Manual (Dashboard)
- Zip your project folder
- Upload via Vercel Dashboard → Deployments → Upload

---

## Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key for AI food recognition | Yes |

---

## Performance Optimization

### Tips for Better Performance

1. **Enable Caching**
   - Vercel automatically caches static assets
   - Food data is loaded once per serverless function instance

2. **Monitor Usage**
   - Check Vercel Analytics for traffic patterns
   - Monitor Gemini API quota usage

3. **Optimize Images**
   - Users upload images, but they're processed server-side
   - Consider adding image compression if needed

---

## Security Best Practices

### Implemented Security Features

✅ **API Key Protection**
- API key stored as environment variable
- Never exposed to frontend

✅ **HTTPS**
- Vercel provides automatic HTTPS

✅ **CORS**
- Flask CORS configured for security

### Additional Recommendations

- **Rate Limiting**: Consider adding rate limiting to prevent abuse
- **Input Validation**: Already implemented in backend
- **Error Handling**: Comprehensive error handling in place

---

## Monitoring & Analytics

### Vercel Analytics
- Go to Project → Analytics
- View page views, unique visitors, and performance metrics

### Function Logs
- Go to Project → Logs
- Monitor backend errors and API calls

### Gemini API Usage
- Check Google AI Studio for API quota usage
- Monitor costs if using paid tier

---

## Scaling Considerations

### Free Tier Limits (Vercel)
- 100 GB bandwidth/month
- 100 hours serverless function execution/month
- Unlimited deployments

### If You Exceed Limits
- Upgrade to Vercel Pro ($20/month)
- Optimize function execution time
- Consider caching strategies

---

## Troubleshooting Commands

### View Deployment Logs
```bash
vercel logs
```

### List Deployments
```bash
vercel ls
```

### Remove Deployment
```bash
vercel remove [deployment-url]
```

### Check Environment Variables
```bash
vercel env ls
```

---

## Support Resources

- **Vercel Documentation**: https://vercel.com/docs
- **Vercel Support**: https://vercel.com/support
- **Google Gemini API**: https://ai.google.dev/docs

---

## Next Steps After Deployment

1. **Share Your App**
   - Share the Vercel URL with friends, family, or on social media
   - Get feedback from real users

2. **Monitor Performance**
   - Check Vercel Analytics daily
   - Monitor error logs

3. **Iterate**
   - Add more Kenyan foods to the database
   - Improve AI prompts based on user feedback
   - Add new features

4. **Marketing**
   - Create social media posts
   - Share on Kenyan tech communities
   - Consider submitting to app directories

---

## Congratulations! 🎉

Your NutrifyKE app is now live and accessible to anyone in the world!

**Your deployment URL**: `https://[your-project-name].vercel.app`

---

**Made with ❤️ for Kenya** 🇰🇪
