# Deployment Guide - Render

This guide explains how to deploy your Django Medical Connect application to Render.

## Prerequisites

- GitHub account with your repository
- Render account (https://render.com)
- Your project pushed to GitHub

## Step 1: Push Your Project to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

## Step 2: Create a New Web Service on Render

1. Go to https://dashboard.render.com
2. Click **New +** → **Web Service**
3. Select **Deploy an existing GitHub repository**
4. Authorize Render to access your GitHub
5. Select your medical_connect repository
6. Fill in the details:
   - **Name**: medical-connect (or your preferred name)
   - **Environment**: Python 3
   - **Region**: Choose closest to your users
   - **Branch**: main
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn medical_connect.wsgi`

## Step 3: Configure Environment Variables

In the Render dashboard, go to your service and add these environment variables:

```
SECRET_KEY=your-secret-key-here-generate-a-new-one
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
ENV=production
```

### Generate a new SECRET_KEY

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

## Step 4: Configure PostgreSQL Database (Optional)

If you want to use PostgreSQL instead of SQLite:

1. In Render dashboard, click **New +** → **PostgreSQL**
2. Fill in database details
3. Copy the connection string (DATABASE_URL)
4. In your Web Service environment variables, add:
   ```
   DATABASE_URL=your-postgres-url
   ```

The app will automatically use PostgreSQL when DATABASE_URL is set.

## Step 5: Finalize Deployment

1. Click **Create Web Service**
2. Render will automatically start building and deploying
3. Check the **Logs** tab to monitor deployment

## Important Files Created for Deployment

- **Procfile** - Specifies how to run your app and run migrations
- **runtime.txt** - Specifies Python version
- **.gitignore** - Excludes sensitive files from version control
- **requirements.txt** - Updated with `dj-database-url`
- **settings.py** - Updated with environment variable support

## First Deployment Troubleshooting

### Issue: "ModuleNotFoundError"
- Check that all dependencies are in `requirements.txt`
- Run: `pip freeze > requirements.txt` locally and commit

### Issue: "Secret key not found"
- Make sure `SECRET_KEY` environment variable is set

### Issue: "Static files not loading"
- WhiteNoise middleware is already configured
- Run: `python manage.py collectstatic` locally to test

### Issue: "Database connection error"
- If using PostgreSQL, verify DATABASE_URL is correct
- Check that migrations were applied (included in Procfile)

## Post-Deployment

1. Create a superuser for admin:
   ```bash
   render exec python manage.py createsuperuser
   ```

2. Test your application at: `https://your-app-name.onrender.com`

3. Access admin panel at: `https://your-app-name.onrender.com/admin`

## Updating Your App

1. Make changes locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Your message"
   git push
   ```
3. Render automatically redeploys on push to main branch

## Important Security Notes

- ✅ Never hardcode sensitive data (SECRET_KEY, database credentials)
- ✅ Always use environment variables
- ✅ `.gitignore` prevents committing `.env` files
- ✅ Use strong SECRET_KEY (generated, not predictable)
- ✅ Set DEBUG=False in production

## Support

For issues, check:
- Render Logs: Your service dashboard → Logs tab
- Django Documentation: https://docs.djangoproject.com/
- Render Documentation: https://render.com/docs