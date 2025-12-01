# TODO: Remove AJAX Mode and localStorage Mode for Job Portal Admin

## Tasks
- [x] Fix 1: Update `job_portal_admin` view in `portal/views.py` to query and send both internships and jobs to the template.
- [x] Fix 2: In `portal/static/brand_new_site/js/admin.js`, delete `loadInternships()` function, remove `loadJobs()` from DOMContentLoaded, and ensure `renderJobs()` is not called.
- [x] Fix 3: In `portal/templates/brand_new_site/job_portal_admin.html`, replace the jobs table structure with server-side rendering using `{% for job in jobs %}` loop as specified.
- [ ] Followup: Run the Django server and verify the admin page loads internships and jobs server-side without AJAX or localStorage.

# TODO: Create HTML Application Forms for Internship and Job Applications

## Tasks
- [x] Create internship_application.html with form fields for personal info, education, skills, internship preferences, and document upload
- [x] Create job_application.html with form fields for personal info, education, experience, job preferences, and document upload
- [x] Match UI theme from dashboard.html including CSS variables, background video, and styling
- [x] Place both files in portal/templates/brand_new_site/ directory
- [x] Followup: Test the forms in browser and verify styling matches dashboard theme
