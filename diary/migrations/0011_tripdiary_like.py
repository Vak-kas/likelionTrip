# Generated by Django 5.0.7 on 2024-08-05 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0010_tripdiary_real_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='tripdiary',
            name='like',
            field=models.BooleanField(default=False),
        ),
    ]