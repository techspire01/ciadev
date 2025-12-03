from django.urls import path, re_path
from . import views

urlpatterns = [
    path('career@cianext/', views.brand_new_site_dashboard, name='dashboard'),
    path('details/', views.details, name='details'),
    path('brand-new-site/', views.brand_new_site_dashboard, name='brand_new_site_dashboard'),
    path('job_portal_admin/', views.job_portal_admin, name='job_portal_admin'),
    path('admin/ui-model/', views.job_admin, name='job_admin'),

    # Internship management URLs (using portal-admin prefix to avoid conflict with Django Admin)
    path('portal-admin/edit-internship/<int:id>/', views.edit_internship, name='edit_internship'),
    path('portal-admin/delete-internship/<int:id>/', views.delete_internship, name='delete_internship'),
    path('portal-admin/toggle-internship/<int:id>/', views.toggle_internship, name='toggle_internship'),
    # Job admin (server-side)
    path('portal-admin/edit-job/<int:id>/', views.edit_job, name='edit_job'),
    path('portal-admin/delete-job/<int:id>/', views.delete_job, name='delete_job'),
    path('portal-admin/toggle-job/<int:id>/', views.toggle_job, name='toggle_job'),
    # API endpoints for internship management (kept for backward compatibility if needed)
    path('api/internships/', views.get_internships, name='get_internships'),
    path('api/internships/add/', views.add_internship, name='add_internship'),
    path('api/internships/<int:internship_id>/update/', views.update_internship, name='update_internship'),
    path('api/internships/<int:internship_id>/toggle/', views.toggle_internship_status, name='toggle_internship_status'),
    # API endpoints for job management
    path('api/jobs/add/', views.add_job_api, name='add_job'),
    path('api/jobs/<int:job_id>/update/', views.update_job_api, name='update_job'),
    path('api/jobs/<int:job_id>/toggle/', views.toggle_job_status_api, name='toggle_job_status'),
    path('api/jobs/<int:job_id>/delete/', views.delete_job_api, name='delete_job_api'),

    # Application forms
    path('internship/<int:internship_id>/apply/', views.internship_application, name='internship_application'),
    path('job/<int:job_id>/apply/', views.job_application, name='job_application'),
    
    # View applicants for jobs and internships
    path('portal-admin/job/<int:job_id>/applicants/', views.view_job_applicants, name='view_job_applicants'),
    path('portal-admin/internship/<int:internship_id>/applicants/', views.view_internship_applicants, name='view_internship_applicants'),
    
    # View individual applicant details
    path('portal-admin/job/<int:job_id>/applicant/<int:application_id>/', views.view_job_applicant_detail, name='view_job_applicant_detail'),
    path('portal-admin/internship/<int:internship_id>/applicant/<int:application_id>/', views.view_internship_applicant_detail, name='view_internship_applicant_detail'),
    
    # Preview application files (resume, attachment)
    path('portal-admin/preview/<str:application_type>/<int:application_id>/<str:file_type>/', views.preview_application_file, name='preview_application_file'),
    
    # Delete applicants
    path('portal-admin/job/<int:job_id>/applicant/<int:application_id>/delete/', views.delete_job_applicant, name='delete_job_applicant'),
    path('portal-admin/internship/<int:internship_id>/applicant/<int:application_id>/delete/', views.delete_internship_applicant, name='delete_internship_applicant'),
    
    # Protected media download endpoint
    re_path(r'^protected-media/(?P<path>.+)/$', views.protected_media, name='protected_media'),
   ]
