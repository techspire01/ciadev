from django.core.management.base import BaseCommand
from django.conf import settings
from supabase import create_client


class Command(BaseCommand):
    help = 'Setup and verify Supabase bucket'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔧 Setting up Supabase bucket...\n'))

        # Check settings
        supabase_url = getattr(settings, 'SUPABASE_URL', None)
        service_key = getattr(settings, 'SUPABASE_SERVICE_ROLE_KEY', None)
        bucket_name = getattr(settings, 'SUPABASE_BUCKET', None)

        if not supabase_url:
            self.stdout.write(self.style.ERROR('❌ SUPABASE_URL not set in settings'))
            return
        
        if not service_key:
            self.stdout.write(self.style.ERROR('❌ SUPABASE_SERVICE_ROLE_KEY not set in settings'))
            return
        
        if not bucket_name:
            self.stdout.write(self.style.ERROR('❌ SUPABASE_BUCKET not set in settings'))
            return

        self.stdout.write(f'✓ SUPABASE_URL: {supabase_url}')
        self.stdout.write(f'✓ SUPABASE_BUCKET: {bucket_name}')
        self.stdout.write(f'✓ SUPABASE_SERVICE_ROLE_KEY: ***\n')

        # Initialize Supabase client
        try:
            client = create_client(supabase_url, service_key)
            self.stdout.write(self.style.SUCCESS('✓ Connected to Supabase'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Failed to connect to Supabase: {str(e)}'))
            return

        # List existing buckets
        try:
            buckets = client.storage.list_buckets()
            bucket_names = [b.name for b in buckets]
            self.stdout.write(f'\n📦 Found {len(bucket_names)} bucket(s):')
            for bucket in bucket_names:
                self.stdout.write(f'  - {bucket}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Failed to list buckets: {str(e)}'))
            return

        # Check if our bucket exists
        if bucket_name in bucket_names:
            self.stdout.write(self.style.SUCCESS(f'\n✓ Bucket "{bucket_name}" already exists'))
        else:
            self.stdout.write(self.style.WARNING(f'\n⚠️  Bucket "{bucket_name}" not found. Creating...\n'))
            try:
                client.storage.create_bucket(bucket_name, options={"public": False})
                self.stdout.write(self.style.SUCCESS(f'✓ Successfully created bucket "{bucket_name}"'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Failed to create bucket: {str(e)}'))
                self.stdout.write('\n💡 Tip: Make sure your service role key has storage permissions')
                return

        self.stdout.write(self.style.SUCCESS('\n✅ Supabase bucket setup complete!'))
