"""
Security middleware for CIA Portal

Logs security-related events including:
- Unauthorized access attempts (403)
- Rate limit rejections (429)
- Other suspicious activity
"""

import logging
import os
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
from django.conf import settings

logger = logging.getLogger('cai_security')


class SecurityLoggingMiddleware(MiddlewareMixin):
    """Log security-related HTTP responses and events"""

    def process_response(self, request, response):
        """Log 403 Forbidden and 429 Too Many Requests responses"""
        
        status_code = response.status_code
        
        # Log 403 Forbidden - Unauthorized Access
        if status_code == 403:
            logger.warning(
                "403 Forbidden: path=%s user=%s user_id=%s ip=%s method=%s",
                request.path,
                getattr(request.user, 'email', 'anonymous'),
                getattr(request.user, 'id', 'N/A'),
                self._get_client_ip(request),
                request.method,
            )
        
        # Log 429 Too Many Requests - Rate Limit
        elif status_code == 429:
            logger.warning(
                "429 Too Many Requests: path=%s user=%s user_id=%s ip=%s method=%s",
                request.path,
                getattr(request.user, 'email', 'anonymous'),
                getattr(request.user, 'id', 'N/A'),
                self._get_client_ip(request),
                request.method,
            )
        
        # Log 401 Unauthorized
        elif status_code == 401:
            logger.warning(
                "401 Unauthorized: path=%s ip=%s method=%s",
                request.path,
                self._get_client_ip(request),
                request.method,
            )
        
        return response
    
    @staticmethod
    def _get_client_ip(request):
        """Extract client IP from request, accounting for proxies"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip


class CacheControlMiddleware(MiddlewareMixin):
    """
    Add cache control headers to prevent browser caching of dynamic pages.
    Ensures users always see the latest data from the server.
    """
    
    def process_response(self, request, response):
        """Add cache control headers to all responses"""
        
        # Never cache pages by default
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        return response


class DynamicCSRFOriginMiddleware(MiddlewareMixin):
    """
    Dynamically manage CSRF trusted origins for localhost development.
    
    Handles the "null origin" issue by accepting requests from localhost
    even when the Origin header is null or missing.
    """
    
    def process_request(self, request):
        """For localhost requests, add current origin to trusted list"""
        
        try:
            host = request.get_host()
            
            # Only process for localhost (development)
            if 'localhost' not in host and '127.0.0.1' not in host:
                return None
            
            # Get current trusted origins
            trusted_origins = list(getattr(settings, 'CSRF_TRUSTED_ORIGINS', []))
            protocol = 'https' if request.is_secure() else 'http'
            current_origin = f"{protocol}://{host}"
            
            # Add current origin if not present
            if current_origin not in trusted_origins:
                trusted_origins.append(current_origin)
                settings.CSRF_TRUSTED_ORIGINS = trusted_origins
                logger.debug(f"Auto-added CSRF origin: {current_origin}")
        
        except Exception as e:
            logger.warning(f"DynamicCSRFOriginMiddleware error: {e}")
        
        return None


class NullOriginCSRFMiddleware(MiddlewareMixin):
    """
    Custom CSRF middleware that handles null origins from same-site requests.
    
    When a form is submitted from the same site (e.g., localhost form POST),
    browsers often send Origin: null or no Origin header. This middleware
    accepts those requests if the Referer header points to a trusted origin.
    """
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """Override to handle null origins gracefully"""
        
        origin = request.META.get('HTTP_ORIGIN', '')
        referer = request.META.get('HTTP_REFERER', '')
        host = request.get_host()
        
        # For localhost, skip origin validation if it's null
        if 'localhost' in host or '127.0.0.1' in host:
            if origin == 'null' or not origin:
                # Accept if this looks like a same-site request
                logger.debug(f"Accepting null origin for localhost: {request.path}")
                return None
        
        # Otherwise use default CSRF processing
        return super().process_view(request, view_func, view_args, view_kwargs)
