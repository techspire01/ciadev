from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('details/', views.details, name='details'),
    path('brand-new-site/', views.brand_new_site_dashboard, name='brand_new_site_dashboard'),
    path('job_portal_admin/', views.job_portal_admin, name='job_portal_admin'),
    path('admin/ui-model/', views.job_admin, name='job_admin'),
    path('internship_job/', views.internship_job, name='internship_job'),
   ]
