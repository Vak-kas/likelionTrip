from django.urls import path
from .views import CreateUserInfo, RecommendUserInfo, ListUserInfo

urlpatterns = [
    path('create_user_info/', CreateUserInfo.as_view(), name='create_user_info'),
    path('recommend/<int:travel_user_id>/', RecommendUserInfo.as_view(), name='recommend_user_info'),
    path('list/<int:travel_user_id>/', ListUserInfo.as_view(), name='list_user_info'),
]