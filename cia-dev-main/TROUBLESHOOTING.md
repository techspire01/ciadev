# Troubleshooting Guide

## Preview Not Working

### Issue: Preview modal doesn't open
**Possible Causes:**
- JavaScript error in console
- CSRF token not found
- Endpoint not registered
- Supplier not logged in

**Debug Steps:**
1. Open browser DevTools (F12)
2. Click Console tab
3. Click preview button
4. Look for JavaScript errors
5. Check Network tab for failed requests

**Solution:**
- Ensure @supplier_required decorator is on view
- Check CSRF token is in template: `{{ csrf_token }}`
- Verify URL pattern in urls.py matches template URL
- Ensure supplier is logged in

### Issue: Modal shows but PDF doesn't display
**Possible Causes:**
- Signed URL invalid
- PDF file doesn't exist in Supabase
- Google Docs Viewer down (unlikely)
- File type not supported

**Debug Steps:**
1. Right-click on blank iframe
2. Select "Open Frame in New Tab"
3. Check if Google Docs Viewer error page appears
4. In Network tab, check if `/portal-admin/preview/` returns 200
5. Check response contains valid `url` field

**Solution:**
- Verify file exists in Supabase bucket
- Check `settings.SUPABASE_URL` is correct
- Verify `SERVICE_KEY` permissions allow reading files
- Try PDF from different application

### Issue: Preview returns 404
**Possible Causes:**
- Supplier doesn't own the job/internship
- Application ID wrong
- File type not 'resume' or 'attachment'
- Application deleted

**Debug Steps:**
1. Check browser Network tab for 404
2. Verify application_id in URL
3. Verify application_type is 'job' or 'internship'
4. Verify file_type is 'resume' or 'attachment'
5. Verify you're logged in as correct supplier

**Solution:**
- Only suppliers who posted the job/internship can preview
- Check application still exists
- Verify file field not empty

---

## Delete Not Working

### Issue: Delete button doesn't do anything
**Possible Causes:**
- JavaScript error
- Confirmation dialog rejected
- Network error
- Endpoint error

**Debug Steps:**
1. Open DevTools Console
2. Click delete button
3. Look for JavaScript errors
4. Check if confirmation dialog appeared
5. Check Network tab for failed POST request

**Solution:**
- Press OK on confirmation dialog
- Check Console for error messages
- Verify Django server is running
- Check Django console for server-side errors

### Issue: Delete returns error message
**Possible Causes:**
- Storage failure
- Database failure
- Permission denied
- File doesn't exist

**Debug Steps:**
1. Note the exact error message
2. Check Django console for detailed error
3. Verify file exists in Supabase
4. Verify storage bucket is accessible
5. Check supplier ownership

**Solution:**
- Check Supabase credentials in .env
- Verify SERVICE_KEY has delete permissions
- Ensure file path is correct
- Check database record exists

### Issue: File deleted but page doesn't update
**Possible Causes:**
- Page reload failed
- File deleted from storage but not from DB
- File deleted from DB but not from storage

**Debug Steps:**
1. Manually refresh page
2. Check Supabase bucket for file
3. Check database record for file reference
4. Check Django logs for errors

**Solution:**
- Clear browser cache
- Hard refresh (Cmd+Shift+R on Mac)
- Check logs for transaction failures

### Issue: Application deleted but still visible
**Possible Causes:**
- Page didn't reload
- Delete transaction failed
- Browser cache

**Debug Steps:**
1. Manually navigate to applicant list
2. Check if application gone
3. Look for error in Django console
4. Check database directly

**Solution:**
- Page reload should fix it
- Check for database transaction errors
- Manually delete if necessary

---

## Authorization Issues

### Issue: Getting "Access denied" or 404
**Possible Causes:**
- Not logged in as supplier
- Logged in as wrong supplier
- Job/internship doesn't belong to supplier
- Application doesn't belong to job/internship

**Debug Steps:**
1. Check if logged in at top of page
2. Check username matches job poster
3. Navigate to Jobs → click your job
4. Click applicants → check it's your job
5. Verify application is for your job

**Solution:**
- Log in as correct supplier
- Only suppliers can access their own applicants
- Create a test job and application if needed

### Issue: Logged in but getting 404
**Possible Causes:**
- ID mismatch
- Application type wrong (job vs internship)
- Record deleted

**Debug Steps:**
1. Copy application ID from URL
2. Check URL format: /portal/TYPE/ID/applicant/APP_ID/delete/
3. Verify application exists in list
4. Check database for record

**Solution:**
- Ensure ID matches application being accessed
- Refresh list and try again
- Create new application if deleted

---

## Logging Issues

### Issue: No success/error messages appearing
**Possible Causes:**
- Messages middleware not configured
- Messages not displayed in template
- Template extends wrong base
- JavaScript alerts not firing

**Debug Steps:**
1. Check Django settings for MESSAGE_STORAGE
2. Check template includes messages display
3. Check browser alerts are enabled
4. Look in Django console for message setup

**Solution:**
- Verify INSTALLED_APPS includes 'django.contrib.messages'
- Ensure template has `{% if messages %}`
- Check browser popup blockers
- Reload page to see messages

### Issue: No logs in Django console
**Possible Causes:**
- Logging not configured
- Log level too high
- Logger name wrong
- No logger setup

**Debug Steps:**
1. Check proj/settings.py for LOGGING dict
2. Check 'cai_security' logger is configured
3. Look for import of logger in views.py
4. Check log level (DEBUG, INFO, ERROR)

**Solution:**
- Ensure logger is imported: `logger = logging.getLogger(...)`
- Add logging.basicConfig() if logger not setup
- Check that logging.info() or logging.error() is called

---

## Storage Issues

### Issue: Files not actually deleted from Supabase
**Possible Causes:**
- Storage backend delete() not called
- Storage permissions wrong
- File path wrong
- Supabase credentials wrong

**Debug Steps:**
1. Check Supabase bucket in dashboard
2. Look for file in folder structure
3. Verify SERVICE_KEY permissions
4. Check SUPABASE_BUCKET setting

**Solution:**
- Verify storage.delete() is called in views
- Check .env SUPABASE_SERVICE_KEY is correct
- Verify bucket name in settings
- Check file path in database

### Issue: Signed URLs not working
**Possible Causes:**
- SUPABASE_BUCKET wrong
- SERVICE_KEY wrong
- File path doesn't match Supabase path
- URL expired

**Debug Steps:**
1. Copy signed URL from response
2. Open in new tab
3. Check for Supabase error
4. Verify bucket and file path in URL
5. Check URL timestamp vs current time

**Solution:**
- Generate new signed URL (expires after 1 hour)
- Verify SUPABASE_SIGNED_URL_EXPIRES setting
- Check bucket and path match actual storage structure
- Ensure SERVICE_KEY is valid

---

## Database Issues

### Issue: Application record not deleted
**Possible Causes:**
- Delete transaction failed
- Constraint violation
- Application already deleted
- Database connection error

**Debug Steps:**
1. Check Django console for transaction error
2. Check if application has related records
3. Try delete again
4. Check database directly

**Solution:**
- Look for integrity constraint errors
- Check for orphaned file references
- Restart database connection
- Use Django admin to delete if needed

### Issue: File reference still in database
**Possible Causes:**
- Save not called
- Application query object stale
- Database connection lost
- Transaction rolled back

**Debug Steps:**
1. Check if application.save() is called
2. Reload application from DB
3. Check Django logs for transaction rollback
4. Check database consistency

**Solution:**
- Add explicit save() after field update
- Refresh object: app = Application.objects.get(id=id)
- Check for transaction errors in logs
- Verify database connection

---

## Performance Issues

### Issue: Delete operation slow
**Possible Causes:**
- Large file being deleted
- Network latency
- Database transaction slow
- Multiple files being deleted

**Debug Steps:**
1. Check file size in Supabase
2. Check network latency in DevTools
3. Check query count in Django debug toolbar
4. Time the operation

**Solution:**
- Large files take longer to delete
- Consider async task for bulk operations
- Optimize database queries
- Add progress indicator to UI

---

## Testing Checklist

### Manual Testing
- [ ] Can preview resume?
- [ ] Can preview attachment?
- [ ] Can delete resume only?
- [ ] Can delete attachment only?
- [ ] Can delete entire application?
- [ ] Page reloads after individual delete?
- [ ] Redirects to list after full delete?
- [ ] Success messages appear?
- [ ] Error messages appear on failure?
- [ ] Unauthorized users get 404?
- [ ] Files actually deleted from Supabase?
- [ ] Database records updated correctly?

### Browser Checks
- [ ] Works in Chrome?
- [ ] Works in Safari?
- [ ] Works in Firefox?
- [ ] Works on mobile?
- [ ] Modals display correctly?
- [ ] Buttons are clickable?
- [ ] Forms submit properly?

### Security Checks
- [ ] CSRF token prevents attacks?
- [ ] Only supplier can access own applicants?
- [ ] No sensitive data in error messages?
- [ ] No SQL injection possible?
- [ ] No XSS vulnerabilities?
- [ ] Signed URLs expire?

---

## Getting Help

### Check These First
1. Django console for error messages
2. Browser DevTools Console for JS errors
3. Browser DevTools Network tab for failed requests
4. Django logs file for detailed errors
5. Supabase dashboard for file status
6. Database admin for record status

### Common Error Messages

**"Access denied"**
→ You're not logged in as the supplier who posted this job/internship

**"No resume found to delete"**
→ The resume field is already empty or file doesn't exist

**"Error deleting resume from storage"**
→ Supabase credentials wrong or network issue

**"Application not found"**
→ Application was deleted or ID is wrong

**"Invalid application type"**
→ Type must be 'job' or 'internship'

**"Invalid file type"**
→ File type must be 'resume' or 'attachment'

### Quick Fixes
- Refresh page (F5 or Cmd+R)
- Clear browser cache (Cmd+Shift+Delete)
- Log out and log back in
- Restart Django server
- Check .env file has all variables
- Verify Supabase credentials are correct

---

## Still Not Working?

1. **Verify Setup**
   - [ ] Django server running?
   - [ ] Correct port (8000)?
   - [ ] Logged in as supplier?
   - [ ] Job/internship exists?
   - [ ] Application exists?

2. **Check Logs**
   - [ ] Any errors in Django console?
   - [ ] Any errors in browser console?
   - [ ] Any errors in browser network?
   - [ ] Check server.log file

3. **Review Code**
   - [ ] Check line numbers match yours
   - [ ] Verify all functions present
   - [ ] Confirm no syntax errors
   - [ ] Run verify_implementation.py

4. **Test Components**
   - [ ] Can preview work?
   - [ ] Can you access admin?
   - [ ] Can you delete files manually?
   - [ ] Is Supabase working?

5. **Contact Support**
   - Report specific error message
   - Include Django console output
   - Include browser DevTools errors
   - Include .env settings (without secrets)
