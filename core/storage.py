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
        self._init_client()

    def _init_client(self):
        if self._client:
            return
        if not getattr(settings, "SUPABASE_SERVICE_KEY", None) or not getattr(settings, "SUPABASE_URL", None):
            raise RuntimeError("SUPABASE_SERVICE_KEY and SUPABASE_URL must be set in settings.")
        self._client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

    def _save(self, name, content):
        """
        name: path inside bucket, e.g. 'resumes/user_1/resume.pdf'
        content: file-like object (django UploadedFile)
        Returns the name stored.
        """
        self._init_client()
        # Ensure content is bytes
        content.seek(0)
        data = content.read()
        # If content is a Django UploadedFile (InMemoryUploadedFile / TemporaryUploadedFile)
        if hasattr(data, "read"):
            # shouldn't usually happen; ensure bytes
            data = data.read()

        # Use upsert True so overwrites replace
        resp = self._client.storage.from_(self._bucket).upload(name, data, file_options={"upsert": True})
        # Supabase returns metadata on success, otherwise raises
        return name

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
        """
        self._init_client()
        # expires_in in seconds (1 hour default), make configurable via settings
        expires = getattr(settings, "SUPABASE_SIGNED_URL_EXPIRES", 3600)
        res = self._client.storage.from_(self._bucket).create_signed_url(name, expires_in=expires)
        # res is like {"signedURL": "..."} or may raise
        # safety: guard if response shape different
        if isinstance(res, dict):
            # supabase-py returns {'signedURL': 'https://...'}
            signed = res.get("signedURL") or res.get("signed_url") or res.get("signed_url")
            if signed:
                return signed
        # fallback: public URL (only works if bucket public)
        return f"{settings.SUPABASE_URL}/storage/v1/object/public/{self._bucket}/{name}"

    def delete(self, name):
        self._init_client()
        try:
            # supabase remove takes list of file paths
            self._client.storage.from_(self._bucket).remove([name])
            return True
        except Exception:
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
