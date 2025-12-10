from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
from django.utils import timezone
import datetime
from django.utils.translation import gettext_lazy as _
from utils.paths import supplier_logo_upload, photo_gallery_upload, book_upload, newspaper_upload, flash_upload

# Create your models here.
class Announcement(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    is_critical = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    referral_url = models.TextField(blank=True, null=True)
    image1 = models.ImageField(upload_to=flash_upload, blank=True, null=True)
    image1_url = models.URLField(blank=True, null=True)
    image2 = models.ImageField(upload_to=flash_upload, blank=True, null=True)
    image2_url = models.URLField(blank=True, null=True)
    image3 = models.ImageField(upload_to=flash_upload, blank=True, null=True)
    image3_url = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.title} - {self.date.strftime('%Y-%m-%d')}"

class Supplier(models.Model):
    name = models.CharField(max_length=255, unique=True)  # enforce unique name  
    founder_name = models.CharField(max_length=255, blank=True, null=True)

    website_url = models.TextField(blank=True, null=True)
    logo_url = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to=supplier_logo_upload, blank=True, null=True)
    image_url = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    sub_category1 = models.CharField(max_length=255, blank=True, null=True)
    sub_category2 = models.CharField(max_length=255, blank=True, null=True)
    sub_category3 = models.CharField(max_length=255, blank=True, null=True)
    sub_category4 = models.CharField(max_length=255, blank=True, null=True)
    sub_category5 = models.CharField(max_length=255, blank=True, null=True)
    sub_category6 = models.CharField(max_length=255, blank=True, null=True)
    product_image1_url = models.TextField(blank=True, null=True)
    product_image2_url = models.TextField(blank=True, null=True)
    product_image3_url = models.TextField(blank=True, null=True)
    product_image4_url = models.TextField(blank=True, null=True)
    product_image5_url = models.TextField(blank=True, null=True)
    product_image6_url = models.TextField(blank=True, null=True)
    product_image7_url = models.TextField(blank=True, null=True)
    product_image8_url = models.TextField(blank=True, null=True)
    product_image9_url = models.TextField(blank=True, null=True)
    product_image10_url = models.TextField(blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    contact_person_name = models.CharField(max_length=255, blank=True, null=True)
    person_image_url = models.TextField(blank=True, null=True)

    # Product fields
    product1 = models.CharField(max_length=255, blank=True, null=True)
    product2 = models.CharField(max_length=255, blank=True, null=True)
    product3 = models.CharField(max_length=255, blank=True, null=True)
    product4 = models.CharField(max_length=255, blank=True, null=True)
    product5 = models.CharField(max_length=255, blank=True, null=True)
    product6 = models.CharField(max_length=255, blank=True, null=True)
    product7 = models.CharField(max_length=255, blank=True, null=True)
    product8 = models.CharField(max_length=255, blank=True, null=True)
    product9 = models.CharField(max_length=255, blank=True, null=True)
    product10 = models.CharField(max_length=255, blank=True, null=True)

    # Split address fields
    door_number = models.CharField(max_length=50, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    area = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pin_code = models.CharField(max_length=6, blank=True, null=True)

    # Expanded business details
    business_description = models.TextField(blank=True, null=True)

    phone_number = models.CharField(max_length=15, blank=True, null=True)

    # New fields
    gstno = models.CharField(max_length=15, blank=True, null=True)
    instagram = models.TextField(blank=True, null=True)
    facebook = models.TextField(blank=True, null=True)
    total_employees = models.IntegerField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    cia_id = models.PositiveIntegerField(unique=True, blank=True, null=True)  # CIA serial id
    
    # Link supplier to a user account (OneToOne, optional for migration window)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='supplier_profile'
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.cia_id:
            # Assign next available cia_id (serialized, no gaps)
            existing_ids = Supplier.objects.exclude(pk=self.pk).order_by('cia_id').values_list('cia_id', flat=True)
            next_id = 1
            for eid in existing_ids:
                if eid != next_id:
                    break
                next_id += 1
            self.cia_id = next_id
        super().save(*args, **kwargs)

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        swappable = 'AUTH_USER_MODEL'

class PasswordResetOTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return timezone.now() < self.created_at + datetime.timedelta(minutes=10)

class PhotoGallery(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to=photo_gallery_upload, blank=True, null=True)
    image_url = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title or f"Photo {self.id}"

class Leadership(models.Model):
    name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    bio = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to="leadership/photos/", blank=True, null=True)
    photo_url = models.TextField(blank=True, null=True)
    facebook = models.TextField(blank=True, null=True)
    instagram = models.TextField(blank=True, null=True)
    linkedin = models.TextField(blank=True, null=True)
    twitter = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    dis_pos = models.PositiveIntegerField(default=0, help_text="Display position for ordering leadership cards")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['dis_pos', '-created_at']

    def __str__(self):
        return f"{self.name} - {self.position}"

class NewspaperGallery(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to=newspaper_upload, blank=True, null=True)
    image_url = models.TextField(blank=True, null=True)
    date = models.DateField(blank=True, null=True, help_text="Manually entered date for the newspaper cutting")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title or f"Newspaper Cutting {self.id}"

class BookShowcase(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to=book_upload, blank=True, null=True)
    image_url = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0, help_text="Order for display")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title or f"Book Image {self.id}"

class SupplierEditRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()  # User's message describing the requested changes
    contact_phone = models.CharField(max_length=15, blank=True, null=True)  # Contact phone for the request
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_requests')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Edit request for {self.supplier.name} by {self.user.email}"

class SupplierListingRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    # Company Information
    company_name = models.CharField(max_length=255)
    founder_name = models.CharField(max_length=255, blank=True, null=True)
    website_url = models.TextField(blank=True, null=True)
    logo_url = models.TextField(blank=True, null=True)
    image_url = models.TextField(blank=True, null=True)

    # Business Details
    category = models.CharField(max_length=255, blank=True, null=True)
    sub_category1 = models.CharField(max_length=255, blank=True, null=True)
    sub_category2 = models.CharField(max_length=255, blank=True, null=True)
    sub_category3 = models.CharField(max_length=255, blank=True, null=True)

    # Contact Information
    email = models.EmailField(max_length=255)
    contact_person_name = models.CharField(max_length=255, blank=True, null=True)
    person_image_url = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    # Products (up to 10)
    product1 = models.CharField(max_length=255, blank=True, null=True)
    product2 = models.CharField(max_length=255, blank=True, null=True)
    product3 = models.CharField(max_length=255, blank=True, null=True)
    product4 = models.CharField(max_length=255, blank=True, null=True)
    product5 = models.CharField(max_length=255, blank=True, null=True)
    product6 = models.CharField(max_length=255, blank=True, null=True)
    product7 = models.CharField(max_length=255, blank=True, null=True)
    product8 = models.CharField(max_length=255, blank=True, null=True)
    product9 = models.CharField(max_length=255, blank=True, null=True)
    product10 = models.CharField(max_length=255, blank=True, null=True)

    # Address
    door_number = models.CharField(max_length=50, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    area = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pin_code = models.CharField(max_length=6, blank=True, null=True)

    # Additional Business Details
    business_description = models.TextField(blank=True, null=True)
    gstno = models.CharField(max_length=15, blank=True, null=True)
    instagram = models.TextField(blank=True, null=True)
    facebook = models.TextField(blank=True, null=True)
    total_employees = models.IntegerField(blank=True, null=True)

    # Request metadata
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_listing_requests')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Listing request for {self.company_name} by {self.user.email}"

class About(models.Model):
    mission = models.TextField(blank=True, null=True, help_text="Our mission statement")
    story = models.TextField(blank=True, null=True, help_text="Our story content")
    member_companies = models.PositiveIntegerField(default=0, help_text="Number of member companies")
    industrial_sectors = models.PositiveIntegerField(default=0, help_text="Number of industrial sectors")
    established_year = models.PositiveIntegerField(default=2020, help_text="Year established")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "About"
        verbose_name_plural = "About"

    def __str__(self):
        return "About Page Content"

class ContactInformation(models.Model):
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Contact Information"
        verbose_name_plural = "Contact Information"

    def __str__(self):
        return f"Contact Information - {self.email or 'No Email'}"


class Complaint(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    complaint_text = models.TextField()
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Complaint #{self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class EmailConfiguration(models.Model):
    host = models.CharField(max_length=255, default='smtp.gmail.com')
    port = models.IntegerField(default=587)
    use_tls = models.BooleanField(default=True)
    use_ssl = models.BooleanField(default=False)
    host_user = models.EmailField(default='cianextcbe@gmail.com')
    host_password = models.CharField(max_length=255, default='cwgk azyb oxsp pfih')
    default_from_email = models.EmailField(default='cianextcbe@gmail.com')

    class Meta:
        verbose_name = "Email Configuration"
        verbose_name_plural = "Email Configuration"

    def __str__(self):
        return "Email Configuration"
