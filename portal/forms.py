from django import forms
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from .models import InternshipApplication, JobApplication


class InternshipApplicationForm(forms.ModelForm):
    """Form for internship applications with conditional fields based on fresher/experienced status"""

    # Personal Details
    first_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name',
        })
    )
    last_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name',
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number',
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address',
        })
    )
    address = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Address',
        })
    )
    city = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City',
        })
    )
    state = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'State',
        })
    )
    country = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Country',
        })
    )

    # Experience Status
    status = forms.ChoiceField(
        choices=[
            ('fresher', 'Fresher'),
            ('experienced', 'Experienced'),
        ],
        required=True,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input',
        }),
        label='Are you a Fresher or Experienced?'
    )

    # Resume Upload
    resume = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.doc,.docx',
        }),
        help_text='Max size: 2MB. Accepted formats: PDF, DOCX, DOC',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])]
    )

    # Education Details (Required for all)
    school_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'School/College Name',
        }),
        label='School/College Name'
    )
    city_of_study = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City',
        }),
        label='City of Study'
    )
    degree = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Degree (e.g., Bachelor of Science)',
        })
    )
    field_of_study = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Major/Field of Study',
        }),
        label='Major/Field of Study'
    )
    study_from_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        }),
        label='From Date'
    )
    study_to_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        }),
        label='To Date'
    )
    currently_studying = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        }),
        label='Currently studying'
    )

    # Skills (Optional)
    skills = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter skills separated by commas (e.g., Python, JavaScript, Data Analysis)',
        }),
        help_text='Enter skills separated by commas or as tags'
    )

    # LinkedIn Profile
    linkedin_profile = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://linkedin.com/in/yourprofile',
        }),
        label='LinkedIn Profile URL'
    )

    # Internships (Optional for freshers)
    internships = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'List your internships (optional)',
        }),
        help_text='Details of internships (optional)',
        label='Internships (Optional)'
    )

    # Additional Questions
    additional_questions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Answer any additional questions (0-2000 characters)',
            'maxlength': '2000',
        }),
        max_length=2000,
        label='Additional Questions (Optional)'
    )

    # Message to Hiring Manager
    message_to_manager = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Message to Hiring Manager (0-2000 characters)',
            'maxlength': '2000',
        }),
        max_length=2000,
        label='Message to Hiring Manager'
    )

    # Additional Attachments
    additional_attachment = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.doc,.docx,.png,.jpg,.jpeg',
        }),
        help_text='Max size: 5MB. Accepted formats: PDF, DOCX, DOC, PNG, JPG'
    )

    class Meta:
        model = InternshipApplication
        fields = [
            'first_name', 'last_name', 'phone', 'email', 'address', 'city', 'state', 'country',
            'status', 'resume',
            'school_name', 'city_of_study', 'degree', 'field_of_study', 'study_from_date', 'study_to_date', 'currently_studying',
            'skills', 'linkedin_profile', 'internships',
            'additional_questions', 'message_to_manager', 'additional_attachment'
        ]

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        currently_studying = cleaned_data.get('currently_studying')
        study_to_date = cleaned_data.get('study_to_date')

        # If not currently studying, study_to_date is required
        if status and not currently_studying and not study_to_date:
            raise ValidationError("Please specify the end date or check 'Currently studying'.")

        return cleaned_data


class JobApplicationForm(forms.ModelForm):
    """Form for job applications with conditional fields based on fresher/experienced status"""

    # Personal Details
    first_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name',
        })
    )
    last_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name',
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number',
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address',
        })
    )
    address = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Address',
        })
    )
    city = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City',
        })
    )
    state = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'State',
        })
    )
    country = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Country',
        })
    )

    # Experience Status
    status = forms.ChoiceField(
        choices=[
            ('fresher', 'Fresher'),
            ('experienced', 'Experienced'),
        ],
        required=True,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input',
        }),
        label='Are you a Fresher or Experienced?'
    )

    # Resume Upload
    resume = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.doc,.docx',
        }),
        help_text='Max size: 2MB. Accepted formats: PDF, DOCX, DOC',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])]
    )

    # Education Details (Required for all)
    school_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'School/College Name',
        }),
        label='School/College Name'
    )
    city_of_study = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City',
        }),
        label='City of Study'
    )
    degree = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Degree (e.g., Bachelor of Science)',
        })
    )
    field_of_study = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Major/Field of Study',
        }),
        label='Major/Field of Study'
    )
    study_from_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        }),
        label='From Date'
    )
    study_to_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        }),
        label='To Date'
    )
    currently_studying = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        }),
        label='Currently studying'
    )

    # Work Experience (Required for experienced, optional for freshers)
    work_experiences_json = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label='Work Experiences (JSON)'
    )

    # Skills
    skills = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter skills separated by commas (e.g., Python, JavaScript, Project Management)',
        }),
        help_text='Enter skills separated by commas or as tags'
    )

    # LinkedIn Profile
    linkedin_profile = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://linkedin.com/in/yourprofile',
        }),
        label='LinkedIn Profile URL'
    )

    # Screening Questions
    screening_questions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Answer any screening questions (0-2000 characters)',
            'maxlength': '2000',
        }),
        max_length=2000,
        label='Screening Questions (Optional)'
    )

    # Message to Hiring Manager
    message_to_manager = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Message to Hiring Manager (0-2000 characters)',
            'maxlength': '2000',
        }),
        max_length=2000,
        label='Message to Hiring Manager'
    )

    # Additional Attachments
    additional_attachment = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.doc,.docx,.png,.jpg,.jpeg',
        }),
        help_text='Max size: 5MB. Accepted formats: PDF, DOCX, DOC, PNG, JPG'
    )

    class Meta:
        model = JobApplication
        fields = [
            'first_name', 'last_name', 'phone', 'email', 'address', 'city', 'state', 'country',
            'status', 'resume',
            'school_name', 'city_of_study', 'degree', 'field_of_study', 'study_from_date', 'study_to_date', 'currently_studying',
            'skills', 'linkedin_profile',
            'screening_questions', 'message_to_manager', 'additional_attachment'
        ]

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        work_experiences_json = cleaned_data.get('work_experiences_json')
        currently_studying = cleaned_data.get('currently_studying')
        study_to_date = cleaned_data.get('study_to_date')

        # If experienced, at least 1 work experience entry is required
        if status == 'experienced':
            if not work_experiences_json:
                raise ValidationError("Please add at least one work experience entry.")

        # If not currently studying, study_to_date is required
        if status and not currently_studying and not study_to_date:
            raise ValidationError("Please specify the end date or check 'Currently studying'.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Parse the JSON work experiences from the form
        work_experiences_json = self.cleaned_data.get('work_experiences_json')
        if work_experiences_json:
            import json
            try:
                instance.work_experiences = json.loads(work_experiences_json)
            except (json.JSONDecodeError, ValueError):
                instance.work_experiences = []
        
        if commit:
            instance.save()
        return instance
