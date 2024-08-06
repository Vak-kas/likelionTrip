from django.contrib import admin
from .models import User, UserInfoPersona, Question, Picture, UserPersona, City

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('travel_user_id',)

@admin.register(UserInfoPersona)
class UserInfoPersonaAdmin(admin.ModelAdmin):
    list_display = ('user', 'mbti', 'visited_places', 'desired_places', 'tendency', 'ei', 'sn', 'ft', 'pj')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('user_info_persona', 'question1', 'question2', 'question3', 'question4', 'question5', 'question6', 'question7', 'question8', 'question9', 'question10')

@admin.register(Picture)
class PictureAdmin(admin.ModelAdmin):
    list_display = ('user_info_persona', 'picture1', 'picture2', 'picture3', 'picture4', 'picture5', 'picture6', 'picture7', 'picture8', 'picture9', 'picture10')

@admin.register(UserPersona)
class UserPersonaAdmin(admin.ModelAdmin):
    list_display = ('user_info_persona', 'word', 'count')

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('city', 'mbti')
