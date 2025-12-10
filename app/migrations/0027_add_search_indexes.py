# Generated migration for search performance optimization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0026_contactinformation_facebook_and_more'),
    ]

    operations = [
        # Add indexes on frequently searched/filtered fields
        migrations.AddIndex(
            model_name='supplier',
            index=models.Index(fields=['name'], name='supplier_name_idx'),
        ),
        migrations.AddIndex(
            model_name='supplier',
            index=models.Index(fields=['category'], name='supplier_category_idx'),
        ),
        migrations.AddIndex(
            model_name='supplier',
            index=models.Index(fields=['sub_category1'], name='supplier_sub_cat1_idx'),
        ),
        migrations.AddIndex(
            model_name='supplier',
            index=models.Index(fields=['sub_category2'], name='supplier_sub_cat2_idx'),
        ),
        migrations.AddIndex(
            model_name='supplier',
            index=models.Index(fields=['sub_category3'], name='supplier_sub_cat3_idx'),
        ),
        migrations.AddIndex(
            model_name='supplier',
            index=models.Index(fields=['product1'], name='supplier_product1_idx'),
        ),
        migrations.AddIndex(
            model_name='supplier',
            index=models.Index(fields=['product2'], name='supplier_product2_idx'),
        ),
        migrations.AddIndex(
            model_name='supplier',
            index=models.Index(fields=['product3'], name='supplier_product3_idx'),
        ),
    ]
