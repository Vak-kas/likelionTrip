from django.urls import path
from .views import TripDiaryListCreateAPIView, TripDiaryDetailAPIView, LikedTripDiaryListAPIView

urlpatterns = [
    path('<int:travel_user_id>/', TripDiaryListCreateAPIView.as_view(), name='diary-list-create'),
    path('<int:travel_user_id>/detail/<int:pk>/', TripDiaryDetailAPIView.as_view(), name='diary-detail'),
    path('<int:travel_user_id>/liked/', LikedTripDiaryListAPIView.as_view(), name='liked-trip-diary-list'),
]

