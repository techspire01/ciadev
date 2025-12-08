# Multi-Company Access Control Implementation

## Tasks
- [ ] Update portal/models.py: Add supplier ForeignKey to PortalInternship, PortalJob, InternshipApplication, JobApplication
- [ ] Update portal/views.py: Filter queries by supplier in job_portal_admin and other views; set supplier when creating jobs/internships/applications
- [ ] Create and run migrations for model changes
- [ ] Test the isolation (each supplier sees only their data)
