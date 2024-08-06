from django.db import models
from persona.models import UserInfoPersona

def user_directory_path(instance, filename):
    return f'pictures/user_{instance.user_info_persona.user.id}/diary/{filename}'

class TripDiary(models.Model):
    user_info_persona = models.ForeignKey(UserInfoPersona, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, unique=True)

    question1 = models.TextField()
    answer1 = models.TextField()
    question2 = models.TextField()
    answer2 = models.TextField()
    question3 = models.TextField()
    answer3 = models.TextField()
    question4 = models.TextField()
    answer4 = models.TextField()
    question5 = models.TextField()
    answer5 = models.TextField()
    question6 = models.TextField()
    answer6 = models.TextField()
    question7 = models.TextField()
    answer7 = models.TextField()
    question8 = models.TextField()
    answer8 = models.TextField()
    question9 = models.TextField()
    answer9 = models.TextField()
    question10 = models.TextField()
    answer10 = models.TextField()

    diary = models.TextField(blank=True, null=True)
    picture = models.URLField(max_length=1024, blank=True, null=True)
    real_picture = models.ImageField(blank=True, null=True)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank = True, null = True)

    like = models.BooleanField(default = False)



