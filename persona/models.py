# persona/models.py

from django.db import models

def user_directory_path(instance, filename):
    return f'pictures/user_{instance.user_info_persona.user.id}/{filename}'

class User(models.Model):
    travel_user_id = models.IntegerField(unique=True)
    model = models.BooleanField(default=False)

    def __str__(self):
        return str(self.travel_user_id)  # travel_user_id를 문자열로 반환

class UserInfoPersona(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mbti = models.CharField(max_length=4)
    visited_places = models.TextField()
    desired_places = models.TextField()
    tendency = models.CharField(max_length=255, null=True, blank=True)
    ei = models.IntegerField(null=True, blank=True)
    sn = models.IntegerField(null=True, blank=True)
    ft = models.IntegerField(null=True, blank=True)
    pj = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return str(self.user)  # user의 __str__ 메서드를 호출하여 travel_user_id를 반환

class Question(models.Model):
    user_info_persona = models.OneToOneField(UserInfoPersona, on_delete=models.CASCADE)
    question1 = models.IntegerField()
    question2 = models.IntegerField()
    question3 = models.IntegerField()
    question4 = models.IntegerField()
    question5 = models.IntegerField()
    question6 = models.IntegerField()
    question7 = models.IntegerField()
    question8 = models.IntegerField()
    question9 = models.IntegerField()
    question10 = models.IntegerField()

class Picture(models.Model):
    user_info_persona = models.OneToOneField(UserInfoPersona, on_delete=models.CASCADE)
    picture1 = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    picture2 = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    picture3 = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    picture4 = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    picture5 = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    picture6 = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    picture7 = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    picture8 = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    picture9 = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    picture10 = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    picture11 = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    picture12 = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    picture13 = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    picture14 = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    picture15 = models.ImageField(upload_to=user_directory_path, blank=True, null=True)

class UserPersona(models.Model):
    user_info_persona = models.ForeignKey(UserInfoPersona, on_delete=models.CASCADE)
    word = models.CharField(max_length=255)
    count = models.IntegerField(blank = True, null = True)

    def __str__(self):
        return f"{self.user_info_persona.user} - {self.word}"

class City(models.Model):
    city = models.CharField(max_length=255)
    mbti = models.CharField(max_length=4)
