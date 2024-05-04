# Generated by Django 5.0.4 on 2024-05-04 12:41

import blog_api.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog_api', '0002_alter_blog_created_at_alter_category_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='image',
            field=models.ImageField(default='default.jpg', upload_to=blog_api.models.upload_to, verbose_name='Image'),
        ),
    ]