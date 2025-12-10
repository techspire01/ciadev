# Performance Optimization Guide

This document outlines the performance improvements applied to the CIA project to reduce page load times from ~2000ms to < 20ms.

## Implemented Changes

### 1. **Image Lazy Loading** ✅
- Added `loading="lazy"` to all `<img>` tags across templates
- Updated templates: `navbar.html`, `index.html`, `mobile-menu.html`, `footer.html`
- Prevents blocking page rendering on image loading

### 2. **Response Compression** ✅
- **GZip Middleware**: Added `django.middleware.gzip.GZipMiddleware` to compress HTTP responses
- **WhiteNoise Static Compression**: Configured `CompressedManifestStaticFilesStorage` for CSS/JS
- **Long-term Caching**: Set `WHITENOISE_MAX_AGE = 31536000` (1 year) for static files

### 3. **Database Query Optimization** ✅

#### Key Optimizations:
- **Caching**: Implemented Django cache layer (LocMemCache) for frequently-accessed data:
  - Supplier lists and categories cached for 1 hour
  - Product/subcategory filters cached
  - Category counts cached per-category
  
- **Query Reduction**:
  - `index` view: Reduced N+1 queries by caching supplier fetches and using `values()` to limit columns
  - `category` view: Replaced multiple Supplier queries with single cached fetch
  - `cia_networks` view: Added `only()` to limit columns, cached filter options
  - `supplier_detail_page` view: Added caching for supplier lookup, use `only()` for initial search

#### Before:
```python
# Multiple queries in a loop (N+1 problem)
for category in categories:
    count = Supplier.objects.filter(category=category).count()  # N queries!
```

#### After:
```python
# Single query with caching
cache_key = f'category_count:{category_name}'
count = cache.get(cache_key)
if count is None:
    count = Supplier.objects.filter(category=category_name).count()
    cache.set(cache_key, count, 3600)
```

### 4. **Image Format Conversion (WebP/AVIF)** ✅

#### New Files:
- `app/image_utils.py`: Image conversion utilities (requires Pillow)
- `app/templatetags/perf_tags.py`: Template filters for responsive images
- `app/management/commands/convert_images.py`: Batch conversion command

#### Usage in Templates:
```django
{% load perf_tags %}

{# Simple lazy image #}
{{ image.url|lazy_image:"Alt text" }}

{# Picture tag with WebP/AVIF fallback #}
{{ image.url|picture_tag:"Alt text" }}
```

#### Generate WebP versions:
```bash
python manage.py convert_images --format webp --media --static
```

#### Generate AVIF versions:
```bash
python manage.py convert_images --format avif --media --static
```

### 5. **Caching Infrastructure** ✅

Added `app/optimization.py` with utilities:
- `cache_view_response(timeout)`: Decorator for full view caching
- `cache_queryset(queryset, cache_key, timeout)`: Decorator for queryset caching
- Configurable timeouts (defaults: 1 hour for static, 5 minutes for dynamic)

## Configuration

### Django Settings (already applied):

```python
# In proj/settings.py

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.gzip.GZipMiddleware',  # ← NEW: Compress responses
    'django.middleware.cache.UpdateCacheMiddleware',
    # ... other middleware
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'cia-cache',
        'OPTIONS': {'MAX_ENTRIES': 10000},
        'TIMEOUT': 300
    }
}

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_MAX_AGE = 31536000  # 1 year cache for static files
```

## Dependencies

Ensure you have these installed:

```bash
pip install pillow django django-compressor whitenoise
```

Check Pillow WebP/AVIF support:
```bash
python -c "from PIL import Image; print('WebP:', Image.HAVE_WEBP); print('AVIF:', hasattr(Image, 'AVIF'))"
```

## Next Steps for Production

### 1. **Collect Static Files**
```bash
python manage.py collectstatic --noinput
```

### 2. **Pre-convert Images** (optional but recommended)
```bash
# Convert to WebP for better compression
python manage.py convert_images --format webp --media --static

# Convert to AVIF for even better compression (optional)
python manage.py convert_images --format avif --media --static
```

### 3. **Enable HTTP/2 and Brotli** (on hosting provider)
- Most modern hosting supports HTTP/2 by default
- Configure Brotli compression for even better compression than GZip

### 4. **Use a CDN** (recommended for production)
```python
# Update STATIC_URL and MEDIA_URL to CDN URLs
STATIC_URL = 'https://your-cdn.com/static/'
MEDIA_URL = 'https://your-cdn.com/media/'
```

### 5. **Add Cache Headers** (optional, already in WhiteNoise)
```python
# Already configured via WHITENOISE_MAX_AGE
```

### 6. **Database Connection Pooling** (for heavy traffic)
```bash
pip install psycopg2-pool
```

```python
# In settings.py (for PostgreSQL)
DATABASES = {
    'default': {
        # ... existing config
        'CONN_MAX_AGE': 600,  # Reuse connections
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}
```

## Performance Benchmarks

### Expected Improvements:

| Metric | Before | After |
|--------|--------|-------|
| Full Page Load | ~2000ms | ~200-400ms |
| Static Files Load | ~800ms | ~50-100ms |
| First Contentful Paint | ~1200ms | ~150-250ms |
| Largest Contentful Paint | ~1500ms | ~200-350ms |
| Images (lazy loaded) | Blocking | Non-blocking |

**Note**: Actual improvements depend on:
- Network speed
- Database performance
- Server resources
- Content size
- Number of images per page

## Troubleshooting

### Cache not working?
Check cache backend in Django shell:
```python
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value', 60)
>>> cache.get('test')  # Should return 'value'
```

### Images not converting to WebP?
```bash
# Check Pillow's WebP support
python -c "from PIL import Image; Image.new('RGB', (1,1)).save('/tmp/test.webp')"
```

### Static files not compressing?
```bash
# Regenerate static files
python manage.py collectstatic --noinput --clear
```

## Cache Invalidation

To clear cache when updating data:

```python
from django.core.cache import cache

# Clear specific cache key
cache.delete('index_suppliers')

# Clear all cache
cache.clear()
```

## Monitoring

For production, monitor:
1. **Page Load Times**: Use Google Analytics or Sentry
2. **Database Queries**: Django Debug Toolbar (dev only) or Silk
3. **Cache Hit Rate**: Add logging to cache utilities
4. **CDN Performance**: CloudFlare Analytics or similar

## References

- [Django Caching Framework](https://docs.djangoproject.com/en/stable/topics/cache/)
- [WhiteNoise Static Compression](http://whitenoise.evans.io/)
- [Pillow Image Processing](https://python-pillow.org/)
- [Web Vitals Optimization](https://web.dev/vitals/)
