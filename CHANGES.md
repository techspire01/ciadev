# Quick Reference: What Changed

## Summary
Fixed delete functionality (was broken) and added preview capability for applicant resumes and documents.

## Files Changed: 3

### 1. portal/views.py
**Lines 781-825**: Added `preview_application_file()` function
```
- New endpoint handler for PDF preview
- Returns signed URL from Supabase
- Validates supplier ownership
- Returns JSON: {success, url, filename, file_type}
```

**Lines 829-920**: Enhanced `delete_job_applicant()` function  
```
- Now supports 3 deletion modes:
  1. delete_resume_only=true → Remove only resume
  2. delete_attachment_only=true → Remove only attachment
  3. (default) → Remove everything
- Added proper try-catch error handling
- Added Django messages (success/error/warning)
- Added logging for audit trail
- Added JSON responses for AJAX calls
- Detects is_ajax and responds accordingly
```

**Lines 923-1014**: Enhanced `delete_internship_applicant()` function
```
- Same improvements as job delete function
- Supports same 3 deletion modes
- Same error handling, logging, messaging
```

### 2. portal/urls.py
**New route** (around line 50):
```python
path(
    'portal-admin/preview/<str:application_type>/<int:application_id>/<str:file_type>/',
    views.preview_application_file,
    name='preview_application_file'
)
```

### 3. portal/templates/brand_new_site/applicant_detail.html

**Lines 418-460**: Reorganized Document Section
```
Resume:
  - 👁️ Preview Resume button (new)
  - 📥 Download Resume link (existing)
  - 🗑️ Delete Resume Only button (moved from danger zone)

Additional Document (if attached):
  - 👁️ Preview Document button (new)
  - 📥 Download Document link (existing)  
  - 🗑️ Delete Document Only button (new)
```

**Lines 465-469**: Added Preview Modal HTML
```html
<div id="previewModal"> <!-- Modal for PDF preview -->
    <button onclick="closePreview()">✕ Close</button>
    <iframe id="previewFrame"></iframe>
</div>
```

**Lines 471-481**: Updated Danger Zone
```
- Removed individual delete buttons (moved to document sections)
- Kept only "Delete Entire Application" button
- Added clear warning text
```

**Lines 502-541**: Added `previewFile()` JavaScript function
```
- Calls /portal-admin/preview/TYPE/ID/FILE/ endpoint
- Receives signed URL from backend
- Displays PDF in modal using Google Docs Viewer
- Shows modal with loading state
- Handles errors gracefully
```

**Lines 544-548**: Added `closePreview()` JavaScript function
```
- Closes preview modal
- Clears iframe
- Resets display state
```

**Lines 550-567**: Added event listeners
```
- Click outside modal to close
- Escape key to close modal
```

**Lines 570-595**: Added `deleteFile()` JavaScript function
```
- AJAX POST with delete_resume_only OR delete_attachment_only
- Receives JSON response
- Shows success/error alerts
- Reloads page on success
```

**Lines 598-606**: Updated `deleteApplication()` JavaScript function
```
- Changed from form submission to AJAX
- Now posts as JSON request
- Handles response and redirects on success
- Shows alerts on failure
```

## What Works Now

✅ **Preview** - Click preview button, see PDF in modal, close with button/Escape/click-outside
✅ **Delete Resume** - Removes resume, keeps app and attachment, page reloads
✅ **Delete Attachment** - Removes attachment, keeps app and resume, page reloads  
✅ **Delete App** - Removes everything, redirects to applicant list
✅ **Errors** - All operations logged, errors shown to user
✅ **Security** - Only suppliers who posted job/internship can manage

## How to Test

1. Start server: `python manage.py runserver`
2. Login as supplier at `/portal-admin/`
3. Go to a job or internship
4. Click on an applicant
5. Test the new buttons:
   - 👁️ Preview Resume/Document
   - 🗑️ Delete Resume/Document Only
   - ⚠️ Delete Entire Application

## Files Created (Optional)

- `verify_implementation.py` - Verify all code is in place
- `test_delete_and_preview.py` - Django unit tests
- `DELETE_PREVIEW_IMPLEMENTATION.md` - Full documentation
