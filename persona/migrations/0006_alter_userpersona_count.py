# Generated by Django 5.0.7 on 2024-07-25 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('persona', '0005_picture_picture11_picture_picture12_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpersona',
            name='count',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
