# Generated by Django 5.0.7 on 2024-08-26 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_userprofile_zip_number'),
        ('products', '0002_alter_product_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='product_favorites',
            field=models.ManyToManyField(to='products.product'),
        ),
    ]
