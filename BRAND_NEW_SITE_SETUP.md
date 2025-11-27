# Brand New Site Integration - Portal App

## ✅ Setup Complete

All files have been successfully added to the `portal` app with Django `{% load static %}` template support.

---

## 📁 File Structure

### Templates (`portal/templates/brand_new_site/`)
- **`dashboard.html`** - Main career opportunities portal (renamed from `index.html`)
- **`job_portal_admin.html`** - Admin dashboard for managing internships and jobs
- **`job_admin.html`** - Admin UI model/wireframe page

### Static Files (`portal/static/brand_new_site/`)
- **`dashboard.json`** - Career data (internships & job opportunities)
- **`server.js`** - Node.js static server (for reference)
- **`pacakge.json`** - Package configuration

---

## 🔗 URL Routes

Access the new pages via these Django URLs:

| Route | View | Template |
|-------|------|----------|
| `/portal/brand-new-site/` | `brand_new_site_dashboard` | `dashboard.html` |
| `/portal/admin/portal/` | `job_portal_admin` | `job_portal_admin.html` |
| `/portal/admin/ui-model/` | `job_admin` | `job_admin.html` |

---

## 📝 Template Features

### Dashboard (`dashboard.html`)
- Career opportunities portal with job & internship listings
- Responsive grid layout
- Filter by category (All, Internships, Jobs)
- Search functionality
- Detail modal for viewing full opportunity details
- Uses `{% load static %}` for asset references
- Fetches data from `{% static 'brand_new_site/dashboard.json' %}`

### Job Portal Admin (`job_portal_admin.html`)
- Admin dashboard with sidebar navigation
- Tabs for: Add Internships, View Internships, Add Jobs, View Jobs, Applications
- Form-based management interface
- Modals for editing entries
- LocalStorage integration for data persistence

### Job Admin (`job_admin.html`)
- UI model/wireframe documentation
- Shows complete dashboard layout
- Design system & color palette
- Component showcase
- User flow diagrams

---

## 🎨 Django Static Usage

All templates use Django's `{% load static %}` and `{% static %}` tags:

```html
{% load static %}

<!-- External CSS -->
<link rel="stylesheet" href="{% static 'brand_new_site/css/admin.css' %}">

<!-- External JS -->
<script src="{% static 'brand_new_site/js/admin.js' %}"></script>

<!-- JSON Data -->
const dataUrl = "{% static 'brand_new_site/dashboard.json' %}";
```

---

## 📦 Required Files (To Add)

If you want full functionality, create these CSS/JS files in the static directory:

```
portal/static/brand_new_site/
├── css/
│   ├── admin.css
│   ├── admin-styles.css
│   └── job-admin-styles.css
├── js/
│   ├── admin.js
│   └── job-admin.js
├── videos/
│   └── background.mp4 (optional)
└── images/
    └── (company logos, etc.)
```

---

## 🚀 Running the Server

```bash
# From the project root
python manage.py runserver

# Then visit:
# http://localhost:8000/portal/brand-new-site/
# http://localhost:8000/portal/admin/portal/
# http://localhost:8000/portal/admin/ui-model/
```

---

## ✨ Next Steps

1. **Add CSS Files**: Create `admin.css`, `admin-styles.css`, and `job-admin-styles.css` for styling
2. **Add JS Files**: Create `admin.js` and `job-admin.js` for functionality
3. **Add Media Files**: Optionally add videos and images to the static directory
4. **Test Templates**: Open each URL in the browser to verify they load correctly
5. **Customize**: Modify templates as needed to match your exact requirements

---

## 📖 Views Added

In `portal/views.py`:
- `brand_new_site_dashboard()` - Serves dashboard.html
- `job_portal_admin()` - Serves job_portal_admin.html
- `job_admin()` - Serves job_admin.html

In `portal/urls.py`:
- Added 3 new URL patterns for the above views
