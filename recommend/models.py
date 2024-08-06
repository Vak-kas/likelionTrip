from django.db import models
from persona.models import User

class RecommendedPlace(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    place = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

class RecommendRoute(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sequence = models.IntegerField()
    place = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)  # description 필드 추가
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
