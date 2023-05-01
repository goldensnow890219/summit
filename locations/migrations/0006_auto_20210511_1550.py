# Generated by Django 3.1.7 on 2021-05-11 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0005_professional_business_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='professional',
            name='email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name='professional',
            name='social_media_link_1',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='professional',
            name='social_media_link_2',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='professional',
            name='studio',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]