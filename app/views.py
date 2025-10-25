from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.contrib import messages
from django.db import models
import random
from .models import Supplier, CustomUser, PasswordResetOTP, Announcement, PhotoGallery, Leadership, NewspaperGallery, BookShowcase, SupplierEditRequest, ContactInformation
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Supplier
import json
from .forms import SupplierForm, UserCreationForm, UserProfileForm, SupplierEditForm, SupplierListingForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import datetime
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def index(request):
    # Fetch 3 random suppliers
    all_suppliers = list(Supplier.objects.all())
    if len(all_suppliers) > 3:
        random_suppliers = random.sample(all_suppliers, 3)
    else:
        random_suppliers = all_suppliers

    # Fetch all unique categories from Supplier model (like in category view)
    categories = Supplier.objects.values_list('category', flat=True).distinct()
    categories = [cat for cat in categories if cat]  # Remove None/empty values

    # Count suppliers for each category
    category_counts = {}
    for category_name in categories:
        count = Supplier.objects.filter(category=category_name).count()
        category_counts[category_name] = count

    # Build a dictionary mapping category to its subcategories
    category_subcategories = {}
    for category_name in categories:
        sub_cats = set()
        suppliers_in_cat = Supplier.objects.filter(category=category_name)
        for i in range(1, 4):
            sub_cats.update(suppliers_in_cat.values_list(f'sub_category{i}', flat=True).distinct())
        sub_cats.discard(None)
        category_subcategories[category_name] = sorted(sub_cats)
    
    # Fetch book showcase images
    book_showcase_images = BookShowcase.objects.all()

    context = {
        'user': request.user,
        'featured_suppliers': random_suppliers,
        'categories': categories,
        'category_counts': category_counts,
        'category_subcategories': category_subcategories,
        'book_showcase_images': book_showcase_images,
    }
    return render(request, "index.html", context)

def about(request):
    # Fetch latest 6 images from PhotoGallery
    latest_photos = PhotoGallery.objects.all()[:6]
    total_photos = PhotoGallery.objects.count()

    # Fetch latest 6 newspaper cuttings from NewspaperGallery
    latest_newspapers = NewspaperGallery.objects.all()[:6]
    total_newspapers = NewspaperGallery.objects.count()

    # Fetch all leadership members
    leadership_members = Leadership.objects.all()

    context = {
        'latest_photos': latest_photos,
        'total_photos': total_photos,
        'show_view_more': total_photos > 6,
        'latest_newspapers': latest_newspapers,
        'total_newspapers': total_newspapers,
        'show_newspaper_view_more': total_newspapers > 6,
        'leadership_members': leadership_members
    }
    return render(request, "about.html", context)

def announcement(request):
    # Get filter parameters from request
    show_inactive = request.GET.get('show_inactive', 'false').lower() == 'true'
    filter_type = request.GET.get('filter', 'all')
    
    # Base queryset
    if show_inactive:
        announcements = Announcement.objects.all().order_by('-date')
    else:
        announcements = Announcement.objects.filter(is_active=True).order_by('-date')
    
    # Apply additional filters
    if filter_type == 'critical':
        announcements = announcements.filter(is_critical=True)
    elif filter_type == 'latest':
        announcements = announcements[:10]  # Show only latest 10
    
    critical_announcement = announcements.filter(is_critical=True).first()
    
    # Get latest 3 announcements for the sidebar
    latest_announcements = Announcement.objects.filter(is_active=True).order_by('-date')[:3]
    
    context = {
        'announcements': announcements,
        'critical_announcement': critical_announcement,
        'latest_announcements': latest_announcements,
        'show_inactive': show_inactive,
        'current_filter': filter_type
    }
    return render(request, "announcement.html", context)

def announcement_detail(request, announcement_id):
    try:
        announcement = Announcement.objects.get(id=announcement_id)
        latest_announcements = Announcement.objects.filter(is_active=True).order_by('-date')[:3]
        
        context = {
            'announcement': announcement,
            'latest_announcements': latest_announcements
        }
        return render(request, "announcement_detail.html", context)
    except Announcement.DoesNotExist:
        return redirect('announcement')

def category(request):
    # Fetch all unique categories from Supplier model
    categories = Supplier.objects.values_list('category', flat=True).distinct()
    categories = [cat for cat in categories if cat]  # Remove None/empty values

    # Count suppliers for each category
    category_counts = {}
    for category_name in categories:
        count = Supplier.objects.filter(category=category_name).count()
        category_counts[category_name] = count

    # Build a dictionary mapping category to its subcategories
    category_subcategories = {}
    for category_name in categories:
        sub_cats = set()
        suppliers_in_cat = Supplier.objects.filter(category=category_name)
        for i in range(1, 4):
            sub_cats.update(suppliers_in_cat.values_list(f'sub_category{i}', flat=True).distinct())
        sub_cats.discard(None)
        category_subcategories[category_name] = sorted(sub_cats)
    
    context = {
        'categories': categories,
        'category_counts': category_counts,
        'category_subcategories': category_subcategories,
    }
    return render(request, "category.html", context)

def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.email}!")
                return redirect('index')
            else:
                messages.error(request, "Invalid email or password.")
        except Exception as e:
            messages.error(request, "An error occurred. Please try again.")
            
    return render(request, "login.html")

def signup_view(request):
    return render(request, "signup.html")

def suppliers(request):
    category = request.GET.get('category', '')
    product_filter = request.GET.get('product', '')
    search_query = request.GET.get('search', '')

    suppliers = Supplier.objects.all()

    if category:
        suppliers = suppliers.filter(
            models.Q(category__icontains=category) |
            models.Q(sub_category1__icontains=category) |
            models.Q(sub_category2__icontains=category) |
            models.Q(sub_category3__icontains=category)
        )
    
    if product_filter:
        suppliers = suppliers.filter(
            models.Q(product1__icontains=product_filter) |
            models.Q(product2__icontains=product_filter) |
            models.Q(product3__icontains=product_filter) |
            models.Q(product4__icontains=product_filter) |
            models.Q(product5__icontains=product_filter) |
            models.Q(product6__icontains=product_filter) |
            models.Q(product7__icontains=product_filter) |
            models.Q(product8__icontains=product_filter) |
            models.Q(product9__icontains=product_filter) |
            models.Q(product10__icontains=product_filter)
        )

    if search_query:
        suppliers = suppliers.filter(
            models.Q(name__icontains=search_query) |
            models.Q(product1__icontains=search_query) |
            models.Q(product2__icontains=search_query) |
            models.Q(product3__icontains=search_query) |
            models.Q(product4__icontains=search_query) |
            models.Q(product5__icontains=search_query) |
            models.Q(product6__icontains=search_query) |
            models.Q(product7__icontains=search_query) |
            models.Q(product8__icontains=search_query) |
            models.Q(product9__icontains=search_query) |
            models.Q(product10__icontains=search_query) |
            models.Q(category__icontains=search_query) |
            models.Q(sub_category1__icontains=search_query) |
            models.Q(sub_category2__icontains=search_query) |
            models.Q(sub_category3__icontains=search_query)
        )

    count = suppliers.count()

    # Get all categories and subcategories for the filter dropdowns
    categories = Supplier.objects.values_list('category', flat=True).distinct()
    sub_categories = set()
    for i in range(1, 4):
        sub_categories.update(Supplier.objects.values_list(f'sub_category{i}', flat=True).distinct())
    sub_categories.discard(None)  # Remove None values

    products = list(set(
        list(Supplier.objects.values_list('product1', flat=True).distinct()) +
        list(Supplier.objects.values_list('product2', flat=True).distinct()) +
        list(Supplier.objects.values_list('product3', flat=True).distinct()) +
        list(Supplier.objects.values_list('product4', flat=True).distinct()) +
        list(Supplier.objects.values_list('product5', flat=True).distinct()) +
        list(Supplier.objects.values_list('product6', flat=True).distinct()) +
        list(Supplier.objects.values_list('product7', flat=True).distinct()) +
        list(Supplier.objects.values_list('product8', flat=True).distinct()) +
        list(Supplier.objects.values_list('product9', flat=True).distinct()) +
        list(Supplier.objects.values_list('product10', flat=True).distinct())
    ))
    products = [p for p in products if p]  # Remove empty strings

    return render(request, "suppliers.html", {
        "suppliers": suppliers,
        "categories": categories,
        "sub_categories": sub_categories,
        "products": products,
        "count": count,
    })

def create_supplier(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('suppliers')
    else:
        form = SupplierForm()
    return render(request, 'create_supplier.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('index')

def send_otp_email(user):
    otp = str(random.randint(100000, 999999))
    PasswordResetOTP.objects.create(user=user, otp=otp)
    send_mail(
        "Password Reset OTP",
        f"Your OTP for password reset is {otp}",
        "yourgmail@gmail.com",
        [user.email],
    )

def request_password_reset(request):
    if request.method == "POST":
        email = request.POST["email"]
        try:
            user = CustomUser.objects.get(email=email)
            send_otp_email(user)
            return render(request, "verify_otp.html", {"email": email})
        except CustomUser.DoesNotExist:
            return render(request, "request_reset.html", {"error": "Email not found"})
    return render(request, "request_reset.html")

def verify_otp(request):
    if request.method == "POST":
        email = request.POST["email"]
        otp = request.POST["otp"]
        user = CustomUser.objects.get(email=email)
        otp_obj = PasswordResetOTP.objects.filter(user=user, otp=otp).last()
        if otp_obj and otp_obj.is_valid():
            return render(request, "set_new_password.html", {"email": email})
        else:
            return render(request, "verify_otp.html", {"error": "Invalid or expired OTP", "email": email})

def set_new_password(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        
        if password != confirm_password:
            return render(request, "set_new_password.html", {"error": "Passwords don't match", "email": email})
        
        try:
            user = CustomUser.objects.get(email=email)
            user.set_password(password)
            user.save()
            return redirect('login')
        except CustomUser.DoesNotExist:
            return render(request, "set_new_password.html", {"error": "User not found", "email": email})
    
    return render(request, "set_new_password.html")

def google_login(request):
    # Redirect to Google OAuth2 login using allauth's built-in view
    from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
    from allauth.socialaccount.providers.oauth2.client import OAuth2Client
    from allauth.socialaccount.views import signup
    
    # This will redirect to the Google OAuth2 login page
    adapter = GoogleOAuth2Adapter(request)
    client = OAuth2Client(
        request,
        adapter.get_client_id(),
        adapter.get_client_secret(),
        adapter.get_access_token_method(),
        adapter.get_access_token_url(),
        adapter.get_callback_url(),
        adapter.get_scope()
    )
    
    # Get the authorization URL and redirect
    authorization_url = client.get_redirect_url(adapter.get_authorize_url())
    return redirect(authorization_url)

def resend_otp(request):
    if request.method == "POST":
        email = request.POST["email"]
        try:
            user = CustomUser.objects.get(email=email)
            send_otp_email(user)
            messages.success(request, "Verification code has been resent to your email.")
            return render(request, "verify_otp.html", {"email": email})
        except CustomUser.DoesNotExist:
            messages.error(request, "Email not found.")
            return render(request, "request_reset.html", {"error": "Email not found"})
    
    return redirect('request_reset')

def supplier_details(request, supplier_id):
    try:
        supplier = Supplier.objects.get(id=supplier_id)
        
        # Collect all non-empty subcategories
        sub_categories = []
        for i in range(1, 7):
            sub_category = getattr(supplier, f'sub_category{i}')
            if sub_category:
                sub_categories.append(sub_category)

        # Prepare product images URLs if they exist
        product_images = []
        for i in range(1, 11):
            image_url = getattr(supplier, f'product_image{i}_url')
            if image_url:
                product_images.append(image_url)
        
        # Prepare products list
        products = []
        for i in range(1, 11):
            product = getattr(supplier, f'product{i}')
            if product:
                products.append(product)

        # Handle logo URL
        logo_url = supplier.logo_url

        # Handle main image URL
        image_url = supplier.image_url

        # Handle person image URL
        person_image_url = supplier.person_image_url

        # Handle product image URLs
        product_images_with_urls = []
        for i in range(1, 11):
            image_url = getattr(supplier, f'product_image{i}_url')
            if image_url:
                product_images_with_urls.append(image_url)

        data = {
            "cia_id": supplier.cia_id,  # add cia_id
            "name": supplier.name,
            "founder_name": supplier.founder_name,
            "website_url": supplier.website_url,
            "logo": logo_url,
            "image": image_url,
            "category": supplier.category,
            "sub_categories": sub_categories,
            "email": supplier.email,
            "contact_person_name": supplier.contact_person_name,
            "person_image": person_image_url,
            "products": products,
            "product_images": product_images_with_urls,
            "door_number": supplier.door_number,
            "street": supplier.street,
            "area": supplier.area,
            "city": supplier.city,
            "state": supplier.state,
            "pin_code": supplier.pin_code,
            "business_description": supplier.business_description,
            "phone_number": supplier.phone_number,
            "gstno": supplier.gstno,
            "instagram": supplier.instagram,
            "facebook": supplier.facebook,
            "total_employees": supplier.total_employees,
        }
        return JsonResponse(data)
    except Supplier.DoesNotExist:
        return JsonResponse({"error": "Supplier not found"}, status=404)

@require_GET
def companies_by_category(request):
    category = request.GET.get('category', '')
    if not category:
        return JsonResponse({"error": "Category parameter is required"}, status=400)
    
    suppliers = Supplier.objects.filter(
        models.Q(category__iexact=category) |
        models.Q(sub_category1__iexact=category) |
        models.Q(sub_category2__iexact=category) |
        models.Q(sub_category3__iexact=category)
    )
    
    data = []
    for supplier in suppliers:
        data.append({
            "id": supplier.id,
            "name": supplier.name,
            "logo": supplier.logo_url,
            "category": supplier.category,
            "sub_categories": [getattr(supplier, f'sub_category{i}') for i in range(1,4) if getattr(supplier, f'sub_category{i}')],
            "email": supplier.email,
            "phone_number": supplier.phone_number,
        })
    return JsonResponse({"companies": data})

@require_GET
def search_suggestions(request):
    query = request.GET.get('q', '').strip().lower()
    
    if not query or len(query) < 2:
        return JsonResponse({"suggestions": []})
    
    # Search in suppliers
    supplier_results = Supplier.objects.filter(
        models.Q(name__icontains=query) |
        models.Q(category__icontains=query) |
        models.Q(sub_category1__icontains=query) |
        models.Q(sub_category2__icontains=query) |
        models.Q(sub_category3__icontains=query) |
        models.Q(product1__icontains=query) |
        models.Q(product2__icontains=query) |
        models.Q(product3__icontains=query) |
        models.Q(product4__icontains=query) |
        models.Q(product5__icontains=query) |
        models.Q(product6__icontains=query) |
        models.Q(product7__icontains=query) |
        models.Q(product8__icontains=query) |
        models.Q(product9__icontains=query) |
        models.Q(product10__icontains=query) |
        models.Q(business_description__icontains=query) |
        models.Q(gstno__icontains=query) |
        models.Q(instagram__icontains=query) |
        models.Q(facebook__icontains=query)
    )[:10]  # Limit to 10 results
    
    suggestions = []
    
    # Add supplier suggestions
    for supplier in supplier_results:
        suggestions.append({
            "type": "supplier",
            "name": supplier.name,
            "category": supplier.category,
            "url": f"/suppliers/?search={query}",
            "icon": "fas fa-building"
        })
    
    # Add category suggestions
    categories = Supplier.objects.filter(
        models.Q(category__icontains=query) |
        models.Q(sub_category1__icontains=query) |
        models.Q(sub_category2__icontains=query) |
        models.Q(sub_category3__icontains=query)
    ).values_list('category', flat=True).distinct()[:5]
    
    for category in categories:
        if category:
            suggestions.append({
                "type": "category",
                "name": category,
                "url": f"/suppliers/?category={category}",
                "icon": "fas fa-tag"
            })
    
    # Add product suggestions
    products = Supplier.objects.filter(
        models.Q(product1__icontains=query) |
        models.Q(product2__icontains=query) |
        models.Q(product3__icontains=query) |
        models.Q(product4__icontains=query) |
        models.Q(product5__icontains=query) |
        models.Q(product6__icontains=query) |
        models.Q(product7__icontains=query) |
        models.Q(product8__icontains=query) |
        models.Q(product9__icontains=query) |
        models.Q(product10__icontains=query)
    ).values_list('product1', 'product2', 'product3', 'product4', 'product5', 'product6', 'product7', 'product8', 'product9', 'product10').distinct()[:5]
    
    for product_tuple in products:
        for product in product_tuple:
            if product and query.lower() in product.lower():
                suggestions.append({
                    "type": "product",
                    "name": product,
                    "url": f"/suppliers/?product={product}",
                    "icon": "fas fa-box"
                })
    
    # Remove duplicates by name
    seen = set()
    unique_suggestions = []
    for suggestion in suggestions:
        if suggestion['name'] not in seen:
            seen.add(suggestion['name'])
            unique_suggestions.append(suggestion)
    
    return JsonResponse({"suggestions": unique_suggestions[:10]})

@require_GET
def search_api(request):
    """Search API endpoint that searches both database and HTML content"""
    query = request.GET.get('q', '').strip()

    if not query:
        return JsonResponse({"results": []})

    results = []

    # Search in database (suppliers and announcements)
    supplier_results = Supplier.objects.filter(
        models.Q(name__icontains=query) |
        models.Q(category__icontains=query) |
        models.Q(sub_category1__icontains=query) |
        models.Q(sub_category2__icontains=query) |
        models.Q(sub_category3__icontains=query) |
        models.Q(product1__icontains=query) |
        models.Q(product2__icontains=query) |
        models.Q(product3__icontains=query) |
        models.Q(product4__icontains=query) |
        models.Q(product5__icontains=query) |
        models.Q(product6__icontains=query) |
        models.Q(product7__icontains=query) |
        models.Q(product8__icontains=query) |
        models.Q(product9__icontains=query) |
        models.Q(product10__icontains=query) |
        models.Q(business_description__icontains=query) |
        models.Q(founder_name__icontains=query) |
        models.Q(contact_person_name__icontains=query) |
        models.Q(city__icontains=query) |
        models.Q(state__icontains=query) |
        models.Q(gstno__icontains=query) |
        models.Q(instagram__icontains=query) |
        models.Q(facebook__icontains=query)
    )[:20]
    
    for supplier in supplier_results:
        results.append({
            "type": "supplier",
            "title": supplier.name,
            "description": supplier.business_description or f"{supplier.category} supplier",
            "url": f"/suppliers/?search={query}",
            "category": supplier.category,
            "score": 1.0
        })
    
    # Search in announcements
    announcement_results = Announcement.objects.filter(
        models.Q(title__icontains=query) |
        models.Q(content__icontains=query)
    )[:10]
    
    for announcement in announcement_results:
        results.append({
            "type": "announcement",
            "title": announcement.title,
            "description": announcement.content[:200] + "..." if len(announcement.content) > 200 else announcement.content,
            "url": f"/announcement/{announcement.id}/",
            "category": "Announcement",
            "score": 0.8
        })
    
    # Search in HTML content (headings and paragraphs)
    # This is a simplified approach - in production, you might want to use a proper search engine
    # or pre-index the content
    html_results = search_html_content(query)
    results.extend(html_results)
    
    # Sort by relevance score (highest first)
    results.sort(key=lambda x: x['score'], reverse=True)
    
    return JsonResponse({"results": results[:20]})

def search_html_content(query):
    """Search for query in HTML content (headings and paragraphs)"""
    import os
    from django.conf import settings
    import re
    
    results = []
    query_lower = query.lower()
    
    # List of HTML templates to search
    templates_to_search = [
        'index.html',
        'about.html',
        'category.html',
        'announcement.html',
        'announcement_detail.html',
        'suppliers.html',
        'login.html',
        'signup.html'
    ]
    
    for template_name in templates_to_search:
        template_path = os.path.join(settings.BASE_DIR, 'app', 'templates', template_name)
        
        try:
            with open(template_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
                # Remove Django template tags for cleaner search
                content_clean = re.sub(r'{%[^%]*%}|{{[^}]*}}', '', content)
                
                # Search for headings (h1-h6)
                heading_matches = re.findall(r'<h[1-6][^>]*>(.*?)</h[1-6]>', content_clean, re.IGNORECASE | re.DOTALL)
                for heading in heading_matches:
                    # Clean HTML tags from heading
                    heading_clean = re.sub(r'<[^>]*>', '', heading).strip()
                    if heading_clean and query_lower in heading_clean.lower():
                        results.append({
                            "type": "page_content",
                            "title": f"Page: {template_name.replace('.html', '')} - Heading",
                            "description": heading_clean,
                            "url": get_url_from_template(template_name),
                            "category": "Content",
                            "score": 0.6
                        })
                
                # Search for paragraphs
                paragraph_matches = re.findall(r'<p[^>]*>(.*?)</p>', content_clean, re.IGNORECASE | re.DOTALL)
                for paragraph in paragraph_matches:
                    # Clean HTML tags from paragraph
                    paragraph_clean = re.sub(r'<[^>]*>', '', paragraph).strip()
                    if paragraph_clean and query_lower in paragraph_clean.lower():
                        results.append({
                            "type": "page_content",
                            "title": f"Page: {template_name.replace('.html', '')} - Content",
                            "description": paragraph_clean[:150] + "..." if len(paragraph_clean) > 150 else paragraph_clean,
                            "url": get_url_from_template(template_name),
                            "category": "Content",
                            "score": 0.5
                        })
                        
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"Error searching {template_name}: {e}")
            continue
    
    return results

def get_url_from_template(template_name):
    """Get URL from template name"""
    url_map = {
        'index.html': '/',
        'about.html': '/about/',
        'category.html': '/category/',
        'announcement.html': '/announcement/',
        'announcement_detail.html': '/announcement/',  # Generic announcement page
        'suppliers.html': '/suppliers/',
        'login.html': '/login/',
        'signup.html': '/signup/'
    }
    return url_map.get(template_name, '/')

def search_results(request):
    """Search results page view"""
    query = request.GET.get('q', '').strip()

    if not query:
        return redirect('index')

    # Use the same search logic as the API but return the results directly
    results = []

    # Search in database (suppliers and announcements)
    supplier_results = Supplier.objects.filter(
        models.Q(name__icontains=query) |
        models.Q(category__icontains=query) |
        models.Q(sub_category1__icontains=query) |
        models.Q(sub_category2__icontains=query) |
        models.Q(sub_category3__icontains=query) |
        models.Q(product1__icontains=query) |
        models.Q(product2__icontains=query) |
        models.Q(product3__icontains=query) |
        models.Q(product4__icontains=query) |
        models.Q(product5__icontains=query) |
        models.Q(product6__icontains=query) |
        models.Q(product7__icontains=query) |
        models.Q(product8__icontains=query) |
        models.Q(product9__icontains=query) |
        models.Q(product10__icontains=query) |
        models.Q(business_description__icontains=query) |
        models.Q(founder_name__icontains=query) |
        models.Q(contact_person_name__icontains=query) |
        models.Q(city__icontains=query) |
        models.Q(state__icontains=query) |
        models.Q(gstno__icontains=query) |
        models.Q(instagram__icontains=query) |
        models.Q(facebook__icontains=query)
    )[:20]
    
    for supplier in supplier_results:
        results.append({
            "type": "supplier",
            "title": supplier.name,
            "description": supplier.business_description or f"{supplier.category} supplier",
            "url": f"/suppliers/?search={query}",
            "phone_number": supplier.phone_number,
            "category": supplier.category,
            "score": 1.0
        })
    
    # Search in announcements
    announcement_results = Announcement.objects.filter(
        models.Q(title__icontains=query) |
        models.Q(content__icontains=query)
    )[:10]
    
    for announcement in announcement_results:
        results.append({
            "type": "announcement",
            "title": announcement.title,
            "description": announcement.content[:200] + "..." if len(announcement.content) > 200 else announcement.content,
            "url": f"/announcement/{announcement.id}/",
            "category": "Announcement",
            "score": 0.8
        })
    
    # Search in HTML content (headings and paragraphs)
    html_results = search_html_content(query)
    results.extend(html_results)
    
    # Sort by relevance score (highest first)
    results.sort(key=lambda x: x['score'], reverse=True)
    
    context = {
        'query': query,
        'results': results,
        'total_results': len(results),
    }
    
    return render(request, "search_results.html", context)

def photo_gallery(request):
    # Fetch all images from PhotoGallery
    all_photos = PhotoGallery.objects.all()

    context = {
        'all_photos': all_photos,
        'total_photos': all_photos.count()
    }
    return render(request, "photo_gallery.html", context)

def news_gallery(request):
    # Fetch all newspaper cuttings from NewspaperGallery in descending order
    all_newspapers = NewspaperGallery.objects.all().order_by('-uploaded_at')

    context = {
        'all_newspapers': all_newspapers,
        'total_newspapers': all_newspapers.count()
    }
    return render(request, "news_gallery.html", context)

@require_GET
def get_supplier_categories(request):
    """
    AJAX endpoint to get all supplier categories for dynamic dropdown updates
    """
    try:
        # Get all unique categories from Supplier model
        categories = Supplier.objects.values_list('category', flat=True).distinct()
        categories = [cat for cat in categories if cat]  # Remove None/empty values
        categories = sorted(categories)  # Sort alphabetically

        return JsonResponse({
            'success': True,
            'categories': categories
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# User Creation and Profile Management Views

def create_user_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        # ensure widgets have classes even if form is re-rendered with errors
        apply_form_css(form)
        if form.is_valid():
            # Store form data in session for OTP verification
            request.session['user_data'] = {
                'email': form.cleaned_data['email'],
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'password': form.cleaned_data['password'],
                'membership_type': form.cleaned_data['membership_type'],
                'business_type': form.cleaned_data['business_type'],
            }
            # Send OTP to email
            send_user_otp(request, form.cleaned_data['email'])
            return redirect('verify_user_otp')
        else:
            # Form is invalid, render with errors
            return render(request, 'create_user.html', {'form': form})
    else:
        form = UserCreationForm()
        apply_form_css(form)
    return render(request, 'create_user.html', {'form': form})

def apply_form_css(form, css_class='form-input w-full'):
    """
    Ensure every field widget has the provided CSS class.
    Call this after instantiating a form to avoid needing the add_class filter in templates.
    """
    try:
        for fld in form.fields.values():
            # preserve existing classes
            existing = fld.widget.attrs.get('class', '')
            if existing:
                # append if different
                if css_class not in existing:
                    fld.widget.attrs['class'] = f"{existing} {css_class}"
            else:
                fld.widget.attrs['class'] = css_class
    except Exception:
        pass

def send_user_otp(request, email):
    otp = str(random.randint(100000, 999999))
    PasswordResetOTP.objects.create(user=None, otp=otp)  # We'll update user after creation
    request.session['user_otp'] = otp
    request.session['user_email'] = email
    try:
        send_mail(
            "Email Verification OTP",
            f"Your OTP for email verification is {otp}",
            "yourgmail@gmail.com",
            [email],
        )
        messages.success(request, "OTP sent to your email. Please check your inbox.")
    except Exception as e:
        messages.error(request, "Failed to send verification code. Please check your email address and try again.")

def verify_user_otp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        stored_otp = request.session.get('user_otp')
        if otp == stored_otp:
            # Create user
            user_data = request.session.get('user_data')
            if user_data:
                try:
                    user = CustomUser.objects.create_user(
                        email=user_data['email'],
                        password=user_data['password'],
                        first_name=user_data['first_name'],
                        last_name=user_data['last_name']
                    )
                    # Update OTP with user
                    otp_obj = PasswordResetOTP.objects.filter(otp=otp).last()
                    if otp_obj:
                        otp_obj.user = user
                        otp_obj.save()
                    # Clear session
                    del request.session['user_data']
                    del request.session['user_otp']
                    del request.session['user_email']
                    messages.success(request, "Account created successfully! Please login.")
                    return redirect('login')
                except Exception as e:
                    error_message = str(e)
                    if "duplicate key value violates unique constraint" in error_message and "email" in error_message:
                        messages.error(request, "An account with this email already exists. Please use a different email or try logging in.")
                    else:
                        messages.error(request, "An error occurred while creating your account. Please try again.")
                    return redirect('create_user')
        messages.error(request, "Invalid OTP")
    return render(request, 'verify_user_otp.html')

@login_required
def profile_view(request):
    # Check if user has a supplier profile
    try:
        supplier = Supplier.objects.get(email=request.user.email)
        has_supplier_profile = True
    except Supplier.DoesNotExist:
        supplier = None
        has_supplier_profile = False

    context = {
        'user': request.user,
        'supplier': supplier,
        'has_supplier_profile': has_supplier_profile,
    }
    return render(request, 'profile.html', context)

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            # Send OTP for verification before saving
            request.session['edit_data'] = {
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
            }
            send_edit_otp(request, request.user.email)
            return redirect('verify_edit_otp')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'edit_profile.html', {'form': form})

def send_edit_otp(request, email):
    otp = str(random.randint(100000, 999999))
    PasswordResetOTP.objects.create(user=request.user, otp=otp)
    request.session['edit_otp'] = otp
    send_mail(
        "Profile Edit Verification OTP",
        f"Your OTP for profile edit verification is {otp}",
        "yourgmail@gmail.com",
        [email],
    )

@login_required
def verify_edit_otp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        stored_otp = request.session.get('edit_otp')
        if otp == stored_otp:
            # Update user profile
            edit_data = request.session.get('edit_data')
            if edit_data:
                request.user.first_name = edit_data['first_name']
                request.user.last_name = edit_data['last_name']
                request.user.save()
                # Clear session
                del request.session['edit_data']
                del request.session['edit_otp']
                messages.success(request, "Profile updated successfully!")
                return redirect('profile')
        messages.error(request, "Invalid OTP")
    return render(request, 'verify_edit_otp.html')

@login_required
def edit_supplier_profile_view(request):
    try:
        supplier = Supplier.objects.get(email=request.user.email)
    except Supplier.DoesNotExist:
        messages.error(request, "No business profile found for your account.")
        return redirect('profile')

    if request.method == 'POST':
        form = SupplierEditForm(request.POST)
        if form.is_valid():
            # Create an edit request with message and contact phone
            SupplierEditRequest.objects.create(
                supplier=supplier,
                user=request.user,
                message=form.cleaned_data['message'],
                contact_phone=form.cleaned_data.get('contact_phone')
            )
            # Send notification email to admin
            send_admin_notification_email(request.user, supplier, form.cleaned_data['message'], form.cleaned_data.get('contact_phone'))
            messages.success(request, "Your edit request has been submitted for admin approval. You will receive an email notification once it's reviewed.")
            return redirect('profile')
    else:
        form = SupplierEditForm()
    return render(request, 'edit_supplier_profile.html', {'form': form, 'supplier': supplier})

@login_required
def request_supplier_listing_view(request):
    if request.method == 'POST':
        form = SupplierListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing_request = form.save(commit=False)
            listing_request.user = request.user
            listing_request.save()
            # Send notification email to admin
            send_admin_listing_notification_email(request.user, listing_request)
            # Send confirmation email to user
            send_user_listing_confirmation_email(request.user, listing_request)
            messages.success(request, "Your supplier listing request has been submitted for admin approval. You will receive an email notification once it's reviewed.")
            return redirect('profile')
    else:
        form = SupplierListingForm()
    return render(request, 'request_supplier_listing.html', {'form': form})

def send_admin_listing_notification_email(user, listing_request):
    """Send notification email to admin about supplier listing request"""
    try:
        # Prefer project ADMINS setting if present
        admin_emails = [email for _, email in getattr(settings, 'ADMINS', [])]
        if not admin_emails:
            admin_emails = ['admin@cia.com']  # fallback

        subject = f"New Supplier Listing Request: {listing_request.company_name}"
        # Build readable message
        lines = [
            "A new supplier listing request has been submitted:",
            f"User: {user.email}",
            f"Company: {listing_request.company_name}",
            f"Founder: {listing_request.founder_name or 'Not provided'}",
            f"Email: {listing_request.email}",
            f"Phone: {listing_request.phone_number or 'Not provided'}",
            f"Category: {listing_request.category or 'Not provided'}",
            f"Products: {', '.join([getattr(listing_request, f'product{i}') for i in range(1, 11) if getattr(listing_request, f'product{i}')]) or 'Not provided'}",
            f"Business Description: {listing_request.business_description or 'Not provided'}",
            f"Address: {', '.join([getattr(listing_request, attr) for attr in ['door_number', 'street', 'area', 'city', 'state', 'pin_code'] if getattr(listing_request, attr)]) or 'Not provided'}"
        ]

        message_body = "\n".join(lines)
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'webmaster@localhost')

        # Make sure failure is logged (fail_silently False)
        send_mail(subject, message_body, from_email, admin_emails, fail_silently=False)
    except Exception as e:
        logger.exception("Failed to send admin listing notification email: %s", e)

def send_admin_notification_email(user, supplier, message, contact_phone):
    """Send notification email to admin about supplier edit request"""
    try:
        # Prefer project ADMINS setting if present
        admin_emails = [email for _, email in getattr(settings, 'ADMINS', [])]
        if not admin_emails:
            admin_emails = ['admin@cia.com']  # fallback

        subject = f"Supplier Edit Request: {getattr(supplier, 'name', supplier)}"
        # Build readable message
        lines = [
            "A supplier edit request has been submitted:",
            f"User: {getattr(user, 'email', 'unknown')}",
            f"Supplier: {getattr(supplier, 'name', supplier)}",
            f"Message: {message}",
            f"Contact Phone: {contact_phone or 'Not provided'}"
        ]

        message_body = "\n".join(lines)
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'webmaster@localhost')

        # Make sure failure is logged (fail_silently False)
        send_mail(subject, message_body, from_email, admin_emails, fail_silently=False)
    except Exception as e:
        logger.exception("Failed to send admin notification email: %s", e)

def send_user_listing_confirmation_email(user, listing_request):
    """Send confirmation email to user about their supplier listing request"""
    try:
        subject = f"Supplier Listing Request Submitted: {listing_request.company_name}"
        # Build readable message
        lines = [
            f"Dear {user.first_name or 'User'},",
            "",
            "Thank you for submitting your supplier listing request!",
            "",
            "Your request details:",
            f"Company: {listing_request.company_name}",
            f"Category: {listing_request.category or 'Not specified'}",
            f"Email: {listing_request.email}",
            f"Phone: {listing_request.phone_number or 'Not provided'}",
            "",
            "Your request has been submitted for admin review. You will receive an email notification once your listing is approved and published.",
            "",
            "If you have any questions, please contact us.",
            "",
            "Best regards,",
            "CIA Team"
        ]

        message_body = "\n".join(lines)
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'webmaster@localhost')

        # Make sure failure is logged (fail_silently False)
        send_mail(subject, message_body, from_email, [user.email], fail_silently=False)
    except Exception as e:
        logger.exception("Failed to send user listing confirmation email: %s", e)

def contact(request):
    # Fetch contact information from database
    contact_info = ContactInformation.objects.first()  # Get the first (and likely only) contact info record

    context = {
        'contact_info': contact_info,
    }
    return render(request, "contact.html", context)

def book_showcase(request):
    # Fetch all book showcase images
    book_photos = BookShowcase.objects.all()

    context = {
        'book_photos': book_photos,
        'total_photos': book_photos.count()
    }
    return render(request, "book_showcase.html", context)
