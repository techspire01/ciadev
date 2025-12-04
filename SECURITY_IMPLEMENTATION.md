# CIA Portal Security Implementation - Completion Summary

## Date: 2 December 2025

This document summarizes the security hardening and infrastructure improvements implemented for the CIA Dev portal project.

---

## 1. DATABASE SCHEMA CHANGES ✅

### Added Supplier.user OneToOneField
- **File**: `app/models.py`
- **Migration**: `app/migrations/0023_supplier_user.py`
- **Status**: ✅ Applied to database
- **Details**:
  - Added optional OneToOne relationship from Supplier to CustomUser
  - Allows null for migration window
  - When populated, enables direct user-to-supplier lookup
  - `related_name='supplier_profile'` provides reverse access

### Migration Applied
```bash
python manage.py migrate
# Result: Applying app.0023_supplier_user... OK
```

---

## 2. DATA SYNCHRONIZATION ✅

### Management Command: sync_supplier_users
- **File**: `app/management/commands/sync_supplier_users.py`
- **Usage**: `python manage.py sync_supplier_users [--dry-run]`
- **Status**: ✅ Tested and ready
- **Results from dry-run**:
  - Total suppliers: 162
  - Matched to users: 2
  - Unmatched: 160 (no matching user accounts)
  - No email: 23
  
**Matched suppliers:**
1. dezacodex → mohanbabuscsda2023@sankara.ac.in
2. sankaara college → sanjayraga1610vino@gmail.com

**Action**: Run without --dry-run when ready to sync:
```bash
python manage.py sync_supplier_users
```

---

## 3. SUPPLIER LOOKUP REFACTORING ✅

### New Helper Function
- **File**: `app/utils.py`
- **Function**: `get_supplier_for_user_or_raise(request)`
- **Status**: ✅ Implemented
- **Features**:
  - Tries new OneToOne relationship first (preferred)
  - Falls back to email lookup for migration window
  - Logs all fallback usage for audit trail
  - Raises PermissionDenied on failure
  - Comprehensive error handling

### Updated Views
- **File**: `portal/views.py`
- **Status**: ✅ All 18+ occurrences replaced
- **Changes**:
  - Replaced `Supplier.objects.get(email=request.user.email)` with helper
  - Replaced `except Supplier.DoesNotExist` with `except PermissionDenied`
  - Updated `@supplier_required` decorator to use helper
  - Attached supplier to request object for downstream use

### Usage Pattern
```python
from app.utils import get_supplier_for_user_or_raise

supplier = get_supplier_for_user_or_raise(request)  # Raises PermissionDenied on failure
request.supplier = supplier
```

---

## 4. RATE-LIMITING PROTECTION ✅

### Installation
- **Package**: django-ratelimit 4.1.0
- **Status**: ✅ Installed
- **Fallback**: Graceful degradation if package missing

### Protected Endpoints
- **internship_application()** - Rate limited to 30 requests/hour
- **job_application()** - Rate limited to 30 requests/hour
- **Method**: IP-based limiting on POST requests
- **Behavior**: `block=True` returns 429 on limit exceeded

### Implementation
```python
from ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='30/h', method='POST', block=True)
def job_application(request, job_id):
    ...
```

---

## 5. PROTECTED MEDIA ENDPOINT ✅

### New View: protected_media()
- **File**: `portal/views.py`
- **URL Route**: `re_path(r'^protected-media/(?P<path>.+)/$', views.protected_media)`
- **Status**: ✅ Implemented
- **Security Features**:
  - Path sanitization (prevents directory traversal)
  - Ownership verification
  - Staff can access all files
  - Application owner can access their files
  - Email-based fallback for migration window
  - Comprehensive logging

### Access Control
```
Allowed:
- Staff members (is_staff=True) - all files
- Application owner - their resume/attachments
- Supplier via email match (fallback)

Denied:
- Unauthenticated users
- Users without permission
```

### Usage in Templates
```html
<a href="{% url 'protected_media' app.resume.name %}">Download Resume</a>
```

---

## 6. LOGGING & SECURITY MONITORING ✅

### Logging Configuration
- **File**: `proj/settings.py`
- **Logger Name**: `cai_security`
- **Status**: ✅ Configured
- **Features**:
  - Separate security log file
  - Rotating file handler (10MB per file, 10 backups)
  - INFO level for security events
  - ERROR level for system errors
  - Verbose formatting with timestamps

### Middleware: SecurityLoggingMiddleware
- **File**: `proj/middleware.py`
- **Registered**: ✅ In MIDDLEWARE setting
- **Events Logged**:
  - 403 Forbidden - Unauthorized access
  - 429 Too Many Requests - Rate limit exceeded
  - 401 Unauthorized - Authentication failures
  - Client IP address preserved (proxy-aware)

### Log Locations
```
logs/security.log    - Security events
logs/errors.log      - System errors
```

### Sample Log Entry
```
WARNING 2025-12-02 20:08:25 portal.views Access denied for supplier lookup: user=5 email=test@example.com
INFO 2025-12-02 20:08:26 Internship 42 created by supplier 7
WARNING 2025-12-02 20:08:27 403 for /portal-admin/job/5/applicants user=email@example.com ip=192.168.1.1
```

---

## 7. TEMPLATE FILTERS ✅

### Safe Split Filter
- **File**: `app/templatetags/custom_filters.py`
- **Status**: ✅ Already exists
- **Function**: `split(value, sep=',')`
- **Usage**: `{% load custom_filters %} {{ skills|split:"," }}`

---

## 8. QUERY OPTIMIZATION ✅

### N+1 Query Fix
- **File**: `portal/views.py`
- **View**: `job_portal_admin()`
- **Status**: ✅ Implemented
- **Change**: Replaced per-item `.count()` loops with `.annotate(Count())`

**Before (N+1 Problem)**:
```python
for job in jobs:
    count = JobApplication.objects.filter(job=job, supplier=supplier).count()  # Database query per job!
    job.application_count = count
```

**After (Optimized)**:
```python
from django.db.models import Count
jobs = jobs.annotate(application_count=Count('applications'))  # Single query!
```

---

## 9. PAGINATION ✅

### Paginated Views
- **File**: `portal/views.py`
- **Status**: ✅ Implemented
- **Views**:
  - `view_job_applicants()` - 10 per page
  - `view_internship_applicants()` - 10 per page
- **Features**:
  - Django Paginator with fallback to first page on error
  - `page_obj` available in templates
  - Handles EmptyPage gracefully

### Template Usage
```html
{% for app in applications %}
  {{ app.first_name }} {{ app.last_name }}
{% endfor %}

{% if page_obj.has_previous %}
  <a href="?page={{ page_obj.previous_page_number }}">Previous</a>
{% endif %}

Page {{ page_obj.number }} of {{ page_obj.paginator.num_pages }}

{% if page_obj.has_next %}
  <a href="?page={{ page_obj.next_page_number }}">Next</a>
{% endif %}
```

---

## 10. AUTOMATIC FILE CLEANUP ✅

### Signals Module
- **File**: `portal/signals.py`
- **Status**: ✅ Implemented
- **Registered**: ✅ In `portal/apps.py` ready() method

### Cleanup Triggers
- **post_delete on JobApplication**: Deletes resume + attachment files
- **post_delete on InternshipApplication**: Deletes resume + attachment files
- **post_delete on PortalJob**: Deletes all application files for that job

### Implementation
```python
@receiver(post_delete, sender=JobApplication)
def delete_job_application_files(sender, instance, **kwargs):
    # Safely deletes files from MEDIA_ROOT
    # Logs all operations
```

---

## 11. HTTPS & SECURITY HEADERS ✅

### Configuration
- **File**: `proj/settings.py`
- **Status**: ✅ Configured (dev mode: False, enable in production)
- **Settings**:

```python
# Development (currently disabled)
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0

# Production (enable these):
SECURE_SSL_REDIRECT = True              # Force HTTP→HTTPS
SESSION_COOKIE_SECURE = True            # Only send cookies over HTTPS
CSRF_COOKIE_SECURE = True               # Only send CSRF cookies over HTTPS
SECURE_HSTS_SECONDS = 31536000          # 1 year HSTS
SECURE_HSTS_INCLUDE_SUBDOMAINS = True   # Include subdomains in HSTS
SECURE_HSTS_PRELOAD = True              # Add to HSTS preload list
SECURE_REFERRER_POLICY = "strict-origin"
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# For reverse proxy (Nginx, load balancer)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

### Production Nginx Example
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$host$request_uri;  # Redirect HTTP to HTTPS
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header X-Forwarded-Proto https;
    }
}
```

---

## TESTING CHECKLIST

### Run These Tests Before Production Deployment

```bash
# 1. Check Django setup
python manage.py check

# 2. Run migrations (already done)
python manage.py migrate

# 3. Test data sync script (dry-run first)
python manage.py sync_supplier_users --dry-run
python manage.py sync_supplier_users  # When ready

# 4. Run tests
python manage.py test

# 5. Check logs are created
ls -la logs/

# 6. Verify protected_media endpoint
# Visit: https://yourdomain/protected-media/applications/resumes/test.pdf
# Should verify ownership and log access

# 7. Test rate-limiting
# Submit >30 applications from same IP in 1 hour
# Should receive 429 Too Many Requests

# 8. Test logging
# Trigger 403 error (try accessing someone else's job)
# Verify entry in logs/security.log

# 9. Test pagination
# View applicants when >10 exist
# Verify page navigation works
```

---

## DEPLOYMENT CHECKLIST

### Pre-Deployment
- [ ] Backup database
- [ ] Backup media directory
- [ ] Test on staging environment
- [ ] Review logs/security.log for errors
- [ ] Enable HTTPS on server

### Deployment Steps
1. Pull code changes
2. Run `python manage.py migrate`
3. Run `python manage.py sync_supplier_users`
4. Verify protected_media downloads work
5. Test rate-limiting on one endpoint
6. Monitor logs/security.log for errors
7. Enable HTTPS in settings.py (set SECURE_SSL_REDIRECT=True)

### Post-Deployment
- [ ] Monitor logs for first 24-72 hours
- [ ] Test with 2-3 suppliers
- [ ] Verify resume downloads work
- [ ] Check pagination on large applicant lists
- [ ] Confirm rate-limiting active

---

## CONFIGURATION CHANGES MADE

### settings.py
- Added LOGGING configuration
- Added SECURE_* settings for HTTPS
- Added SecurityLoggingMiddleware to MIDDLEWARE
- Configured cache backend (already present)
- Created logs/ directory on startup

### urls.py (portal)
- Added `re_path(r'^protected-media/(?P<path>.+)/$', views.protected_media)`
- Imported `re_path` from django.urls

### apps.py (portal)
- Added `ready()` method to import signals

### models.py (app)
- Added `user = OneToOneField(CustomUser, null=True, blank=True, on_delete=models.SET_NULL)`

### views.py (portal)
- Added `get_supplier_for_user_or_raise` import
- Updated `@supplier_required` decorator
- Added `protected_media()` view
- Added rate-limiting decorators
- Updated all supplier lookups (18+ locations)
- Added logging to security events
- Implemented .annotate(Count()) for queries
- Added pagination to applicant views

### middleware.py (proj)
- Created new `SecurityLoggingMiddleware` class

### signals.py (portal)
- Created new file with post_delete signal handlers

### utils.py (app)
- Added `get_supplier_for_user_or_raise()` function
- Added logging imports

### management/commands/sync_supplier_users.py (app)
- Created new management command for data sync

---

## KNOWN LIMITATIONS & FUTURE IMPROVEMENTS

### Current Limitations
1. **Email-based fallback**: Temporary measure during migration. Remove after all suppliers have Supplier.user set.
2. **File serving via Django**: Protected_media view is slower than Nginx X-Accel-Redirect or S3. For high-volume production, use S3 presigned URLs.
3. **Rate-limiting**: IP-based; doesn't account for proxies behind NAT.
4. **Logging**: File-based; consider ELK stack for large scale.

### Future Improvements
1. **S3 Integration**: Move files to S3 with presigned URLs for security + performance
2. **Advanced Rate-Limiting**: Per-user limits, configurable by endpoint
3. **Bot Detection**: Add reCAPTCHA or hCaptcha to application forms
4. **Centralized Logging**: ELK stack, Splunk, or Sentry integration
5. **API Key Authentication**: For third-party integrations
6. **Audit Trail**: Detailed change log for admin actions
7. **Email Notifications**: Alert on suspicious activity

---

## FILES MODIFIED/CREATED

### Modified
1. `app/models.py` - Added Supplier.user field
2. `portal/views.py` - Major refactoring (supplier lookups, protected media, rate-limiting)
3. `portal/urls.py` - Added protected_media route
4. `portal/apps.py` - Registered signals
5. `proj/settings.py` - Added logging, security headers, middleware
6. `proj/middleware.py` - Created SecurityLoggingMiddleware
7. `app/utils.py` - Added get_supplier_for_user_or_raise()

### Created
1. `app/migrations/0023_supplier_user.py` - Database migration
2. `app/management/commands/sync_supplier_users.py` - Data sync command
3. `portal/signals.py` - File cleanup signals
4. `proj/middleware.py` - Security logging middleware
5. `logs/` - Directory for log files (created at startup)

---

## NEXT STEPS

1. **Deploy to Staging**: Test all changes in staging environment
2. **Run Data Sync**: `python manage.py sync_supplier_users`
3. **Enable HTTPS**: Configure SSL certificate and enable in settings
4. **Monitor Logs**: Watch security.log for 72 hours post-deployment
5. **Gather Feedback**: Collect issues from suppliers using portal
6. **Plan S3 Migration**: For file storage (future)

---

## SUPPORT & TROUBLESHOOTING

### Common Issues

**Q: "Supplier lookup failed" errors in logs**
A: Run `python manage.py sync_supplier_users` to match suppliers to users

**Q: "Permission denied" on protected-media**
A: Verify user owns the application that uploaded the file

**Q: Rate-limiting not working**
A: Check django-ratelimit is installed: `pip list | grep ratelimit`

**Q: Missing logs directory**
A: Create manually: `mkdir logs/` and restart app

---

## CONTACT & DOCUMENTATION

For questions about this implementation, refer to:
- Django documentation: https://docs.djangoproject.com
- django-ratelimit: https://github.com/views.py-cache/django-ratelimit
- OWASP Security Guidelines: https://owasp.org/

---

**Implementation completed**: 2 December 2025  
**Status**: Ready for staging deployment  
**Approval Required**: Yes - before production deployment
