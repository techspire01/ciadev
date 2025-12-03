# Deployment Instructions for CIA Portal Security Implementation

## Overview
This guide covers deploying the security improvements to your production environment.

## Pre-Deployment Checklist

### 1. Backup Everything
```bash
# Backup database
pg_dump your_database > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup media files
tar -czf media_backup_$(date +%Y%m%d_%H%M%S).tar.gz /path/to/media/
```

### 2. Test on Staging
```bash
# Deploy code to staging environment
git checkout mac
git pull origin mac

# Verify checks pass
python manage.py check
```

### 3. Update Django Settings for Production

**proj/settings.py** - Update these:
```python
# 1. Disable debug
DEBUG = False

# 2. Set secure secret key (generate a new one!)
SECRET_KEY = 'generate-a-new-secure-random-key-here'

# 3. Set allowed hosts
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# 4. Enable HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# 5. If behind proxy (Nginx, load balancer)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

## Deployment Steps

### Step 1: Pull Latest Code
```bash
cd /your/project/path
git pull origin mac
```

### Step 2: Create/Verify Logs Directory
```bash
mkdir -p logs/
chmod 755 logs/
```

### Step 3: Install Dependencies
```bash
source .vevn/bin/activate
pip install -r requirements.txt  # if updated
pip install django-ratelimit  # ensure installed
```

### Step 4: Run Migrations
```bash
python manage.py migrate
# Expected output: Applying app.0023_supplier_user... OK
```

### Step 5: Sync Supplier Data
```bash
# First, dry-run to see what will happen
python manage.py sync_supplier_users --dry-run

# Then run for real
python manage.py sync_supplier_users

# Monitor the output for matched suppliers
```

### Step 6: Collect Static Files
```bash
python manage.py collectstatic --no-input
```

### Step 7: Test Protected Media Endpoint
```bash
# Start development server temporarily
python manage.py runserver

# In another terminal, test:
curl -I http://localhost:8000/protected-media/applications/resumes/test.pdf
# Should get 404 or 403 (not 500)
```

### Step 8: Restart Web Server
```bash
# For Gunicorn
sudo systemctl restart gunicorn

# For uWSGI
sudo systemctl restart uwsgi

# For Nginx (if using)
sudo systemctl reload nginx
```

### Step 9: Verify Deployment
```bash
# Check health
curl https://yourdomain.com/health/

# Verify HTTPS redirect
curl -I http://yourdomain.com/
# Should see 301 redirect to https://

# Check logs
tail -f logs/security.log
```

## Post-Deployment Monitoring

### First 24 Hours
1. **Monitor Security Log**
   ```bash
   tail -f logs/security.log
   ```
   Look for errors like:
   - "Permission denied" - Check supplier.user field populated
   - "File not found" - Verify media paths
   - Multiple 403s - Check access control

2. **Test With Real Users**
   - Have 2-3 suppliers test login
   - Verify resume downloads work
   - Check rate-limiting active

3. **Monitor System Health**
   - CPU/Memory usage
   - Database connection pool
   - Disk space for logs

### First 72 Hours
1. Review error logs
2. Verify data sync results
3. Check for any access denied patterns
4. Confirm pagination works with large applicant lists

## Troubleshooting

### Issue: "Supplier lookup failed" in logs
```bash
# Check how many suppliers have user set
python manage.py shell
>>> from app.models import Supplier
>>> Supplier.objects.filter(user__isnull=False).count()
# Should increase after sync_supplier_users
```

### Issue: Rate-limiting not working
```bash
# Verify package installed
python manage.py shell
>>> from ratelimit.decorators import ratelimit
# Should not raise ImportError
```

### Issue: Protected media returns 404
```bash
# Verify MEDIA_ROOT setting
python manage.py shell
>>> from django.conf import settings
>>> print(settings.MEDIA_ROOT)
# Check files exist there
>>> import os
>>> os.listdir(settings.MEDIA_ROOT)
```

### Issue: HTTPS not redirecting
```bash
# Check setting
python manage.py shell
>>> from django.conf import settings
>>> print(settings.SECURE_SSL_REDIRECT)
# Should be True

# If behind proxy, verify:
>>> print(settings.SECURE_PROXY_SSL_HEADER)
# Should be ('HTTP_X_FORWARDED_PROTO', 'https')
```

## Rollback Plan

If issues occur:

### Rollback Code
```bash
git revert HEAD~1  # or specific commit
git push production
```

### Rollback Database
```bash
# If migration caused issues:
python manage.py migrate app 0022  # revert to before 0023
```

### Restore Media
```bash
tar -xzf media_backup_YYYYMMDD_HHMMSS.tar.gz -C /
```

## Performance Tuning

### Monitor Query Performance
```bash
# In settings.py for staging:
LOGGING = {
    ...
    'django.db.backends': {
        'level': 'DEBUG',  # Log SQL queries
    }
}

# View slow queries
grep "0.[5-9]" logs/debug.log  # Queries taking >500ms
```

### Optimize File Storage
Current: Django file serving (protected_media view)
- Good for small deployments (<100 requests/day)
- Recommended for >1000 requests/day: S3 with presigned URLs

### Cache Configuration
Already configured in settings.py:
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'cia-cache',
    }
}
```
For production, upgrade to Redis:
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

## Monitoring Long-Term

### Weekly
```bash
# Check log file sizes
du -sh logs/

# Rotate if too large
python manage.py --command to rotate (implement custom command)

# Review error patterns
grep ERROR logs/errors.log | wc -l  # Should be low
```

### Monthly
```bash
# Check database size
SELECT pg_size_pretty(pg_database_size('your_db'));

# Verify backup completeness
# Clean old backups
```

## Security Best Practices Going Forward

1. **Never commit secrets**: Use environment variables
2. **Rotate SECRET_KEY**: Annually
3. **Review access logs**: Monthly
4. **Update dependencies**: Quarterly
5. **Security headers**: Enable all in production
6. **SSL/TLS**: Use TLS 1.2+ only
7. **Rate limiting**: Monitor and adjust based on usage

## Support

For deployment issues, check:
1. logs/security.log - Security events
2. logs/errors.log - System errors
3. `python manage.py check --deploy` - Deployment checklist

---

**Last Updated**: 2 December 2025  
**Version**: 1.0  
**Status**: Ready for Production
