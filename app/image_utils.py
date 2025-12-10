"""
Image processing utilities for WebP/AVIF conversion and responsive images.
Requires Pillow with WebP/AVIF support.
"""
import os
from pathlib import Path
from django.core.files.storage import default_storage
from PIL import Image
import io

SUPPORTED_FORMATS = {
    'webp': 'image/webp',
    'avif': 'image/avif',
}

MIN_QUALITY = 75  # Balance quality/size


def convert_image_to_format(image_path, target_format='webp'):
    """
    Convert an image file to WebP or AVIF format.
    Returns the new file path or None if conversion fails.
    """
    if not os.path.exists(image_path):
        return None
    
    try:
        img = Image.open(image_path)
        # Handle RGBA transparency
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        base_path = os.path.splitext(image_path)[0]
        new_path = f"{base_path}.{target_format}"
        
        save_kwargs = {'quality': MIN_QUALITY, 'optimize': True}
        if target_format == 'avif':
            save_kwargs = {'quality': MIN_QUALITY}
        
        img.save(new_path, format=target_format.upper(), **save_kwargs)
        return new_path
    except Exception as e:
        print(f"Image conversion failed for {image_path}: {e}")
        return None


def get_responsive_image_sources(image_path):
    """
    Generate srcset and sources for responsive/format images.
    Returns dict with original, webp, and avif paths.
    """
    result = {
        'original': image_path,
        'webp': None,
        'avif': None,
    }
    
    # Try converting to WebP and AVIF
    for fmt in ['webp', 'avif']:
        converted = convert_image_to_format(image_path, fmt)
        if converted:
            result[fmt] = converted
    
    return result


def generate_picture_tag(image_path, alt_text='', css_classes=''):
    """
    Generate a <picture> tag with WebP/AVIF fallback.
    Usage in template: {{ image_path|picture_tag:"alt text" }}
    """
    sources = get_responsive_image_sources(image_path)
    
    html = f'<picture>'
    if sources['avif']:
        html += f'\n  <source srcset="{sources["avif"]}" type="image/avif">'
    if sources['webp']:
        html += f'\n  <source srcset="{sources["webp"]}" type="image/webp">'
    html += f'\n  <img src="{sources["original"]}" alt="{alt_text}" loading="lazy" class="{css_classes}" />'
    html += f'\n</picture>'
    
    return html
