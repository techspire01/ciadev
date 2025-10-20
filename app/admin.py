
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, Supplier, Announcement, PhotoGallery, IndexHover, Leadership, NewspaperGallery
from .forms import SupplierForm

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

admin.site.register(CustomUser, CustomUserAdmin)
