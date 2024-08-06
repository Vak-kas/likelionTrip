from django.contrib import admin
from .models import Chat

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('user', 'ai_tell', 'person_tell', 'timestamp')
    search_fields = ('user__travel_user_id', 'ai_tell', 'person_tell')
    list_filter = ('timestamp',)
    ordering = ('-timestamp',)
