# Zomato Django Application - Railway.app Deployment

## Deployment Instructions for Railway.app

### Prerequisites
- GitHub account with your code pushed
- Railway.app account (sign up at https://railway.app)

### Step-by-step Deployment

#### 1. Prepare Your Code
```bash
# Make sure you have all deployment files:
# - requirements.txt
# - Procfile
# - runtime.txt
# - .env.example
# - .gitignore
```

#### 2. Environment Variables Setup
Create environment variables in Railway.app dashboard:

1. Go to your Railway project
2. Click on "Variables" tab
3. Add the following variables:

```
SECRET_KEY=your-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=*.railway.app,localhost,127.0.0.1
DATABASE_URL=postgresql://user:password@host:port/database
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
RAZORPAY_KEY_ID=your-razorpay-key
RAZORPAY_SECRET=your-razorpay-secret
```

#### 3. Database Setup (PostgreSQL on Railway)
Railway will automatically provide a DATABASE_URL when you add a PostgreSQL service.

1. Click "Add Service" in Railway
2. Select "PostgreSQL"
3. The DATABASE_URL will be automatically added to variables

#### 4. Connect GitHub Repository
1. In Railway, click "Create New Project"
2. Select "Deploy from GitHub repo"
3. Select your GitHub repository
4. Railway will automatically detect the Procfile and deploy

#### 5. Run Migrations
After deployment:
```bash
# The release command in Procfile will run migrations automatically
# But you can also run manually via Railway shell:
railway run python manage.py migrate
railway run python manage.py createsuperuser
```

#### 6. Collect Static Files
Railway will automatically collect static files when WhiteNoise is configured.

### Important Notes

1. **Sensitive Data**: Never commit `.env` file. Use railway environment variables instead.

2. **Static Files**: WhiteNoise middleware serves static files in production.

3. **Database**: 
   - Development: SQLite (db.sqlite3)
   - Production: PostgreSQL (via Railway)

4. **Media Files**: Configure external storage (AWS S3 or similar) for production.

5. **Security**: The following are enabled in production:
   - HTTPS/SSL redirect
   - Secure cookies
   - HSTS headers
   - XSS protection

### Common Commands

```bash
# Check logs
railway logs

# Run shell
railway shell

# Run migrations
railway run python manage.py migrate

# Create superuser
railway run python manage.py createsuperuser

# Collect static files
railway run python manage.py collectstatic --noinput
```

### Troubleshooting

**Error: ModuleNotFoundError**
- Make sure all dependencies are in requirements.txt
- Re-deploy after updating requirements.txt

**Database Connection Error**
- Verify DATABASE_URL is correctly set
- Check PostgreSQL service is running in Railway

**Static Files Not Loading**
- Run: `railway run python manage.py collectstatic --noinput`
- Check STATIC_ROOT path is correct

**Media Files Not Uploading**
- Configure AWS S3 or another storage service
- Update MEDIA_URL and MEDIA_ROOT settings

### Support
For more help, visit: https://docs.railway.app/
