# Generated by Django 5.0.7 on 2024-08-01 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0008_alter_tripdiary_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tripdiary',
            name='picture',
            field=models.URLField(blank=True, max_length=1024, null=True),
        ),
    ]
