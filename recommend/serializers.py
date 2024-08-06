from rest_framework import serializers
from .models import RecommendedPlace, RecommendRoute

class RecommendedPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendedPlace
        fields = ['id', 'user', 'place', 'latitude', 'longitude', 'created_at']


class RecommendRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendRoute
        fields = '__all__'
