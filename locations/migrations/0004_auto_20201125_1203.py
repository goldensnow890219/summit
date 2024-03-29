# Generated by Django 3.1.2 on 2020-11-25 12:03

from django.db import migrations, models
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0003_auto_20201028_2232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='professional',
            name='services',
            field=modelcluster.fields.ParentalManyToManyField(blank=True, to='locations.Service'),
        ),
        migrations.AlterField(
            model_name='locationpage',
            name='address_line',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name='locationpage',
            name='city',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name='locationpage',
            name='state_code',
            field=models.CharField(blank=True, max_length=2),
        ),
        migrations.AlterField(
            model_name='locationpage',
            name='zip_code',
            field=models.CharField(blank=True, max_length=7),
        ),
    ]
