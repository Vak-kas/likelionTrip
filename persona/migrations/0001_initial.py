# Generated by Django 5.0.7 on 2024-07-20 19:06

import django.db.models.deletion
import persona.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(max_length=255)),
                ('mbti', models.CharField(max_length=4)),
                ('ei', models.IntegerField()),
                ('sn', models.IntegerField()),
                ('ft', models.IntegerField()),
                ('pj', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('travel_user_id', models.IntegerField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserInfoPersona',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mbti', models.CharField(max_length=4)),
                ('visited_places', models.TextField()),
                ('desired_places', models.TextField()),
                ('tendency', models.CharField(blank=True, max_length=255, null=True)),
                ('ei', models.IntegerField(blank=True, null=True)),
                ('sn', models.IntegerField(blank=True, null=True)),
                ('ft', models.IntegerField(blank=True, null=True)),
                ('pj', models.IntegerField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='persona.user')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question1', models.IntegerField()),
                ('question2', models.IntegerField()),
                ('question3', models.IntegerField()),
                ('question4', models.IntegerField()),
                ('question5', models.IntegerField()),
                ('question6', models.IntegerField()),
                ('question7', models.IntegerField()),
                ('question8', models.IntegerField()),
                ('question9', models.IntegerField()),
                ('question10', models.IntegerField()),
                ('user_info_persona', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='persona.userinfopersona')),
            ],
        ),
        migrations.CreateModel(
            name='Picture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('picture1', models.ImageField(blank=True, null=True, upload_to=persona.models.user_directory_path)),
                ('picture2', models.ImageField(blank=True, null=True, upload_to=persona.models.user_directory_path)),
                ('picture3', models.ImageField(blank=True, null=True, upload_to=persona.models.user_directory_path)),
                ('picture4', models.ImageField(blank=True, null=True, upload_to=persona.models.user_directory_path)),
                ('picture5', models.ImageField(blank=True, null=True, upload_to=persona.models.user_directory_path)),
                ('picture6', models.ImageField(blank=True, null=True, upload_to=persona.models.user_directory_path)),
                ('picture7', models.ImageField(blank=True, null=True, upload_to=persona.models.user_directory_path)),
                ('picture8', models.ImageField(blank=True, null=True, upload_to=persona.models.user_directory_path)),
                ('picture9', models.ImageField(blank=True, null=True, upload_to=persona.models.user_directory_path)),
                ('picture10', models.ImageField(blank=True, null=True, upload_to=persona.models.user_directory_path)),
                ('user_info_persona', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='persona.userinfopersona')),
            ],
        ),
        migrations.CreateModel(
            name='UserPersona',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=255)),
                ('count', models.IntegerField()),
                ('user_info_persona', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='persona.userinfopersona')),
            ],
        ),
    ]