from django import forms
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from .models import Supplier

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
