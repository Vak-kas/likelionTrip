# Generated by Django 5.0.7 on 2024-08-05 05:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('persona', '0006_alter_userpersona_count'),
        ('recommend', '0002_recommendplan'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecommendRoute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sequence', models.IntegerField()),
                ('place', models.CharField(max_length=255)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='persona.user')),
            ],
        ),
        migrations.DeleteModel(
            name='RecommendPlan',
        ),
    ]