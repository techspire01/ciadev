from django.core.management.base import BaseCommand
from django.utils import timezone
from app.models import SupplierEditRequest
import json
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Process pending supplier edit requests'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            type=str,
            choices=['approve', 'deny'],
            required=True,
            help='Action to perform on requests'
        )
        parser.add_argument(
            '--ids',
            type=str,
            help='Comma-separated list of request IDs to process'
        )

    def handle(self, *args, **options):
        action = options['action']
        ids = options.get('ids')

        if ids:
            id_list = [int(id.strip()) for id in ids.split(',')]
            queryset = SupplierEditRequest.objects.filter(id__in=id_list, status='pending')
        else:
            queryset = SupplierEditRequest.objects.filter(status='pending')

        if not queryset.exists():
            self.stdout.write(self.style.WARNING('No pending requests found.'))
            return

        self.stdout.write(f'Found {queryset.count()} pending requests.')

        for request in queryset:
            if action == 'approve':
                self.approve_request(request)
            elif action == 'deny':
                self.deny_request(request)

    def approve_request(self, request):
        """Approve a supplier edit request"""
        supplier = request.supplier
        data = request.requested_data

        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                self.stdout.write(self.style.ERROR(f'Invalid JSON data for request {request.id}'))
                return

        changes_applied = []
        for key, value in data.items():
            if hasattr(supplier, key):
                old_value = getattr(supplier, key)
                setattr(supplier, key, value)
                changes_applied.append(f"{key}: '{old_value}' -> '{value}'")
            else:
                self.stdout.write(self.style.WARNING(f"Supplier {supplier} does not have attribute {key}"))

        try:
            supplier.save()
            request.status = 'approved'
            request.reviewed_at = timezone.now()
            request.save()
            self.stdout.write(self.style.SUCCESS(f'Approved request {request.id}: {", ".join(changes_applied)}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to save changes for request {request.id}: {e}'))

    def deny_request(self, request):
        """Deny a supplier edit request"""
        request.status = 'rejected'
        request.reviewed_at = timezone.now()
        request.save()
        self.stdout.write(self.style.SUCCESS(f'Denied request {request.id}'))
