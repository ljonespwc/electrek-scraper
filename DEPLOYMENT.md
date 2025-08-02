# Deploying to Vercel

This Flask app is configured for deployment to Vercel's serverless platform.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **Supabase Project**: You need a Supabase project with your data

## Quick Deployment Steps

### 1. Connect to Vercel

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your GitHub repository
3. Vercel will auto-detect it as a Python project

### 2. Configure Environment Variables

In your Vercel project dashboard, add these environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `SUPABASE_URL` | Your Supabase project URL | `https://your-project.supabase.co` |
| `SUPABASE_KEY` | Your Supabase anon public key | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |
| `FLASK_SECRET_KEY` | Secret key for Flask sessions | `your-random-secret-key` |

**To add environment variables in Vercel:**
1. Go to your project dashboard
2. Click "Settings" tab
3. Click "Environment Variables"
4. Add each variable above

### 3. Deploy

1. Click "Deploy" in Vercel
2. Wait for build to complete (2-3 minutes)
3. Your app will be live at `https://your-project-name.vercel.app`

## Local Development

To run locally with the new optimized dependencies:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables (create .env file)
echo "SUPABASE_URL=your_supabase_url" > .env
echo "SUPABASE_KEY=your_supabase_key" >> .env
echo "FLASK_SECRET_KEY=your_secret_key" >> .env

# Run the app
python app.py
```

## Project Structure for Vercel

```
├── api/
│   └── index.py          # Vercel serverless entry point
├── electrek_scraper/     # Your Flask app
├── static/               # Static files (CSS, JS)
├── templates/            # Jinja2 templates
├── vercel.json          # Vercel configuration
├── requirements.txt     # Optimized dependencies
└── .vercelignore       # Files to ignore during deployment
```

## Custom Domain (Optional)

1. In your Vercel project dashboard
2. Go to "Settings" > "Domains"
3. Add your custom domain
4. Update DNS records as instructed

## Monitoring

- **Analytics**: Available in Vercel dashboard
- **Logs**: View function logs in "Functions" tab
- **Performance**: Monitor in "Analytics" tab

## Troubleshooting

### Common Issues

1. **Build Fails**: Check that all dependencies in `requirements.txt` are available
2. **Function Timeout**: Increase timeout in `vercel.json` (max 30s on free plan)
3. **Memory Issues**: Optimize imports and reduce heavy operations
4. **Static Files**: Ensure static files are properly configured in `vercel.json`

### Environment Variables Not Working

1. Make sure variables are set in Vercel dashboard
2. Check spelling and case sensitivity
3. Redeploy after adding new variables

### Database Connection Issues

1. Verify Supabase URL and key are correct
2. Check Supabase project is active
3. Ensure RLS policies allow your queries

## Files Added for Vercel

- `vercel.json`: Configuration for Vercel platform
- `api/index.py`: Serverless function entry point
- `.vercelignore`: Excludes unnecessary files from deployment
- `requirements.txt`: Optimized dependencies (original backed up as `requirements-full.txt`)

## Performance Optimization

The app has been optimized for serverless deployment:

- ✅ Removed heavy ML libraries (scikit-learn, scipy)
- ✅ Streamlined dependencies
- ✅ Configured proper routing for static files
- ✅ Set reasonable function timeouts

Your Tesla analysis app should deploy smoothly and perform well on Vercel's global infrastructure!