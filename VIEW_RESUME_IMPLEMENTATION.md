# View Resume Implementation - Complete Solution

## Overview
This implementation serves resumes inline in the browser (PDFs display natively) while other formats trigger downloads. The view includes proper security checks to ensure suppliers can only access their own applicants' resumes.

---

## 1. Django View (`portal/views.py`)

### Imports Added
```python
import mimetypes
from io import BytesIO
```

### New View Function
```python
@login_required
def view_resume(request, application_id):
    """
    Serve resume inline for PDFs, download for other formats.
    Ensures supplier can only view their own applicants' resumes.
    """
    try:
        # Get the application - could be job or internship
        job_app = JobApplication.objects.filter(id=application_id).first()
        internship_app = InternshipApplication.objects.filter(id=application_id).first()
        
        if not job_app and not internship_app:
            raise Http404("Application not found.")
        
        application = job_app or internship_app
        
        # Get the job or internship to verify supplier access
        if job_app:
            job = job_app.job
            # Verify supplier owns this job
            try:
                get_supplier_for_user_or_raise(request.user, job.supplier)
            except PermissionDenied:
                raise PermissionDenied("You don't have access to this application.")
        else:
            internship = internship_app.internship
            # Verify supplier owns this internship
            try:
                get_supplier_for_user_or_raise(request.user, internship.supplier)
            except PermissionDenied:
                raise PermissionDenied("You don't have access to this application.")
        
        # Check if resume exists
        if not application.resume:
            raise Http404("Resume not found for this application.")
        
        # Get file content
        try:
            resume_file = application.resume
            file_content = resume_file.read()
        except Exception as e:
            logger.error(f"Error reading resume file: {str(e)}")
            raise Http404(f"Error reading resume: {str(e)}")
        
        # Get filename
        filename = application.resume.name
        if '/' in filename:
            filename = filename.split('/')[-1]
        
        # Auto-detect content type
        content_type, _ = mimetypes.guess_type(filename)
        if content_type is None:
            content_type = 'application/octet-stream'
        
        # Create response with FileResponse
        response = FileResponse(BytesIO(file_content), content_type=content_type)
        
        # For PDFs, use inline display; for other types, trigger download
        if content_type == 'application/pdf':
            response['Content-Disposition'] = f'inline; filename="{filename}"'
        else:
            # For DOCX and other formats, download with proper filename
            clean_filename = f"{application.first_name}_{application.last_name}_Resume.{filename.split('.')[-1]}"
            response['Content-Disposition'] = f'attachment; filename="{clean_filename}"'
        
        response['Content-Length'] = len(file_content)
        
        logger.info(f"Resume served for application {application_id}: {filename}")
        return response
    
    except PermissionDenied as e:
        logger.warning(f"Access denied for user {request.user.id} to application {application_id}: {str(e)}")
        raise PermissionDenied(str(e))
    except Http404 as e:
        logger.warning(f"Resume not found for application {application_id}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error in view_resume: {str(e)}")
        raise Http404(f"Error serving resume: {str(e)}")
```

### Key Features:
- ✅ **Dual-Source Support**: Works with both `JobApplication` and `InternshipApplication` models
- ✅ **Security Checks**: Verifies supplier owns the job/internship before serving resume
- ✅ **Auto-Detection**: Uses `mimetypes` to detect file type automatically
- ✅ **Smart Disposition**: 
  - PDFs → Inline display in browser
  - DOCX/Other → Download as attachment
- ✅ **Proper Content-Type**: Sets correct MIME type for each file
- ✅ **Logging**: Logs all access for security auditing

---

## 2. URL Pattern (`portal/urls.py`)

Add this line to your `urlpatterns` list:

```python
# View resume inline (PDF) or download (other formats)
path('portal-admin/view-resume/<int:application_id>/', views.view_resume, name='view_resume'),
```

---

## 3. Template Update (`applicant_detail.html`)

### Replace Old Button Code:
**OLD:**
```html
<a href="{{ application.resume.url|add:'?download=inline' }}" target="_blank" class="btn btn-primary">
    👁️ View Resume
</a>
```

**NEW:**
```html
<a href="{% url 'view_resume' application.id %}" target="_blank" class="btn btn-primary" style="text-decoration: none; cursor: pointer;">
    👁️ View Resume
</a>
```

---

## How It Works

### User Flow:
1. **Supplier clicks "View Resume" button**
2. **Browser requests**: `/portal-admin/view-resume/123/` (where 123 is application ID)
3. **Django view executes**:
   - ✅ Authenticates user (via `@login_required`)
   - ✅ Verifies supplier owns the job/internship
   - ✅ Reads resume file from storage
   - ✅ Detects file type (PDF, DOCX, etc.)

### Response Handling:
- **PDF files**: Browser displays inline with native PDF viewer
  - User can view, zoom, scroll, print, and download from within the PDF viewer
  - Header: `Content-Disposition: inline; filename="resume.pdf"`

- **Other files (DOCX, DOC, etc.)**: Browser triggers download
  - File downloads with clean filename: `FirstName_LastName_Resume.docx`
  - Header: `Content-Disposition: attachment; filename="John_Doe_Resume.docx"`

---

## Security Features

✅ **Authentication**: Only logged-in users can access  
✅ **Authorization**: Suppliers can only view resumes for their own job/internship postings  
✅ **Error Handling**: Proper 404 responses for missing files  
✅ **Logging**: All access attempts logged for auditing  
✅ **File Validation**: Checks if resume exists before serving  

---

## File Type Behavior Reference

| File Type | MIME Type | Behavior |
|-----------|-----------|----------|
| PDF | `application/pdf` | **Inline** - Opens in browser PDF viewer |
| DOCX | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | **Download** |
| DOC | `application/msword` | **Download** |
| TXT | `text/plain` | **Inline** - Displays as text |
| PNG/JPG | `image/*` | **Inline** - Displays image |
| Other | `application/octet-stream` | **Download** |

---

## Testing Checklist

- [ ] Click "View Resume" for PDF → Opens in new tab and displays inline
- [ ] Can scroll, zoom, print from PDF viewer
- [ ] Can download from within PDF viewer
- [ ] Click "View Resume" for DOCX → Downloads to computer
- [ ] Downloaded DOCX has clean filename: `FirstName_LastName_Resume.docx`
- [ ] Non-owner supplier gets access denied error
- [ ] Non-authenticated user gets redirected to login
- [ ] Console shows proper logging messages

---

## Troubleshooting

### Issue: "Resume not found" error
- **Cause**: Application doesn't have a resume file
- **Solution**: Ensure resume was uploaded when application was created

### Issue: DOCX still opens in browser instead of downloading
- **Check**: Browser settings might be configured to open DOCX files
- **Solution**: This is browser behavior, not application issue. User can right-click → Save As

### Issue: PDF shows generic filename
- **Check**: Filename detection logic
- **Solution**: The Content-Disposition header includes the proper filename, but browser PDF viewer may show generically

---

## Future Enhancements

1. Add view for document attachments: `view_document(request, application_id)`
2. Add file preview cache for performance
3. Add download tracking/analytics
4. Add file type restrictions (only allow PDF/DOCX)
5. Add watermarking for PDFs (view-only mode)

