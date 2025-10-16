from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('category/', views.category, name='category'),
    path('announcement/', views.announcement, name='announcement'),
    path('announcement/<int:announcement_id>/', views.announcement_detail, name='announcement_detail'),
    path('signup/', views.signup_view, name='signup'),
    path('suppliers/', views.suppliers, name='suppliers'),
    
    # Authentication URLs
    path("login/", views.login_view, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("password-reset/", views.request_password_reset, name="request_reset"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("resend-otp/", views.resend_otp, name="resend_otp"),
    path("set-new-password/", views.set_new_password, name="set_new_password"),
    path("supplier/<int:supplier_id>/", views.supplier_details, name="supplier_details"),
    path('supplier/<int:supplier_id>/details/', views.supplier_details, name='supplier_details'),
    path('api/companies_by_category/', views.companies_by_category, name='companies_by_category'),

    # New search API endpoint
    path('api/search/', views.search_api, name='search_api'),

    # Search results page
    path('search/', views.search_results, name='search_results'),

    # Photo gallery page
    path('photo-gallery/', views.photo_gallery, name='photo_gallery'),

    # AJAX endpoint for supplier categories
    path('get_supplier_categories/', views.get_supplier_categories, name='get_supplier_categories'),
]
