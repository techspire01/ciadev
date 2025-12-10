from django.contrib import admin
from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "created_at", "admin_image_preview")
    list_filter = ("is_active",)
    readonly_fields = ("admin_image_preview", "created_at")
    fieldsets = (
        ('Content', {'fields': ('title', 'description', 'is_active')}),
        ('Image', {'fields': ('image', 'admin_image_preview')}),
        ('Timestamps', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )

    actions = ["delete_announcements_and_files"]

    def delete_announcements_and_files(self, request, queryset):
        """
        Admin action to delete selected flash announcements AND their image files in storage.
        """
        count = 0
        for ann in queryset:
            # capture image name before delete
            image_name = ann.image.name if ann.image else None
            ann.delete()  # our model delete handles storage delete
            # if model delete didn't remove file (fallback), attempt explicit delete
            if image_name:
                try:
                    from django.core.files.storage import default_storage
                    default_storage.delete(image_name)
                except Exception:
                    pass
            count += 1
        self.message_user(request, f"Deleted {count} flash announcements and their images (if any).")
    delete_announcements_and_files.short_description = "Delete selected flash announcements and their image files"
