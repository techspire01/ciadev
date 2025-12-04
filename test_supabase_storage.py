#!/usr/bin/env python
"""
Test script to verify Supabase Storage is properly configured
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')
django.setup()

from django.core.files.storage import storages
from django.conf import settings

print("=" * 60)
print("SUPABASE STORAGE CONFIGURATION TEST")
print("=" * 60)

# Check settings
print("\n1. Checking Django Settings:")
if hasattr(settings, 'STORAGES'):
    print(f"   STORAGES configured: {bool(settings.STORAGES)}")
    print(f"   STORAGES['default']: {settings.STORAGES.get('default', {})}")
print(f"   SUPABASE_URL: {'SET' if settings.SUPABASE_URL else 'NOT SET'}")
print(f"   SUPABASE_BUCKET: {settings.SUPABASE_BUCKET}")

# Check storage backend
print("\n2. Checking Storage Backend:")
try:
    default_storage = storages["default"]
    storage_type = type(default_storage).__name__
    storage_module = type(default_storage).__module__
    print(f"   Backend class: {storage_type}")
    print(f"   Backend module: {storage_module}")
    
    if "SupabaseStorage" in storage_type:
        print("\n✅ SUCCESS! Supabase Storage is active!")
    else:
        print(f"\n⚠️ WARNING: Using {storage_type} instead of SupabaseStorage")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ Error loading storage: {e}")
    sys.exit(1)

# Check Supabase client initialization
print("\n3. Checking Supabase Client:")
try:
    from supastorage.storage import SupabaseStorage
    storage = SupabaseStorage()
    print(f"   ✅ SupabaseStorage initialized successfully")
    print(f"   Bucket: {storage._bucket}")
except Exception as e:
    print(f"   ❌ Error initializing Supabase: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("All tests passed! Supabase Storage is ready to use.")
print("=" * 60)
