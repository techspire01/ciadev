"""
Django management command to pre-convert images to WebP/AVIF formats.
Usage: python manage.py convert_images --format webp
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import os
from app.image_utils import convert_image_to_format


class Command(BaseCommand):
    help = 'Pre-convert images in media and static directories to WebP/AVIF'

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            type=str,
            default='webp',
            choices=['webp', 'avif'],
            help='Target image format (default: webp)',
        )
        parser.add_argument(
            '--media',
            action='store_true',
            help='Convert media files',
        )
        parser.add_argument(
            '--static',
            action='store_true',
            help='Convert static files',
        )

    def handle(self, *args, **options):
        target_format = options['format']
        convert_media = options['media'] or not (options['media'] or options['static'])
        convert_static = options['static'] or not (options['media'] or options['static'])
        
        converted_count = 0
        
        if convert_media:
            media_root = settings.MEDIA_ROOT
            self.stdout.write(f"Converting images in {media_root} to {target_format}...")
            for root, dirs, files in os.walk(media_root):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        file_path = os.path.join(root, file)
                        result = convert_image_to_format(file_path, target_format)
                        if result:
                            self.stdout.write(self.style.SUCCESS(f'✓ {file_path} → {target_format}'))
                            converted_count += 1
        
        if convert_static:
            static_root = settings.STATIC_ROOT if hasattr(settings, 'STATIC_ROOT') else os.path.join(settings.BASE_DIR, 'staticfiles')
            if os.path.exists(static_root):
                self.stdout.write(f"Converting images in {static_root} to {target_format}...")
                for root, dirs, files in os.walk(static_root):
                    for file in files:
                        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                            file_path = os.path.join(root, file)
                            result = convert_image_to_format(file_path, target_format)
                            if result:
                                self.stdout.write(self.style.SUCCESS(f'✓ {file_path} → {target_format}'))
                                converted_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'\nConversion complete! {converted_count} images converted to {target_format}.'))
