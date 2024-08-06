from django.contrib import admin
from .models import RecommendedPlace, RecommendRoute

@admin.register(RecommendedPlace)
class RecommendedPlaceAdmin(admin.ModelAdmin):
    list_display = ('user', 'place', 'latitude', 'longitude', 'created_at')
    search_fields = ('user__travel_user_id', 'place')

@admin.register(RecommendRoute)
class RecommendRouteAdmin(admin.ModelAdmin):
    list_display = ('user', 'sequence', 'place', 'start_date', 'end_date', 'description', 'created_at')
    search_fields = ('user__travel_user_id', 'place')
    list_filter = ('start_date', 'end_date')
