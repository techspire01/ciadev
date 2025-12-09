from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.contrib import messages
from django.db import models
import random
from .models import Supplier, CustomUser, PasswordResetOTP, Announcement, PhotoGallery, Leadership, NewspaperGallery, BookShowcase, SupplierEditRequest, ContactInformation, About, Complaint
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

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

def coders_club(request):
    return render(request, "coders_club.html")

def coders_contact(request):
    return render(request, "coders_contact.html")

def complaint_page(request):
    return render(request, "complain.html")

@csrf_exempt
@require_http_methods(["POST"])
def submit_complaint(request):
    complaint_text = request.POST.get('complaint') or request.POST.get('complaint_text')
    contact_number = request.POST.get('contact_number')

    if not complaint_text:
        return JsonResponse({'error': 'Complaint text is required.'}, status=400)

    try:
        user = request.user if request.user.is_authenticated else None
        complaint = Complaint.objects.create(
            user=user,
            complaint_text=complaint_text,
            contact_number=contact_number
        )


        # Prepare email
        subject = f"New Complaint Submitted - #{complaint.id}"
        message = (
            f"A new complaint has been submitted:\n\n"
            f"Complaint ID: {complaint.id}\n"
            f"User: {getattr(user, 'email', 'Anonymous')}\n"
            f"Contact Number: {contact_number or 'N/A'}\n\n"
            f"Complaint:\n{complaint_text}\n"
        )

        # Use dynamic email settings (from EmailConfiguration or fallback)
        from .utils import get_email_settings
        email_settings = get_email_settings()
        config_email = email_settings.get('host_user') or email_settings.get('default_from_email')

        # Recipients: admin(s) and config email
        recipients = set()
        if config_email:
            recipients.add(config_email)
        admins = getattr(settings, 'ADMINS', None)
        if admins:
            for a in admins:
                try:
                    recipients.add(a[1])
                except Exception:
                    continue

        # Also add any previous admin_email logic for backward compatibility
        admin_email = getattr(settings, 'EMAIL_HOST_USER', None)
        if admin_email:
            recipients.add(admin_email)

        if recipients:
            try:
                send_mail(subject, message, config_email or admin_email or list(recipients)[0], list(recipients), fail_silently=False)
            except Exception as e:
                logger.exception("Failed sending complaint email: %s", e)

        return JsonResponse({'message': 'Complaint submitted successfully.'}, status=201)
    except Exception as e:
        logger.exception("Failed to submit complaint: %s", e)
        return JsonResponse({'error': 'Failed to submit complaint.'}, status=500)

def index(request):
    # Check if user just logged in and show welcome message only once
    if request.session.pop('show_welcome_message', False):
        if request.user.is_authenticated:
            messages.success(request, f"Welcome back, {request.user.email}!")
    
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

    # Fetch latest active announcement
    from announcements.models import Announcement
    announcement = Announcement.objects.filter(is_active=True).first()
    
    # Pre-generate announcement image URL (with error handling)
    announcement_image_url = None
    if announcement and announcement.image:
        try:
            announcement_image_url = announcement.image.url
        except Exception as e:
            logger.warning(f"Could not generate announcement image URL: {str(e)}")
            announcement_image_url = None

    context = {
        'user': request.user,
        'featured_suppliers': random_suppliers,
        'categories': categories,
        'category_counts': category_counts,
        'category_subcategories': category_subcategories,
        'book_showcase_images': book_showcase_images,
        'announcement': announcement,
        'announcement_image_url': announcement_image_url,
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
    leadership_members = Leadership.objects.all().order_by('dis_pos', '-created_at')

    # Fetch about information
    about_info = About.objects.first()

    context = {
        'latest_photos': latest_photos,
        'total_photos': total_photos,
        'show_view_more': total_photos > 6,
        'latest_newspapers': latest_newspapers,
        'total_newspapers': total_newspapers,
        'show_newspaper_view_more': total_newspapers > 6,
        'leadership_members': leadership_members,
        'about_info': about_info
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
    
    # Get flash announcements from announcements app
    from announcements.models import Announcement as FlashAnnouncement
    flash_announcements = FlashAnnouncement.objects.filter(is_active=True).order_by('-created_at')

    context = {
        'announcements': announcements,
        'critical_announcement': critical_announcement,
        'latest_announcements': latest_announcements,
        'flash_announcements': flash_announcements,
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
                # Set a session flag for the welcome message to show only on index page
                request.session['show_welcome_message'] = True
                return redirect('index')
            else:
                messages.error(request, "Invalid email or password.")
        except Exception as e:
            messages.error(request, "An error occurred. Please try again.")
            
    return render(request, "login.html")

def signup_view(request):
    return render(request, "signup.html")

def cia_networks(request):
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

    return render(request, "cia_networks.html", {
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
            return redirect('cia_networks')
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
        email = request.POST.get("email", "")
        otp = request.POST.get("otp", "").strip()
        
        try:
            user = CustomUser.objects.get(email=email)
            # Get the most recent OTP for this user
            otp_obj = PasswordResetOTP.objects.filter(user=user).order_by('-created_at').first()
            
            if not otp_obj:
                return render(request, "verify_otp.html", {
                    "error": "No OTP found. Please request a new one.",
                    "email": email
                })
            
            # Check if OTP is valid (not expired) AND matches entered OTP
            if otp_obj.is_valid() and otp_obj.otp == otp:
                # OTP is correct, proceed to password reset
                otp_obj.delete()  # Delete OTP after successful verification
                return render(request, "set_new_password.html", {"email": email})
            elif not otp_obj.is_valid():
                return render(request, "verify_otp.html", {
                    "error": "OTP has expired. Please request a new one.",
                    "email": email
                })
            else:
                return render(request, "verify_otp.html", {
                    "error": "Invalid OTP. Please check and try again.",
                    "email": email
                })
        except CustomUser.DoesNotExist:
            return render(request, "verify_otp.html", {
                "error": "User not found.",
                "email": email
            })
    
    # GET request
    email = request.GET.get('email', request.session.get('reset_email', ''))
    return render(request, "verify_otp.html", {"email": email})

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

def supplier_detail_page(request, supplier_name):
    """Display full supplier detail page with unique URL based on company name"""
    try:
        from urllib.parse import unquote
        import re

        # Try a few strategies to resolve the supplier name from the slug
        normalized_name = unquote(supplier_name).replace('-', ' ').strip()

        # 1) Direct case-insensitive exact match
        try:
            supplier = Supplier.objects.get(name__iexact=normalized_name)
        except Supplier.DoesNotExist:
            supplier = None

        # 2) If not found, try a normalized token-score matching across all suppliers
        if not supplier:
            def normalize(s):
                return re.sub(r'[^a-z0-9 ]', ' ', (s or '').lower()).strip()

            target = normalize(normalized_name)
            if target:
                target_tokens = set(t for t in target.split() if t)
                best = None
                best_score = 0
                # iterate suppliers and compute token intersection score
                for cand in Supplier.objects.all():
                    cand_norm = normalize(cand.name)
                    cand_tokens = set(t for t in cand_norm.split() if t)
                    if not cand_tokens:
                        continue
                    score = len(target_tokens & cand_tokens)
                    # boost exact substring matches
                    if target in cand_norm or cand_norm in target:
                        score += 1
                    if score > best_score:
                        best_score = score
                        best = cand
                if best and best_score > 0:
                    supplier = best

        # If still not found, return 404 now (avoid later NoneType errors)
        if not supplier:
            from django.http import HttpResponseNotFound
            return HttpResponseNotFound('<h1>Supplier Not Found</h1><p>The supplier you are looking for does not exist.</p>')
        
        # Collect all non-empty subcategories
        sub_categories = []
        for i in range(1, 7):
            sub_category = getattr(supplier, f'sub_category{i}', None)
            if sub_category:
                sub_categories.append(sub_category)

        # Prepare product images URLs
        product_images = []
        for i in range(1, 11):
            image_url = getattr(supplier, f'product_image{i}_url', None)
            if image_url:
                product_images.append(image_url)
        
        # Prepare products list
        products = []
        for i in range(1, 11):
            product = getattr(supplier, f'product{i}', None)
            if product:
                products.append(product)

        context = {
            'supplier': supplier,
            'sub_categories': sub_categories,
            'product_images': product_images,
            'products': products,
        }
        return render(request, 'supplier_detail.html', context)
    except Supplier.DoesNotExist:
        # Return a 404 response with a custom error message
        from django.http import HttpResponseNotFound
        return HttpResponseNotFound('<h1>Supplier Not Found</h1><p>The supplier you are looking for does not exist.</p>')

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
            "url": f"/cia_networks/?search={query}",
            "url": f"/cia_networks/{supplier.name.replace(' ', '-').lower()}/",
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
                "url": f"/cia_networks/?category={category}",
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
                    "url": f"/cia_networks/?product={product}",
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
            "url": f"/cia_networks/?search={query}",
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

    # Search in portal jobs and internships
    try:
        from portal.models import PortalJob, PortalInternship

        job_results = PortalJob.objects.filter(
            models.Q(title__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(company_name__icontains=query) |
            models.Q(location__icontains=query) |
            models.Q(requirements__icontains=query) |
            models.Q(responsibilities__icontains=query)
        )[:10]

        for job in job_results:
            results.append({
                "type": "job",
                "id": job.id,
                "title": job.title,
                "company": job.company_name,
                "location": job.location,
                "description": (job.description[:200] + "...") if len(job.description) > 200 else job.description,
                "url": f"/job/{job.id}/apply/",
                "category": "Job",
                "score": 0.9
            })

        internship_results = PortalInternship.objects.filter(
            models.Q(title__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(company_name__icontains=query) |
            models.Q(location__icontains=query) |
            models.Q(requirements__icontains=query) |
            models.Q(responsibilities__icontains=query)
        )[:10]

        for intern in internship_results:
            results.append({
                "type": "internship",
                "id": intern.id,
                "title": intern.title,
                "company": intern.company_name,
                "location": intern.location,
                "description": (intern.description[:200] + "...") if len(intern.description) > 200 else intern.description,
                "url": f"/internship/{intern.id}/apply/",
                "category": "Internship",
                "score": 0.85
            })
    except Exception:
        # Avoid breaking search if portal app or models aren't available
        logger.exception("Failed to include portal job/internship in search")
    
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
        'cia_networks.html',
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
        'cia_networks.html': '/cia_networks/',
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
            "url": f"/cia_networks/{supplier.name.replace(' ', '-').lower()}/",
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
