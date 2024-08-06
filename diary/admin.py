from django.contrib import admin
from .models import TripDiary

class TripDiaryAdmin(admin.ModelAdmin):
    list_display = ('title', 'user_info_persona', 'created_at', 'updated_at')
    search_fields = ('title', 'diary', 'user_info_persona__user__travel_user_id')
    list_filter = ('created_at', 'updated_at')

admin.site.register(TripDiary, TripDiaryAdmin)
