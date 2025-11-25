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
    
    # Supplier detail page with dynamic URL
    path('supplier/<str:supplier_name>/', views.supplier_detail_page, name='supplier_detail_page'),
    
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

    # News gallery page
    path('news-gallery/', views.news_gallery, name='news_gallery'),

    # AJAX endpoint for supplier categories
    path('get_supplier_categories/', views.get_supplier_categories, name='get_supplier_categories'),

    # Profile management
    path('profile/', views.profile_view, name='profile'),
    path('edit-profile/', views.edit_profile_view, name='edit_profile'),
    path('edit-supplier-profile/', views.edit_supplier_profile_view, name='edit_supplier_profile'),
    path('verify-edit-otp/', views.verify_edit_otp, name='verify_edit_otp'),

    # User creation and profile management
    path('create-user/', views.create_user_view, name='create_user'),
    path('verify-user-otp/', views.verify_user_otp, name='verify_user_otp'),
    path('edit-profile/', views.edit_profile_view, name='edit_profile'),
    path('verify-edit-otp/', views.verify_edit_otp, name='verify_edit_otp'),

    # Supplier listing request
    path('request-supplier-listing/', views.request_supplier_listing_view, name='request_supplier_listing'),

    # Contact page
    path('contact/', views.contact, name='contact'),

    # Book showcase page
    path('internship/', views.internship_view, name='internship'),
    path('internship/submit/', views.intern_submit_view, name='intern_submit'),
    path('complaint/submit/', views.submit_complaint, name='submit_complaint'),
    path('book-showcase/', views.book_showcase, name='book_showcase'),
]
