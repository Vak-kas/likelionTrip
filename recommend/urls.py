from django.urls import path
from .views import RecommendTravelPlaceAPIView, RecommendTravelRouteAPIView

urlpatterns = [
    path('places/', RecommendTravelPlaceAPIView.as_view(), name='recommend-place'),
    path('route/', RecommendTravelRouteAPIView.as_view(), name='generate-route'),
]

