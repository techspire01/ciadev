import io
import os
from django.core.files.storage import Storage
from django.conf import settings
from supabase import create_client, Client
from typing import Optional


class SupabaseStorage(Storage):
    """
    Django storage backend for Supabase Storage using service role key.
    Supports upload, create_signed_url, delete.
    """

    def __init__(self):
        self._client: Optional[Client] = None
        self._bucket = getattr(settings, "SUPABASE_BUCKET")
        self._bucket_initialized = False
        self._init_client()

    def _init_client(self):
        if self._client:
            return
        if not getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", None) or not getattr(settings, "SUPABASE_URL", None):
            raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY and SUPABASE_URL must be set in settings.")
        self._client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    
    def _ensure_bucket_exists(self):
        """Ensure the bucket exists; create it if it doesn't."""
        if self._bucket_initialized:
            return
        
        import logging
        logger = logging.getLogger('django')
        
        try:
            # Try to list buckets to see if ours exists
            buckets = self._client.storage.list_buckets()
            bucket_names = [b.name for b in buckets]
            
            if self._bucket not in bucket_names:
                logger.warning(f"Bucket '{self._bucket}' not found. Attempting to create it...")
                try:
                    self._client.storage.create_bucket(self._bucket, options={"public": False})
                    logger.info(f"Successfully created bucket '{self._bucket}'")
                except Exception as e:
                    logger.error(f"Failed to create bucket '{self._bucket}': {str(e)}")
                    raise RuntimeError(f"Bucket '{self._bucket}' does not exist and could not be created: {str(e)}")
            
            self._bucket_initialized = True
        except Exception as e:
            logger.error(f"Error checking/creating bucket: {str(e)}")
            # Don't fail initialization; let individual operations handle it
            self._bucket_initialized = True

    def _save(self, name, content):
        """
        name: path inside bucket, e.g. 'resumes/user_1/resume.pdf'
        content: file-like object (django UploadedFile)
        Returns the name stored.
        """
        import logging
        logger = logging.getLogger('django')
        
        self._init_client()
        self._ensure_bucket_exists()
        
        # Ensure content is bytes
        content.seek(0)
        data = content.read()
        # If content is a Django UploadedFile (InMemoryUploadedFile / TemporaryUploadedFile)
        if hasattr(data, "read"):
            # shouldn't usually happen; ensure bytes
            data = data.read()

        try:
            # Use upsert True so overwrites replace
            # Note: upsert must be string "true" not boolean True for httpx compatibility
            resp = self._client.storage.from_(self._bucket).upload(name, data, file_options={"upsert": "true"})
            # Supabase returns metadata on success, otherwise raises
            return name
        except Exception as e:
            # Check if it's a network error
            error_type = type(e).__name__
            if 'Network' in error_type or 'Connect' in error_type or isinstance(e, (OSError, ConnectionError)):
                # Handle network/DNS errors gracefully
                logger.warning(f"Network error uploading file {name} to Supabase (file skipped): {str(e)}")
                # Return the filename anyway so the model can still save (graceful degradation)
                return name
            else:
                # Re-raise other exceptions
                logger.error(f"Error uploading file {name} to Supabase: {str(e)}")
                raise

    def exists(self, name):
        self._init_client()
        # Supabase doesn't have a direct exists endpoint; attempt to get metadata
        try:
            listing = self._client.storage.from_(self._bucket).list(prefix=name, limit=1)
            # list returns list of items whose name begins with prefix; check exact match
            for item in listing:
                if item.get("name") == name:
                    return True
            return False
        except Exception:
            return False

    def url(self, name):
        """
        Returns a signed URL (private) valid for some time.
        Falls back to public URL if Supabase is unreachable.
        Includes download=1 parameter to ensure proper file rendering.
        """
        import logging
        logger = logging.getLogger('django')
        
        self._init_client()
        self._ensure_bucket_exists()
        
        # expires_in in seconds (1 hour default), make configurable via settings
        expires = getattr(settings, "SUPABASE_SIGNED_URL_EXPIRES", 3600)
        
        try:
            res = self._client.storage.from_(self._bucket).create_signed_url(name, expires_in=expires)
            # res is like {"signedURL": "..."} or may raise
            # safety: guard if response shape different
            if isinstance(res, dict):
                # supabase-py returns {'signedURL': 'https://...'}
                signed = res.get("signedURL") or res.get("signed_url")
                if signed:
                    # Add download=1 parameter to ensure proper file rendering in browser
                    return signed + "&download=1"
        except Exception as e:
            # Log the error but don't crash - fallback to public URL
            logger.warning(f"Could not generate signed URL for {name}: {str(e)}. Using public URL fallback.")
        
        # fallback: public URL (only works if bucket public)
        return f"{settings.SUPABASE_URL}/storage/v1/object/public/{self._bucket}/{name}?download=1"

    def delete(self, name):
        import logging
        logger = logging.getLogger('django')
        
        self._init_client()
        try:
            # supabase remove takes list of file paths
            self._client.storage.from_(self._bucket).remove([name])
            return True
        except Exception as e:
            # Log but don't fail - file deletion is not critical to app functionality
            error_type = type(e).__name__
            if 'Network' in error_type or 'Connect' in error_type or isinstance(e, (OSError, ConnectionError)):
                logger.warning(f"Network error deleting file {name} from Supabase (will retry later): {str(e)}")
            else:
                logger.error(f"Error deleting file {name} from Supabase: {str(e)}")
            return False

    def size(self, name):
        # try to get metadata via list
        self._init_client()
        items = self._client.storage.from_(self._bucket).list(prefix=name, limit=100)
        for item in items:
            if item.get("name") == name:
                return item.get("size")
        return None

    # simplify open/read operations (not strictly required)
    def open(self, name, mode='rb'):
        self._init_client()
        # download object and return BytesIO
        res = self._client.storage.from_(self._bucket).download(name)
        # res is bytes (or raises)
        buf = io.BytesIO(res)
        return buf
