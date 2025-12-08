"""
Security middleware for CIA Portal

Logs security-related events including:
- Unauthorized access attempts (403)
- Rate limit rejections (429)
- Other suspicious activity
"""

import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse

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
