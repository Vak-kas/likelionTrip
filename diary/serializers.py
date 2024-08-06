from rest_framework import serializers
from .models import TripDiary

class TripDiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = TripDiary
        fields = '__all__'

class TripDiarySummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = TripDiary
        fields = ['id', 'title', 'diary', 'created_at', 'picture', 'like']
