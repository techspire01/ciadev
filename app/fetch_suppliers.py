
import os
import sys
import django

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Point to your project settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')

# Setup Django
django.setup()

from app.models import Supplier

def fetch_suppliers():
    suppliers = Supplier.objects.all()
    for supplier in suppliers:
        print(f"ID: {supplier.id}, Name: {supplier.name}")

if __name__ == "__main__":
    fetch_suppliers()
