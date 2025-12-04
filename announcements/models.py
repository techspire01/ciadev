from django.db import models
from django.utils.html import mark_safe


class Announcement(models.Model):
    title = models.CharField(max_length=200)
    caption = models.TextField(blank=True)
    image = models.ImageField(upload_to="announcements/", blank=True, null=True)
    #url = models.URLField(blank=True, null=True, help_text="Optional URL to open when user clicks announcement.")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Flash Announcement"
        verbose_name_plural = "Flash Announcements"

    def __str__(self):
        return self.title

    def admin_image_preview(self):
        if self.image:
            return mark_safe(f'<img src="{self.image.url}" style="max-height:120px;"/>')
        return "(no image)"
    admin_image_preview.short_description = "Image preview"

    def delete(self, *args, **kwargs):
        """
        Override model delete to remove image from storage as well.
        If image file exists, attempt to delete via default storage.
        """
        storage = self.image.storage if self.image else None
        image_name = self.image.name if self.image else None
        super().delete(*args, **kwargs)  # remove DB record
        # After DB delete, remove storage object
        try:
            if image_name and storage:
                storage.delete(image_name)
        except Exception:
            pass

