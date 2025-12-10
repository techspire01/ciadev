from django import forms
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from .models import Supplier, CustomUser, SupplierEditRequest, SupplierListingRequest

from .models import Complaint

from django.core.files.storage import default_storage
from django.conf import settings
import time
import os


class SupplierForm(forms.ModelForm):

    category = forms.ChoiceField(required=False)
    new_category = forms.CharField(required=False, label='New Category')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Supplier.objects.exclude(category__isnull=True).exclude(category__exact='').values_list('category', flat=True).distinct()
        choices = [(cat, cat) for cat in categories]
        choices.append(('__add_new__', 'Add new category'))
        self.fields['category'].choices = choices

    def clean_logo_url(self):
        url = self.cleaned_data.get('logo_url')
        if url:
            validator = URLValidator()
            try:
                validator(url)
            except ValidationError:
                raise ValidationError("Enter a valid URL.")
        return url

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        new_category = cleaned_data.get('new_category')
        if category == '__add_new__' and not new_category:
            self.add_error('new_category', 'Please enter a new category.')
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        category = self.cleaned_data.get('category')
        new_category = self.cleaned_data.get('new_category')
        if category == '__add_new__' and new_category:
            instance.category = new_category
        else:
            instance.category = category
        # Handle company image upload: if provided, save and set `image_url`
        company_image = self.cleaned_data.get('image_upload') if 'image_upload' in self.cleaned_data else None
        if company_image:
            name_part = (instance.name or 'supplier').replace(' ', '_')
            ext = os.path.splitext(company_image.name)[1]
            filename = f"companies/{int(time.time())}_{name_part}/company_image{ext}"
            saved_path = default_storage.save(filename, company_image)
            try:
                file_url = default_storage.url(saved_path)
            except Exception as e:
                # Fallback: construct URL from MEDIA_URL and saved path
                media_url = settings.MEDIA_URL.rstrip('/')
                saved_path_clean = str(saved_path).lstrip('/')
                file_url = f"{media_url}/{saved_path_clean}"
            instance.image_url = file_url

        # Handle up to 10 product image uploads. For each slot, if a file is uploaded
        # it takes precedence and we set the corresponding product_imageX_url.
        for i in range(1, 11):
            upload_field = f'product_image_upload_{i}'
            uploaded = self.cleaned_data.get(upload_field) if upload_field in self.cleaned_data else None
            if uploaded:
                name_part = (instance.name or 'supplier').replace(' ', '_')
                ext = os.path.splitext(uploaded.name)[1]
                filename = f"companies/{int(time.time())}_{name_part}/products/product_{i}{ext}"
                saved_path = default_storage.save(filename, uploaded)
                try:
                    file_url = default_storage.url(saved_path)
                except Exception as e:
                    # Fallback: construct URL from MEDIA_URL and saved path
                    media_url = settings.MEDIA_URL.rstrip('/')
                    saved_path_clean = str(saved_path).lstrip('/')
                    file_url = f"{media_url}/{saved_path_clean}"
                setattr(instance, f'product_image{i}_url', file_url)

        if commit:
            instance.save()
        return instance

    class Meta:
        model = Supplier
        fields = [
            'name', 'founder_name', 'website_url', 'logo_url', 'image_url',
            'logo',
            'category', 'sub_category1', 'sub_category2', 'sub_category3',
            'email', 'contact_person_name',
            'product1', 'product2', 'product3', 'product4', 'product5', 'product6', 'product7', 'product8', 'product9', 'product10',
            'product_image1_url', 'product_image2_url', 'product_image3_url', 'product_image4_url', 'product_image5_url',
            'product_image6_url', 'product_image7_url', 'product_image8_url', 'product_image9_url', 'product_image10_url',
            'door_number', 'street', 'area', 'city', 'state',
            'pin_code', 'business_description', 'phone_number',
            'gstno', 'instagram', 'facebook', 'total_employees'
        ]  # Explicitly include all fields from the Supplier model

    # Extra non-model field for single product image upload in admin
    # Company image upload which will populate `image_url` when used
    image_upload = forms.ImageField(
        required=False,
        label='Upload Company Image',
        help_text='Provide EITHER a URL (above) OR upload a file here. If you upload a file, it will replace any URL you entered.'
    )

    # Per-product upload fields. Admin will show both URL inputs (model fields)
    # and these upload inputs; uploaded files take precedence.
    product_image_upload_1 = forms.ImageField(required=False, label='Product 1 Image Upload', help_text='Provide EITHER a URL (above) OR upload a file here. Upload takes precedence.')
    product_image_upload_2 = forms.ImageField(required=False, label='Product 2 Image Upload', help_text='Provide EITHER a URL (above) OR upload a file here. Upload takes precedence.')
    product_image_upload_3 = forms.ImageField(required=False, label='Product 3 Image Upload', help_text='Provide EITHER a URL (above) OR upload a file here. Upload takes precedence.')
    product_image_upload_4 = forms.ImageField(required=False, label='Product 4 Image Upload', help_text='Provide EITHER a URL (above) OR upload a file here. Upload takes precedence.')
    product_image_upload_5 = forms.ImageField(required=False, label='Product 5 Image Upload', help_text='Provide EITHER a URL (above) OR upload a file here. Upload takes precedence.')
    product_image_upload_6 = forms.ImageField(required=False, label='Product 6 Image Upload', help_text='Provide EITHER a URL (above) OR upload a file here. Upload takes precedence.')
    product_image_upload_7 = forms.ImageField(required=False, label='Product 7 Image Upload', help_text='Provide EITHER a URL (above) OR upload a file here. Upload takes precedence.')
    product_image_upload_8 = forms.ImageField(required=False, label='Product 8 Image Upload', help_text='Provide EITHER a URL (above) OR upload a file here. Upload takes precedence.')
    product_image_upload_9 = forms.ImageField(required=False, label='Product 9 Image Upload', help_text='Provide EITHER a URL (above) OR upload a file here. Upload takes precedence.')
    product_image_upload_10 = forms.ImageField(required=False, label='Product 10 Image Upload', help_text='Provide EITHER a URL (above) OR upload a file here. Upload takes precedence.')

class UserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input w-full'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input w-full'}))

    membership_type = forms.ChoiceField(
        choices=[
            ('Individual', 'Individual'),
            ('Organization', 'Organization'),
            ('Corporate', 'Corporate')
        ],
        widget=forms.Select(attrs={'class': 'form-input w-full'})
    )
    business_type = forms.ChoiceField(
        choices=[
            ('Manufacturing', 'Manufacturing'),
            ('Textiles', 'Textiles'),
            ('Automobile', 'Automobile'),
            ('IT/Software', 'IT/Software'),
            ('Other', 'Other')
        ],
        widget=forms.Select(attrs={'class': 'form-input w-full'})
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-input w-full'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input w-full'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input w-full'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'email': forms.EmailInput(attrs={'readonly': True}),
        }

class SupplierEditForm(forms.ModelForm):
    message = forms.CharField(widget=forms.Textarea, label='Message', help_text='Describe the changes you want to make to your supplier profile.')
    contact_phone = forms.CharField(max_length=15, required=False, label='Contact Phone', help_text='Optional contact phone number for this request.')

    class Meta:
        model = SupplierEditRequest
        fields = ['message', 'contact_phone']

class SupplierListingForm(forms.ModelForm):
    category = forms.ChoiceField(required=False)
    new_category = forms.CharField(required=False, label='New Category')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Supplier.objects.exclude(category__isnull=True).exclude(category__exact='').values_list('category', flat=True).distinct()
        choices = [(cat, cat) for cat in categories]
        choices.append(('__add_new__', 'Add new category'))
        self.fields['category'].choices = choices

    def clean_logo_url(self):
        url = self.cleaned_data.get('logo_url')
        if url:
            validator = URLValidator()
            try:
                validator(url)
            except ValidationError:
                raise ValidationError("Enter a valid URL.")
        return url

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        new_category = cleaned_data.get('new_category')
        if category == '__add_new__' and not new_category:
            self.add_error('new_category', 'Please enter a new category.')
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        category = self.cleaned_data.get('category')
        new_category = self.cleaned_data.get('new_category')
        if category == '__add_new__' and new_category:
            instance.category = new_category
        else:
            instance.category = category
        if commit:
            instance.save()
        return instance

    class Meta:
        model = SupplierListingRequest
        fields = [
            'company_name', 'founder_name', 'website_url', 'logo_url', 'image_url',
            'category', 'sub_category1', 'sub_category2', 'sub_category3',
            'email', 'contact_person_name',
            'person_image_url', 'product1', 'product2', 'product3', 'product4', 'product5', 'product6', 'product7', 'product8', 'product9', 'product10',
            'door_number', 'street', 'area', 'city', 'state',
            'pin_code', 'business_description', 'phone_number',
            'gstno', 'instagram', 'facebook', 'total_employees'
        ]


from announcements.models import Announcement

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'description', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input w-full'}),
            'description': forms.Textarea(attrs={'class': 'form-input w-full', 'rows': 4}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-input w-full'}),
        }

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['complaint_text', 'contact_number']
        widgets = {
            'complaint_text': forms.Textarea(attrs={'rows':4, 'placeholder':'Describe your complaint...'}),
            'contact_number': forms.TextInput(attrs={'placeholder': 'Contact number (optional)'}),
        }
