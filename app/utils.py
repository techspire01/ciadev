import random
import logging
from django.core.mail import send_mail
from django.core.mail.backends.smtp import EmailBackend
from django.conf import settings
from django.core.exceptions import PermissionDenied
from .models import EmailConfiguration, Supplier

logger = logging.getLogger('cai_security')

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_via_email(email, otp):
    subject = "Your OTP Verification Code"
    message = f"Your One Time Password is {otp}. It will expire in 5 minutes."
    send_mail(subject, message, "dezacodex@gmail.com", [email])

def get_email_settings():
    try:
        config = EmailConfiguration.objects.first()
        if config:
            return {
                'host': config.host,
                'port': config.port,
                'use_tls': config.use_tls,
                'use_ssl': config.use_ssl,
                'host_user': config.host_user,
                'host_password': config.host_password,
                'default_from_email': config.default_from_email,
            }
        else:
            # Fallback to settings
            return {
                'host': getattr(settings, 'EMAIL_HOST', 'smtp.gmail.com'),
                'port': getattr(settings, 'EMAIL_PORT', 587),
                'use_tls': getattr(settings, 'EMAIL_USE_TLS', True),
                'use_ssl': getattr(settings, 'EMAIL_USE_SSL', False),
                'host_user': getattr(settings, 'EMAIL_HOST_USER', ''),
                'host_password': getattr(settings, 'EMAIL_HOST_PASSWORD', ''),
                'default_from_email': getattr(settings, 'DEFAULT_FROM_EMAIL', ''),
            }
    except:
        # If database is not available, use settings
        return {
            'host': getattr(settings, 'EMAIL_HOST', 'smtp.gmail.com'),
            'port': getattr(settings, 'EMAIL_PORT', 587),
            'use_tls': getattr(settings, 'EMAIL_USE_TLS', True),
            'use_ssl': getattr(settings, 'EMAIL_USE_SSL', False),
            'host_user': getattr(settings, 'EMAIL_HOST_USER', ''),
            'host_password': getattr(settings, 'EMAIL_HOST_PASSWORD', ''),
            'default_from_email': getattr(settings, 'DEFAULT_FROM_EMAIL', ''),
        }

class DynamicEmailBackend(EmailBackend):
    def __init__(self, host=None, port=None, username=None, password=None, use_tls=None, fail_silently=False, use_ssl=None, timeout=None, ssl_keyfile=None, ssl_certfile=None):
        # Get settings from model
        email_settings = get_email_settings()
        host = host or email_settings['host']
        port = port or email_settings['port']
        username = username or email_settings['host_user']
        password = password or email_settings['host_password']
        use_tls = use_tls if use_tls is not None else email_settings['use_tls']
        use_ssl = use_ssl if use_ssl is not None else email_settings['use_ssl']
        super().__init__(host, port, username, password, use_tls, fail_silently, use_ssl, timeout, ssl_keyfile, ssl_certfile)


def get_supplier_for_user_or_raise(request):
    """
    Get the Supplier associated with the current user.
    
    Tries the new OneToOne relationship first (preferred).
    Falls back to email lookup for migration window.
    
    Raises PermissionDenied if user is not a supplier.
    Logs fallback usage for audit trail.
    
    Args:
        request: Django request object
        
    Returns:
        Supplier: The supplier associated with the user
        
    Raises:
        PermissionDenied: If user is not associated with any supplier
    """
    try:
        # Try new OneToOne relationship first
        supplier = Supplier.objects.get(user=request.user)
        return supplier
    except Supplier.DoesNotExist:
        pass
    
    # Fallback: Try email lookup (for migration window)
    try:
        supplier = Supplier.objects.get(email__iexact=request.user.email)
        logger.warning(
            "Supplier fallback used for user %s (email: %s). Link Supplier.user to prevent this.",
            request.user.id,
            request.user.email
        )
        return supplier
    except Supplier.DoesNotExist:
        logger.warning(
            "Supplier lookup failed for user %s (email: %s). Not a supplier.",
            request.user.id,
            getattr(request.user, 'email', 'unknown')
        )
        raise PermissionDenied("Access denied. Only suppliers can access this page.")
    except Supplier.MultipleObjectsReturned:
        logger.error(
            "Multiple suppliers found with email %s for user %s",
            request.user.email,
            request.user.id
        )
        raise PermissionDenied("Database integrity error. Please contact support.")

