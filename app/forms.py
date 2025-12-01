from django import forms
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from .models import Supplier, CustomUser, SupplierEditRequest, SupplierListingRequest, SupplierReview

from .models import Complaint

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
        if commit:
            instance.save()
        return instance

    class Meta:
        model = Supplier
        fields = [
            'name', 'founder_name', 'website_url', 'logo_url', 'image_url',
            'category', 'sub_category1', 'sub_category2', 'sub_category3',
            'email', 'contact_person_name',
            'person_image_url', 'product1', 'product2', 'product3', 'product4', 'product5', 'product6', 'product7', 'product8', 'product9', 'product10',
            'product_image1_url', 'product_image2_url', 'product_image3_url', 'product_image4_url', 'product_image5_url', 'product_image6_url', 'product_image7_url', 'product_image8_url', 'product_image9_url', 'product_image10_url',
            'door_number', 'street', 'area', 'city', 'state',
            'pin_code', 'business_description', 'phone_number',
            'gstno', 'instagram', 'facebook', 'total_employees'
        ]  # Explicitly include all fields from the Supplier model

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


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['complaint_text', 'contact_number']
        widgets = {
            'complaint_text': forms.Textarea(attrs={'rows':4, 'placeholder':'Describe your complaint...'}),
            'contact_number': forms.TextInput(attrs={'placeholder': 'Contact number (optional)'}),
        }


class SupplierReviewForm(forms.ModelForm):
    class Meta:
        model = SupplierReview
        fields = ['reviewer_name', 'rating', 'comment']
        widgets = {
            'reviewer_name': forms.TextInput(attrs={'class': 'w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-yellow-500 focus:outline-none focus:ring-2 focus:ring-yellow-200', 'placeholder': 'Your name'}),
            'rating': forms.Select(attrs={'class': 'w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-yellow-500 focus:outline-none focus:ring-2 focus:ring-yellow-200'}),
            'comment': forms.Textarea(attrs={'rows': 4, 'class': 'w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-yellow-500 focus:outline-none focus:ring-2 focus:ring-yellow-200', 'placeholder': 'Share your experience (optional)'}),
        }
        labels = {
            'reviewer_name': 'Name',
            'rating': 'Rating',
            'comment': 'Comments',
        }
