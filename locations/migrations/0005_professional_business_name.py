# Generated by Django 3.1.7 on 2021-05-11 01:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0004_auto_20201125_1203'),
    ]

    operations = [
        migrations.AddField(
            model_name='professional',
            name='business_name',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
