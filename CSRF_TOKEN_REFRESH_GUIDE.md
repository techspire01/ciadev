# CSRF Token Refresh Configuration - Complete Guide

## ✅ Your Current Configuration Status

### 1. **Middleware Order** ✓ CORRECT
Your `settings.py` has the correct middleware order:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'proj.middleware.DynamicCSRFOriginMiddleware',  # Custom, runs early
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  # ✓ Session first
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # ✓ CSRF after session
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'proj.middleware.SecurityLoggingMiddleware',
    'proj.middleware.CacheControlMiddleware',
]
```

**Key points:**
- ✓ `SessionMiddleware` comes BEFORE `CsrfViewMiddleware`
- ✓ `CsrfViewMiddleware` is present
- ✓ Order allows proper CSRF token generation and validation

---

### 2. **Cookie Settings** ✓ CORRECT
Your `settings.py` has proper cookie configuration:

```python
SESSION_COOKIE_SECURE = False  # ✓ Correct for development
CSRF_COOKIE_SECURE = False     # ✓ Correct for development
CSRF_COOKIE_HTTPONLY = False   # ✓ Allows JS to read token
CSRF_COOKIE_SAMESITE = 'Lax'   # ✓ Allows same-site requests
```

**What these do:**
- `SECURE=False`: Uses HTTP cookies (development only, set to True for HTTPS in production)
- `HTTPONLY=False`: JavaScript can read the CSRF token (needed for AJAX)
- `SAMESITE='Lax'`: Browser sends cookies on same-site POST requests

---

### 3. **Template** ✓ CORRECT
Your `app/templates/login.html` has the correct tag:

```html
<form class="space-y-6" action="{% url 'login' %}" method="POST">
    {% csrf_token %}  <!-- ✓ Correct - always generates fresh token -->
```

**Why this matters:**
- `{% csrf_token %}` is a Django template tag that:
  1. Reads the current session
  2. Generates a fresh token specific to that session
  3. Inserts it as a hidden form field
- ✓ It updates every page load/refresh automatically
- ✓ It's NOT hard-coded, so it changes with the session

---

## 🔧 How CSRF Token Refresh Works

### Page Load Flow:
```
1. Browser requests /login/
   ↓
2. Django SessionMiddleware creates sessionid cookie
   (e.g., sessionid=abc123xyz789)
   ↓
3. Django CsrfViewMiddleware creates csrftoken cookie
   (e.g., csrftoken=def456xyz789)
   ↓
4. Template renders {% csrf_token %}
   → Generates hidden input with matching token value
   → Token value derived from session
   ↓
5. Browser receives cookies AND HTML form with token
   ↓
6. User refreshes page
   ↓
7. Session cookie stays same (unless logged in/out)
   BUT token can be rotated and re-generated
   ↓
8. New page load = {% csrf_token %} tag re-evaluates
   → May generate new token if Django rotates it
   → Always matches current session
```

---

## 📋 CSRF Token Not Refreshing? - Checklist

If your token appears identical after refresh, check:

### ✓ Check 1: Is the page actually refreshing?
```
Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
- Clears browser cache
- Forces full page reload
- Ensures Django processes request again
```

### ✓ Check 2: Are cookies being set?
Open DevTools (F12) → Application/Storage → Cookies:

Should see:
- `sessionid` - Session identifier
- `csrftoken` - CSRF token value

**If missing:**
- ✗ Cookies are disabled in browser
- ✗ Private/Incognito mode blocking cookies
- ✗ Browser extension blocking cookies

**Fix:**
```javascript
// In browser console (F12), check:
console.log(document.cookie);

// Should show something like:
// "sessionid=abc123xyz789; csrftoken=def456xyz789"
```

### ✓ Check 3: Is {% csrf_token %} in form?
Search in page source (Ctrl+U) for:
```html
<input type="hidden" name="csrfmiddlewaretoken" value="...">
```

**If NOT found:**
- ✗ Template doesn't have `{% csrf_token %}`
- ✗ Token tag is commented out
- ✗ Using wrong template file

**Your status:** ✓ Token tag is present

### ✓ Check 4: Is CsrfViewMiddleware enabled?
```python
# Check in settings.py
'django.middleware.csrf.CsrfViewMiddleware' in MIDDLEWARE
```

**Your status:** ✓ Middleware is enabled

### ✓ Check 5: Is CSRF_USE_SESSIONS enabled?
If you want tokens tied strictly to sessions:
```python
CSRF_USE_SESSIONS = True  # Optional
```

By default (False), tokens can be refreshed independently.

---

## 🚀 For Modern Frontend (AJAX/Fetch/React)

If using JavaScript to submit forms, add a CSRF endpoint:

### Step 1: Add to `app/views.py`
```python
from django.middleware.csrf import get_token
from django.http import JsonResponse

def get_csrf_token(request):
    """Return fresh CSRF token for AJAX requests"""
    return JsonResponse({
        'csrfToken': get_token(request)
    })
```

### Step 2: Add to `app/urls.py`
```python
from .views import get_csrf_token

urlpatterns = [
    ...
    path('api/csrf-token/', get_csrf_token, name='csrf_token'),
]
```

### Step 3: Use in Frontend
```javascript
// Get fresh token before AJAX
fetch('/api/csrf-token/')
    .then(res => res.json())
    .then(data => {
        csrftoken = data.csrfToken;
        
        // Now send form with fresh token
        fetch('/login/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: 'user@example.com',
                password: 'password123'
            })
        });
    });
```

---

## 🔐 Production Deployment Checklist

When deploying to production (Render, Vercel, etc.), update these settings:

```python
# For HTTPS (production)
DEBUG = False
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True  # ← Change from False
CSRF_COOKIE_SECURE = True     # ← Change from False
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Update allowed hosts
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Set trusted origins
CSRF_TRUSTED_ORIGINS = [
    'https://yourdomain.com',
    'https://www.yourdomain.com',
]
```

---

## 🧪 Test CSRF Token Behavior

### Test Script: `test_csrf_token.py`
```python
from django.test import Client
from django.contrib.auth import get_user_model
from bs4 import BeautifulSoup
import re

User = get_user_model()

def test_csrf_token_refresh():
    """Test that CSRF token is present and updates"""
    client = Client()
    
    # First request
    response1 = client.get('/login/')
    soup1 = BeautifulSoup(response1.content, 'html.parser')
    token1 = soup1.find('input', {'name': 'csrfmiddlewaretoken'})
    
    if token1:
        token_value1 = token1.get('value', '')
        print(f"✓ First request token: {token_value1[:20]}...")
    else:
        print("✗ No CSRF token found in first request!")
        return False
    
    # Second request (simulates refresh)
    response2 = client.get('/login/')
    soup2 = BeautifulSoup(response2.content, 'html.parser')
    token2 = soup2.find('input', {'name': 'csrfmiddlewaretoken'})
    
    if token2:
        token_value2 = token2.get('value', '')
        print(f"✓ Second request token: {token_value2[:20]}...")
        
        if token_value1 == token_value2:
            print("ℹ Tokens match (this is normal - tokens stay same within session)")
        else:
            print("ℹ Tokens differ (token was rotated)")
        
        return True
    else:
        print("✗ No CSRF token found in second request!")
        return False

# Run test
if __name__ == '__main__':
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')
    django.setup()
    
    test_csrf_token_refresh()
```

Run with:
```bash
python test_csrf_token.py
```

---

## 📚 Related Settings Reference

```python
# CSRF Configuration
CSRF_COOKIE_SECURE = False      # True for HTTPS
CSRF_COOKIE_HTTPONLY = False    # False to allow JS access
CSRF_COOKIE_SAMESITE = 'Lax'    # or 'Strict'
CSRF_COOKIE_AGE = 31449600      # 1 year
CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'  # Header name for token
CSRF_FAILURE_VIEW = None        # Custom 403 handler
CSRF_TRUSTED_ORIGINS = [...]    # Allowed origins
CSRF_USE_SESSIONS = False       # Store token in session
CSRF_COOKIE_MASKED = True       # Mask token in cookie

# Session Configuration  
SESSION_COOKIE_SECURE = False   # True for HTTPS
SESSION_COOKIE_HTTPONLY = True  # Prevent JS access to sessionid
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 1209600    # 2 weeks
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
```

---

## Summary

✅ **Your configuration is correct for development**

Your setup properly handles CSRF token refresh because:

1. ✓ Middleware order: Session → CSRF
2. ✓ Template: Uses `{% csrf_token %}` tag
3. ✓ Cookies: Properly configured for development
4. ✓ No hard-coded token values

**Token behavior:**
- Tokens are generated fresh for each request
- They're tied to the session (sessionid)
- Within a session, token may stay same or be rotated (both normal)
- On new session (new browser/logout), completely new token

**If still having issues:**
1. Hard refresh (Ctrl+Shift+R)
2. Clear cookies (DevTools → Storage → Clear All)
3. Check console for JavaScript errors
4. Check Django logs for CSRF failures
