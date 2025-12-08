"""
Management command to sync Supplier records with User accounts by email.
This is a one-time data migration command that matches existing suppliers to users.

Usage:
    python manage.py sync_supplier_users [--dry-run]
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app.models import Supplier
import logging

logger = logging.getLogger('cai_security')
User = get_user_model()


class Command(BaseCommand):
    help = 'Sync Supplier records with User accounts by matching email addresses'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually making changes',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Find all suppliers without a user
        suppliers_without_user = Supplier.objects.filter(user__isnull=True)
        total_to_process = suppliers_without_user.count()
        
        self.stdout.write(f'\nFound {total_to_process} suppliers without user assignment.')
        
        if total_to_process == 0:
            self.stdout.write(self.style.SUCCESS('All suppliers are already linked to users!'))
            return
        
        matched = 0
        not_matched = 0
        
        for supplier in suppliers_without_user:
            if not supplier.email:
                self.stdout.write(f'⊘ Supplier "{supplier.name}" has no email - skipping')
                not_matched += 1
                continue
            
            try:
                # Try to find user by email (case-insensitive)
                user = User.objects.get(email__iexact=supplier.email)
                
                if not dry_run:
                    supplier.user = user
                    supplier.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Assigned supplier "{supplier.name}" ({supplier.email}) -> user {user.email}'
                    )
                )
                logger.info(f"Supplier {supplier.id} linked to user {user.id} by email match")
                matched += 1
                
            except User.DoesNotExist:
                self.stdout.write(
                    f'✗ No matching user for supplier "{supplier.name}" (email: {supplier.email})'
                )
                logger.warning(f"No matching user found for supplier {supplier.id} with email {supplier.email}")
                not_matched += 1
            
            except User.MultipleObjectsReturned:
                self.stdout.write(
                    self.style.ERROR(
                        f'⚠ Multiple users found with email {supplier.email} - manual intervention needed'
                    )
                )
                logger.error(f"Multiple users found for email {supplier.email}")
                not_matched += 1
        
        # Summary
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(f'Summary:')
        self.stdout.write(f'  Matched:     {matched}')
        self.stdout.write(f'  Not matched: {not_matched}')
        self.stdout.write(f'  Total:       {total_to_process}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN - no changes were made. Remove --dry-run to apply.'))
        else:
            self.stdout.write(self.style.SUCCESS('\n✓ Data sync complete!'))
        
        self.stdout.write('=' * 60 + '\n')
