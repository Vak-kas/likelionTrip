from django.db import models
from persona.models import UserInfoPersona, User

class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ai_tell = models.TextField()  # AI가 한 질문
    person_tell = models.TextField()  # 사용자가 한 대답
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.travel_user_id}: {self.ai_tell} - {self.person_tell}"
