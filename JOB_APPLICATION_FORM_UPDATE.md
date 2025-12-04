# Job Application Form — Update Summary

## Overview
The internship and job application forms have been completely redesigned to support both fresher and experienced applicants with dynamic field visibility and improved UX.

---

## 1. Database Models Updated

### InternshipApplication Model (`portal/models.py`)

#### New Fields Added:
- **Personal Information:**
  - `first_name` (CharField) - Separate from full_name for better organization
  - `last_name` (CharField)
  - `city`, `state`, `country` (CharField) - Split address fields

- **Experience Status:**
  - `status` (CharField) - Radio choices: Fresher / Experienced

- **Education Details:**
  - `school_name` (CharField) - School/College Name
  - `city_of_study` (CharField) - City
  - `degree` (CharField) - Degree type
  - `field_of_study` (CharField) - Major/Field of Study
  - `study_from_date` (DateField) - From date
  - `study_to_date` (DateField) - To date (optional if currently studying)
  - `currently_studying` (BooleanField) - Checkbox for current students

- **Skills & Profile:**
  - `skills` (TextField) - Skills/tags (optional)
  - `linkedin_profile` (URLField) - LinkedIn profile URL

- **Optional Sections:**
  - `internships` (TextField) - Optional for freshers
  - `work_experiences` (JSONField) - For experienced applicants

- **Additional Information:**
  - `additional_questions` (TextField) - 0-2000 characters
  - `message_to_manager` (TextField) - Message to hiring manager (0-2000 chars)
  - `additional_attachment` (FileField) - Optional PDF/DOCX/DOC/PNG/JPG (max 5MB)

#### Removed Fields:
- `full_name`, `education`, `major`, `preferred_role`, `availability`, `duration`, `start_date`, `cover_letter`, `additional_info`

---

### JobApplication Model (`portal/models.py`)

#### New Fields Added:
- **Personal Information:**
  - `first_name`, `last_name` (CharField)
  - `city`, `state`, `country` (CharField)

- **Experience Status:**
  - `status` (CharField) - Fresher / Experienced radio buttons

- **Education Details:**
  - Same as InternshipApplication (required for all)
  - `school_name`, `city_of_study`, `degree`, `field_of_study`, `study_from_date`, `study_to_date`, `currently_studying`

- **Work Experience (Conditional):**
  - `work_experiences` (JSONField) - Array of work experience entries
  - Each entry contains: job_title, company_name, from_date, to_date, currently_working, city, description
  - **Required for experienced applicants** (minimum 1 entry)
  - **Limit: 3 entries maximum**

- **Skills & Profile:**
  - `skills` (TextField) - Optional
  - `linkedin_profile` (URLField) - Optional

- **Additional Information:**
  - `screening_questions` (TextField) - 0-2000 characters
  - `message_to_manager` (TextField) - 0-2000 characters
  - `additional_attachment` (FileField) - Optional (max 5MB)

#### Removed Fields:
- `full_name`, `education`, `major`, `experience_years`, `current_position`, `current_company`, `preferred_role`, `employment_type`, `salary_expectation`, `availability_date`, `work_authorization`, `cover_letter`, `portfolio_url`, `additional_info`

---

## 2. Forms Created

### New File: `portal/forms.py`

#### InternshipApplicationForm
- Auto-generates from InternshipApplication model
- Custom validation for education dates
- Handles resume upload (PDF, DOC, DOCX max 2MB)
- Optional attachments (PDF, DOCX, DOC, PNG, JPG max 5MB)
- Bootstrap CSS styling with `.form-control` classes

#### JobApplicationForm
- Similar to InternshipApplicationForm
- Additional handling for work_experiences as JSON
- Validates that experienced applicants have at least 1 work experience entry
- Custom save() method to handle work experience JSON serialization

---

## 3. Templates Updated

### InternshipApplication Template
**File:** `portal/templates/brand_new_site/internship_application.html`

**Sections:**
1. Basic Details (First Name, Last Name, Phone, Email, Address, City, State, Country)
2. Resume Upload (Required, max 2MB)
3. Experience Status (Radio buttons: Fresher / Experienced)
4. Education Details (School, City, Degree, Field, Dates)
5. Skills (Optional)
6. LinkedIn Profile (Optional)
7. Internships (Conditional - only for Freshers)
8. Additional Questions (Optional, 0-2000 chars)
9. Message to Hiring Manager (Optional, 0-2000 chars)
10. Additional Attachments (Optional, max 5MB)

**JavaScript Features:**
- Conditional field visibility based on fresher/experienced status
- File input enhancement showing selected filename
- Parallax background animation
- Form validation

---

### JobApplication Template
**File:** `portal/templates/brand_new_site/job_application.html`

**Sections:**
1. Basic Details (Same as internship)
2. Resume Upload (Required, max 2MB)
3. Experience Status (Radio buttons)
4. Education Details (Required for all)
5. **Work Experience (Conditional - only for Experienced)**
   - Each entry: Job Title, Company, From/To Dates, Currently Working checkbox, City, Description
   - "Add Work Experience" button (max 3 entries)
   - "Remove" button for each entry
6. Skills (Optional)
7. LinkedIn Profile (Optional)
8. Screening Questions (Optional, 0-2000 chars)
9. Message to Hiring Manager (Optional, 0-2000 chars)
10. Additional Attachments (Optional, max 5MB)

**JavaScript Features:**
- Dynamic work experience entry management
- Add/Remove work experience entries (limit 3)
- Save work experience as JSON in hidden field
- Conditional visibility of work experience section
- Disable "To Date" when "Currently work here" is checked

---

## 4. Views Updated

### InternshipApplication View
**File:** `portal/views.py`

```python
def internship_application(request, internship_id):
    from .forms import InternshipApplicationForm
    
    internship = get_object_or_404(PortalInternship, id=internship_id, is_active=True)

    if request.method == 'POST':
        form = InternshipApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.internship = internship
            application.supplier = internship.supplier
            application.save()
            messages.success(request, 'Your internship application has been submitted successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = InternshipApplicationForm()

    context = {'internship': internship, 'form': form}
    return render(request, 'brand_new_site/internship_application.html', context)
```

### JobApplication View
**File:** `portal/views.py`

```python
def job_application(request, job_id):
    from .forms import JobApplicationForm
    import json
    
    job = get_object_or_404(PortalJob, id=job_id, is_active=True)

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.supplier = job.supplier
            application.save()
            messages.success(request, 'Your job application has been submitted successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = JobApplicationForm()

    context = {'job': job, 'form': form}
    return render(request, 'brand_new_site/job_application.html', context)
```

---

## 5. Dynamic Field Behavior

### When Fresher is Selected:
✅ Show Education Details (required)
✅ Show Skills (optional)
✅ Show LinkedIn Profile (optional)
✅ Show Internships section (optional)
❌ HIDE Work Experience section completely

### When Experienced is Selected:
✅ Show Education Details (required)
✅ Show Work Experience section (required - minimum 1 entry)
✅ Show Skills (optional)
✅ Show LinkedIn Profile (optional)
❌ HIDE Internships section

---

## 6. Validation Rules

### InternshipApplication:
- **Required Fields:** First Name, Last Name, Phone, Email, Resume, School Name, City of Study, Degree, Field of Study, Study From Date
- **Conditional Required:** Study To Date (if not currently studying)
- **File Validation:** Resume max 2MB (PDF, DOC, DOCX); Additional attachment max 5MB (PDF, DOCX, DOC, PNG, JPG)
- **Character Limits:** Additional Questions and Message to Manager (0-2000 chars each)

### JobApplication:
- **Required Fields:** Same as internship + Status field
- **Experience-Based Requirements:**
  - **Fresher:** All above fields
  - **Experienced:** All above fields + At least 1 work experience entry
- **Work Experience Entry:** Job Title and Company Name are required; From Date required; To Date optional if "Currently work here" is checked
- **Validation:** Work experience JSON array must have at least 1 entry for experienced applicants

---

## 7. Database Migrations

**Migration File:** `portal/migrations/0008_remove_internshipapplication_additional_info_and_more.py`

### Changes:
- Removed 14 fields from InternshipApplication
- Removed 14 fields from JobApplication
- Added 20 new fields to InternshipApplication
- Added 22 new fields to JobApplication
- New JSONField for work_experiences
- New status choices (Fresher/Experienced)

**Migration Status:** ✅ Applied successfully

---

## 8. UI/UX Enhancements

### Visual Features:
- Industrial themed design with custom CSS variables
- Responsive layout (mobile-friendly)
- Section-based form organization
- Icons for visual hierarchy
- Color-coded buttons (primary = blue, danger = red)
- Smooth animations and transitions

### File Input Enhancement:
- Custom styled file inputs
- Display selected filename after upload
- Accept only specified file types

### Form Handling:
- Real-time field visibility updates
- JSON serialization for work experience entries
- Bootstrap form classes for consistency
- Error messages for failed validations

---

## 9. Key Features

### For Freshers:
- Simplified form focusing on education and skills
- Optional internship history section
- No work experience requirement
- Perfect for students and entry-level candidates

### For Experienced Candidates:
- Detailed work experience section with multiple entries
- Job title, company, dates, location, and description
- "Currently working here" checkbox to skip end date
- LinkedIn profile linking
- Professional message to hiring manager

### Common to Both:
- Educational background (required)
- Resume upload (required, 2MB max)
- Skills and LinkedIn profile (optional)
- Additional attachments support (5MB max)
- Message to hiring manager (0-2000 chars)
- Comprehensive screening questions section

---

## 10. Files Modified/Created

### Created:
- ✅ `portal/forms.py` - New forms for applications

### Modified:
- ✅ `portal/models.py` - Updated InternshipApplication and JobApplication models
- ✅ `portal/templates/brand_new_site/internship_application.html` - Updated template with new form
- ✅ `portal/templates/brand_new_site/job_application.html` - Updated template with conditional work experience section
- ✅ `portal/views.py` - Updated views to use new forms
- ✅ `portal/migrations/0008_...` - Database migration

---

## 11. Testing Recommendations

1. **Test as Fresher:**
   - Fill form as fresher, verify work experience section is hidden
   - Verify internship section is shown and can be filled

2. **Test as Experienced:**
   - Fill form as experienced, verify work experience section is shown
   - Test adding multiple work experience entries (up to 3)
   - Test "Currently work here" checkbox
   - Verify internship section is hidden

3. **Test File Uploads:**
   - Resume upload (max 2MB)
   - Additional attachments (max 5MB)
   - Invalid file types

4. **Test Validations:**
   - Required fields
   - Date format validation
   - Character limits (0-2000 for text areas)
   - At least 1 work experience for experienced applicants

5. **Test Responsive Design:**
   - Mobile devices
   - Tablets
   - Desktop

---

## 12. Deployment Notes

1. **Database Migration:** Run `python manage.py migrate portal` to apply changes
2. **Static Files:** No new static files required (uses existing CSS)
3. **Dependencies:** No new Python dependencies required
4. **Environment Variables:** No new environment variables needed
5. **Testing:** Run unit tests to ensure compatibility

---

## 13. Future Enhancements

- File upload validation with file size checking
- Email confirmation after submission
- Application status tracking
- Applicant dashboard to view submitted applications
- Export applications to CSV/PDF
- Advanced search and filtering in admin panel

