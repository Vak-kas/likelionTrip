# Generated by Django 5.0.7 on 2024-08-01 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0005_tripdiary_answer10_tripdiary_answer9_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tripdiary',
            name='picture1',
        ),
        migrations.RemoveField(
            model_name='tripdiary',
            name='picture10',
        ),
        migrations.RemoveField(
            model_name='tripdiary',
            name='picture2',
        ),
        migrations.RemoveField(
            model_name='tripdiary',
            name='picture3',
        ),
        migrations.RemoveField(
            model_name='tripdiary',
            name='picture4',
        ),
        migrations.RemoveField(
            model_name='tripdiary',
            name='picture5',
        ),
        migrations.RemoveField(
            model_name='tripdiary',
            name='picture6',
        ),
        migrations.RemoveField(
            model_name='tripdiary',
            name='picture7',
        ),
        migrations.RemoveField(
            model_name='tripdiary',
            name='picture8',
        ),
        migrations.RemoveField(
            model_name='tripdiary',
            name='picture9',
        ),
        migrations.AlterField(
            model_name='tripdiary',
            name='title',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
