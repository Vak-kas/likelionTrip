from django.urls import path
from .views import AIChatAPIView

urlpatterns = [
    path('<str:travel_user_id>/', AIChatAPIView.as_view(), name='chat-api'),
]
