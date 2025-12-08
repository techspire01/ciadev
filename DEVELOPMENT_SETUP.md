# Development Setup - CIA Project

## Overview
This project has been converted to **development mode**. The following changes have been made to enable local development.

## Changes Made

### 1. Django Settings (`proj/settings.py`)

#### Debug Mode
- **DEBUG = True** - Enabled for development to show detailed error pages and reload on code changes
- Error pages will display full traceback for debugging

#### Allowed Hosts
- Updated to: `['*', 'localhost', '127.0.0.1']`
- Allows development on localhost without host validation errors

#### Security Headers - DISABLED for Development
The following security features have been **DISABLED** for development:

- ❌ `SECURE_SSL_REDIRECT = False` - HTTP connections allowed (no HTTPS requirement)
- ❌ `SESSION_COOKIE_SECURE = False` - Cookies work over HTTP
- ❌ `CSRF_COOKIE_SECURE = False` - No HTTPS requirement for CSRF
- ❌ `SECURE_HSTS_SECONDS = 0` - HSTS disabled
- ❌ `SECURE_BROWSER_XSS_FILTER = False` - XSS filter disabled
- ❌ `SECURE_CONTENT_TYPE_NOSNIFF = False` - Content-Type sniffing allowed

**⚠️ IMPORTANT**: These settings are intentionally relaxed for development. They **MUST** be re-enabled for production deployment.

#### Email Backend
- Changed to: `EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"`
- Emails will be printed to console instead of being sent
- Useful for testing email functionality without SMTP configuration

### 2. Environment Variables (`.env`)

```dotenv
DEBUG=True                    # Development mode enabled
DJANGO_SECRET_KEY=...        # Safe development key
```

## Starting Development Server

### Install Dependencies
```bash
pip install -r requir.txt
```

### Run Migrations (if needed)
```bash
python manage.py migrate
```

### Start Development Server
```bash
python manage.py runserver
```

The server will start at: **http://localhost:8000**

### Features
- Hot reload on code changes
- Detailed error pages with tracebacks
- Console output for debugging
- Static file serving automatically

## Using Supabase in Development

The project is configured to use **Supabase** for:
- Database (PostgreSQL)
- File Storage (via supastorage backend)

The Supabase credentials in `.env` are configured and active. To use a local SQLite database instead:

```python
# In proj/settings.py, replace:
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv("DATABASE_URL")
    )
}

# With:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

## Development-Only Apps

You can optionally add Django Debug Toolbar for development:

```bash
pip install django-debug-toolbar
```

Then add to `INSTALLED_APPS` in `settings.py`:
```python
'debug_toolbar',
```

## Important Notes

⚠️ **Security Reminder**: This development configuration is **NOT suitable for production**. Before deploying:

1. Set `DEBUG = False`
2. Change `DJANGO_SECRET_KEY` to a secure random string
3. Update `ALLOWED_HOSTS` with actual domain names
4. Re-enable all security headers (SECURE_* settings)
5. Configure proper email backend with SMTP credentials
6. Use environment-specific settings files or environment variables

## Common Development Tasks

### Create Superuser
```bash
python manage.py createsuperuser
```

### Access Django Admin
Visit: http://localhost:8000/admin

### Shell Access
```bash
python manage.py shell
```

### Run Tests
```bash
python manage.py test
```

## Troubleshooting

### Port Already in Use
```bash
python manage.py runserver 8001
```

### Clear Cache
```bash
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
```

### Fresh Database Reset
```bash
python manage.py migrate zero  # Revert all migrations
python manage.py migrate       # Reapply all migrations
```

---

**Status**: ✅ Project converted to development mode
**Date**: December 8, 2025
