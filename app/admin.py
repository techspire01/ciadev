from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils import timezone
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import json
import logging

from .models import CustomUser, Supplier, Announcement, PhotoGallery, IndexHover, Leadership, NewspaperGallery, BookShowcase, SupplierEditRequest, ContactInformation
from .forms import SupplierForm

logger = logging.getLogger(__name__)

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    
    # These are required for UserAdmin to work properly with CustomUser
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    form = SupplierForm

    list_display = (
        "name",
        "business_description_display",
        "phone_number",
        "formatted_address",
        "created_at",
        'founder_name',
        'website_url',
        'category',
        'email',
        'contact_person_name'
    )

    search_fields = (
        'name',
        'email',
        'phone_number',
        'category',
        'sub_category1',
        'sub_category2',
        'sub_category3',
        'sub_category4',
        'sub_category5',
        'sub_category6',
        'founder_name',
        'contact_person_name',
        'city',
        'state',
        'area',
        'business_description',
        'gstno',
        'website_url'
    )

    list_filter = (
        'category',
        'state',
        'created_at'
    )

    ordering = ('name',)
    list_per_page = 25

    class Media:
        js = ('admin/js/supplier_category.js',)

    def business_description_display(self, obj):
        """Display first 50 characters of business description"""
        if obj.business_description:
            return obj.business_description[:50] + "..." if len(obj.business_description) > 50 else obj.business_description
        return "-"
    business_description_display.short_description = "Business Description"

    def formatted_address(self, obj):
        """Format the address from individual fields"""
        address_parts = []
        if obj.door_number:
            address_parts.append(obj.door_number)
        if obj.street:
            address_parts.append(obj.street)
        if obj.area:
            address_parts.append(obj.area)
        if obj.city:
            address_parts.append(obj.city)
        if obj.state:
            address_parts.append(obj.state)
        if obj.pin_code:
            address_parts.append(obj.pin_code)

        return ", ".join(address_parts) if address_parts else "-"
    formatted_address.short_description = "Address"

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'is_critical', 'is_active')
    list_filter = ('is_critical', 'is_active', 'date')
    search_fields = ('title', 'content')
    ordering = ('-date',)
    date_hierarchy = 'date'

@admin.register(PhotoGallery)
class PhotoGalleryAdmin(admin.ModelAdmin):
    list_display = ('title', 'image_preview', 'image_url', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('title',)
    ordering = ('-uploaded_at',)
    readonly_fields = ('image_preview_large', 'uploaded_at')
    fieldsets = (
        (None, {'fields': ('title', 'image_url', 'image_preview_large')}),
        ('Upload Information', {'fields': ('uploaded_at',)}),
    )

    def image_preview(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', obj.image_url)
        elif obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = "Image Preview"

    def image_preview_large(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" style="max-width: 300px; max-height: 300px; object-fit: cover;" />', obj.image_url)
        elif obj.image:
            return format_html('<img src="{}" style="max-width: 300px; max-height: 300px; object-fit: cover;" />', obj.image.url)
        return "No Image"
    image_preview_large.short_description = "Image Preview"

@admin.register(IndexHover)
class IndexHoverAdmin(admin.ModelAdmin):
    list_display = ('title', 'image_preview', 'image_url', 'caption', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'caption')
    ordering = ('-created_at',)
    readonly_fields = ('image_preview_large', 'created_at')
    fieldsets = (
        (None, {'fields': ('title', 'caption', 'image', 'image_url', 'image_preview_large')}),
        ('Timestamps', {'fields': ('created_at',)}),
    )

    def image_preview(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', obj.image_url)
        elif obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = "Image Preview"

    def image_preview_large(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" style="max-width: 300px; max-height: 300px; object-fit: cover;" />', obj.image_url)
        elif obj.image:
            return format_html('<img src="{}" style="max-width: 300px; max-height: 300px; object-fit: cover;" />', obj.image.url)
        return "No Image"
    image_preview_large.short_description = "Image Preview"

@admin.register(Leadership)
class LeadershipAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'photo_preview', 'created_at')
    list_filter = ('position', 'created_at')
    search_fields = ('name', 'position', 'bio')
    ordering = ('-created_at',)
    readonly_fields = ('photo_preview_large', 'created_at')
    fieldsets = (
        (None, {'fields': ('name', 'position', 'bio', 'photo_url', 'photo_preview_large')}),
        ('Social Media Links', {'fields': ('facebook', 'instagram', 'linkedin', 'twitter', 'email')}),
        ('Timestamps', {'fields': ('created_at',)}),
    )

    def photo_preview(self, obj):
        if obj.photo_url:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 50%;" />', obj.photo_url)
        elif obj.photo:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 50%;" />', obj.photo.url)
        return "No Photo"
    photo_preview.short_description = "Photo Preview"

    def photo_preview_large(self, obj):
        if obj.photo_url:
            return format_html('<img src="{}" style="max-width: 300px; max-height: 300px; object-fit: cover;" />', obj.photo_url)
        elif obj.photo:
            return format_html('<img src="{}" style="max-width: 300px; max-height: 300px; object-fit: cover;" />', obj.photo.url)
        return "No Photo"
    photo_preview_large.short_description = "Photo Preview"

@admin.register(NewspaperGallery)
class NewspaperGalleryAdmin(admin.ModelAdmin):
    list_display = ('title', 'image_preview', 'image_url', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('title',)
    ordering = ('-uploaded_at',)
    readonly_fields = ('image_preview_large', 'uploaded_at')
    fieldsets = (
        (None, {'fields': ('title', 'image_url', 'image_preview_large')}),
        ('Upload Information', {'fields': ('uploaded_at',)}),
    )

    def image_preview(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', obj.image_url)
        elif obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = "Image Preview"

    def image_preview_large(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" style="max-width: 300px; max-height: 300px; object-fit: cover;" />', obj.image_url)
        elif obj.image:
            return format_html('<img src="{}" style="max-width: 300px; max-height: 300px; object-fit: cover;" />', obj.image.url)
        return "No Image"
    image_preview_large.short_description = "Image Preview"

@admin.register(BookShowcase)
class BookShowcaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'image_preview', 'image_url', 'order', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title',)
    ordering = ('order', '-created_at',)
    readonly_fields = ('image_preview_large', 'created_at')
    fieldsets = (
        (None, {'fields': ('title', 'image_url', 'order', 'image_preview_large')}),
        ('Upload Information', {'fields': ('created_at',)}),
    )

    def image_preview(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', obj.image_url)
        elif obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = "Image Preview"

    def image_preview_large(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" style="max-width: 300px; max-height: 300px; object-fit: cover;" />', obj.image_url)
        elif obj.image:
            return format_html('<img src="{}" style="max-width: 300px; max-height: 300px; object-fit: cover;" />', obj.image.url)
        return "No Image"
    image_preview_large.short_description = "Image Preview"

class SupplierEditRequestAdmin(admin.ModelAdmin):
    # Use callables to avoid referencing possibly missing model attributes directly
    list_display = ('supplier_display', 'user_display', 'message_display', 'contact_phone', 'created_display', 'status')
    readonly_fields = ('message', 'contact_phone', 'reviewed_at', 'reviewed_by')
    search_fields = ('supplier__name', 'user__email', 'message')
    list_filter = ('status',)
    list_per_page = 25

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Show only pending requests by default
        return qs.filter(status='pending')

    def supplier_display(self, obj):
        return getattr(obj, 'supplier', None)
    supplier_display.short_description = 'Supplier'

    def user_display(self, obj):
        return getattr(obj, 'user', None)
    user_display.short_description = 'User'

    def created_display(self, obj):
        # try common timestamp fields
        for attr in ('created_at', 'created', 'timestamp', 'created_on'):
            if hasattr(obj, attr):
                return getattr(obj, attr)
        return getattr(obj, 'id', '')
    created_display.short_description = 'Created At'

    def message_display(self, obj):
        message = getattr(obj, 'message', '')
        if len(message) > 50:
            return message[:50] + '...'
        return message
    message_display.short_description = 'Message'

    actions = ['approve_requests', 'deny_requests']

    def approve_requests(self, request, queryset):
        """
        Admin action to approve selected edit requests (mark as approved and notify user).
        """
        approved = 0
        for edit_request in queryset:
            edit_request.status = 'approved'
            edit_request.reviewed_by = request.user
            edit_request.reviewed_at = timezone.now()
            edit_request.save()
            approved += 1

            # notify requesting user about approval
            try:
                user = getattr(edit_request, 'user', None)
                supplier = getattr(edit_request, 'supplier', None)
                if user and getattr(user, 'email', None):
                    subject = f"Your edit request for {getattr(supplier, 'name', 'supplier')} has been approved"
                    body = f"Your edit request has been approved by admin.\n\nMessage: {getattr(edit_request, 'message', '')}\nContact Phone: {getattr(edit_request, 'contact_phone', '')}\n\nIf you have questions, contact support."
                    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'webmaster@localhost')
                    send_mail(subject, body, from_email, [user.email], fail_silently=True)
            except Exception:
                logger.exception("Failed to notify user after approving edit request")

        self.message_user(request, f"Approved {approved} request(s).")
    approve_requests.short_description = "Approve selected supplier edit requests"

    def deny_requests(self, request, queryset):
        """
        Admin action to deny selected edit requests.
        """
        denied = 0
        for edit_request in queryset:
            edit_request.status = 'rejected'
            edit_request.reviewed_by = request.user
            edit_request.reviewed_at = timezone.now()
            edit_request.save()
            denied += 1

            # Notify requesting user about denial
            try:
                user = getattr(edit_request, 'user', None)
                supplier = getattr(edit_request, 'supplier', None)
                if user and getattr(user, 'email', None):
                    subject = f"Your edit request for {getattr(supplier, 'name', 'supplier')} has been denied"
                    body = f"Your edit request has been denied by admin.\n\nMessage: {getattr(edit_request, 'message', '')}\nContact Phone: {getattr(edit_request, 'contact_phone', '')}\n\nIf you have questions, contact support."
                    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'webmaster@localhost')
                    send_mail(subject, body, from_email, [user.email], fail_silently=True)
            except Exception:
                logger.exception("Failed to notify user after denying edit request")

        self.message_user(request, f"Denied {denied} request(s).")
    deny_requests.short_description = "Deny selected supplier edit requests"

# Register with admin site (safe even if model fields vary)
admin.site.register(SupplierEditRequest, SupplierEditRequestAdmin)


@receiver(post_save, sender=SupplierEditRequest)
def notify_admin_on_new_edit_request(sender, instance, created, **kwargs):
    """
    Send an email to admins when a new SupplierEditRequest is created.
    This is a fallback in case the view-level notification fails.
    """
    if not created:
        return

    try:
        admin_list = [email for _, email in getattr(settings, 'ADMINS', [])]
        if not admin_list:
            admin_list = ['admin@cia.com']

        supplier_name = getattr(instance, 'supplier', None)
        user_email = getattr(getattr(instance, 'user', None), 'email', 'unknown')
        data = getattr(instance, 'requested_data', {})
        # If JSON stored as string, attempt to convert to dict for readable message
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except Exception:
                pass

        message_lines = [
            f"A supplier edit request has been submitted.",
            f"User: {user_email}",
            f"Supplier: {supplier_name}",
            "Requested Changes:"
        ]
        if isinstance(data, dict):
            for k, v in data.items():
                message_lines.append(f"- {k}: {v}")
        else:
            message_lines.append(str(data))

        subject = f"Supplier Edit Request: {supplier_name}"
        body = "\n".join(message_lines)
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'webmaster@localhost')
        send_mail(subject, body, from_email, admin_list, fail_silently=False)
    except Exception as e:
        logger.exception("Failed to send admin notification for SupplierEditRequest: %s", e)

@admin.register(ContactInformation)
class ContactInformationAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone', 'address_preview', 'created_at', 'updated_at')
    search_fields = ('email', 'phone', 'address', 'description')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Contact Details', {
            'fields': ('email', 'phone', 'address')
        }),
        ('Additional Information', {
            'fields': ('description',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def address_preview(self, obj):
        """Display first 50 characters of address"""
        if obj.address:
            return obj.address[:50] + "..." if len(obj.address) > 50 else obj.address
        return "-"
    address_preview.short_description = "Address"

# Register CustomUser with the admin site
admin.site.register(CustomUser, CustomUserAdmin)
