from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('details/', views.details, name='details'),
    path('brand-new-site/', views.brand_new_site_dashboard, name='brand_new_site_dashboard'),
    path('job_portal_admin/', views.job_portal_admin, name='job_portal_admin'),
    path('admin/ui-model/', views.job_admin, name='job_admin'),
    path('internship_job/', views.internship_job, name='internship_job'),
    # Internship management URLs (using portal-admin prefix to avoid conflict with Django Admin)
    path('portal-admin/edit-internship/<int:id>/', views.edit_internship, name='edit_internship'),
    path('portal-admin/delete-internship/<int:id>/', views.delete_internship, name='delete_internship'),
    path('portal-admin/toggle-internship/<int:id>/', views.toggle_internship, name='toggle_internship'),
    # API endpoints for internship management (kept for backward compatibility if needed)
    path('api/internships/', views.get_internships, name='get_internships'),
    path('api/internships/add/', views.add_internship, name='add_internship'),
    path('api/internships/<int:internship_id>/update/', views.update_internship, name='update_internship'),
    path('api/internships/<int:internship_id>/toggle/', views.toggle_internship_status, name='toggle_internship_status'),
    # API endpoints for job management
    path('api/jobs/add/', views.add_job, name='add_job'),
    path('api/jobs/<int:job_id>/update/', views.update_job, name='update_job'),
    path('api/jobs/<int:job_id>/toggle/', views.toggle_job_status, name='toggle_job_status'),
    path('api/jobs/<int:job_id>/delete/', views.delete_job, name='delete_job'),
   ]
