# Fix for ConnectError at / - DNS Resolution Issue

## Problem
The homepage was crashing with: `[Errno 8] nodename nor servname provided, or not known`

This error occurred when the template tried to render `{{ announcement.image.url }}`. The `.url` property on the FileField calls the storage backend's `url()` method, which attempts to connect to Supabase to generate a signed URL. If Supabase is unreachable, it crashes.

## Root Cause
In `supastorage/storage.py`, the `url()` method was making a network request to Supabase without any error handling. When the network or Supabase was unavailable, it would crash the entire page rendering.

## Solution Implemented

### 1. Enhanced Storage Backend (supastorage/storage.py)
Added error handling to the `url()` method:
- Wrapped Supabase connection in try-except block
- If signed URL generation fails, logs warning and falls back to public URL
- Page renders successfully even if Supabase is temporarily unreachable

```python
def url(self, name):
    try:
        res = self._client.storage.from_(self._bucket).create_signed_url(name, expires_in=expires)
        # ... return signed URL
    except Exception as e:
        logger.warning(f"Could not generate signed URL for {name}: {str(e)}. Using public URL fallback.")
        return f"{settings.SUPABASE_URL}/storage/v1/object/public/{self._bucket}/{name}"
```

### 2. Pre-generate Image URLs in View (app/views.py)
Modified the `index()` view to:
- Pre-generate the announcement image URL with error handling
- Pass pre-generated URL to template instead of letting template call `.url`
- If URL generation fails, pass None to template
- Template shows image only if URL available

```python
announcement_image_url = None
if announcement and announcement.image:
    try:
        announcement_image_url = announcement.image.url
    except Exception as e:
        logger.warning(f"Could not generate announcement image URL: {str(e)}")
```

### 3. Updated Template (app/templates/index.html)
Changed template to use pre-generated URL:
- From: `{% if announcement.image %}`
- To: `{% if announcement_image_url %}`
- From: `<img src="{{ announcement.image.url }}">`
- To: `<img src="{{ announcement_image_url }}">`

## Benefits
✅ Homepage loads even if Supabase temporarily unreachable
✅ Error handling gracefully degrades to public URLs
✅ Logged warnings for debugging connection issues
✅ No user-facing error pages
✅ Application resilient to network issues

## Testing
1. Restart Django server: `python manage.py runserver`
2. Navigate to http://localhost:8000/
3. Homepage should load successfully
4. Announcement image displays if Supabase is available
5. Homepage still loads if Supabase is down (graceful degradation)

## Files Changed
- `supastorage/storage.py` - Added error handling to url() method
- `app/views.py` - Pre-generate announcement image URL with error handling
- `app/templates/index.html` - Use pre-generated URL instead of calling .url in template

---

The application now handles Supabase connectivity issues gracefully without crashing.
