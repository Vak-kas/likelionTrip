from django.urls import path
from .views import FriendUserInfo, NoFriendUserInfo

urlpatterns = [
    path('friends/<str:travel_user_id>/', FriendUserInfo.as_view(), name='friend-user-info'),
    path('no-friends/<str:travel_user_id>/', NoFriendUserInfo.as_view(), name='no-friend-user-info'),
]
