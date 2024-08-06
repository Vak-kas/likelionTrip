from rest_framework import serializers
from .models import UserInfoPersona, Question, Picture, User

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

class PictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Picture
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['travel_user_id']

class UserInfoPersonaSerializer(serializers.ModelSerializer):
    question1 = serializers.IntegerField(write_only=True)
    question2 = serializers.IntegerField(write_only=True)
    question3 = serializers.IntegerField(write_only=True)
    question4 = serializers.IntegerField(write_only=True)
    question5 = serializers.IntegerField(write_only=True)
    question6 = serializers.IntegerField(write_only=True)
    question7 = serializers.IntegerField(write_only=True)
    question8 = serializers.IntegerField(write_only=True)
    question9 = serializers.IntegerField(write_only=True)
    question10 = serializers.IntegerField(write_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    picture1 = serializers.ImageField(required=False)
    picture2 = serializers.ImageField(required=False)
    picture3 = serializers.ImageField(required=False)
    picture4 = serializers.ImageField(required=False)
    picture5 = serializers.ImageField(required=False)
    picture6 = serializers.ImageField(required=False)
    picture7 = serializers.ImageField(required=False)
    picture8 = serializers.ImageField(required=False)
    picture9 = serializers.ImageField(required=False)
    picture10 = serializers.ImageField(required=False)
    picture11 = serializers.ImageField(required=False)
    picture12 = serializers.ImageField(required=False)
    picture13 = serializers.ImageField(required=False)
    picture14 = serializers.ImageField(required=False)
    picture15 = serializers.ImageField(required=False)

    class Meta:
        model = UserInfoPersona
        fields = ['user','mbti', 'visited_places', 'desired_places', 'tendency',
                  'question1', 'question2', 'question3', 'question4', 'question5',
                  'question6', 'question7', 'question8', 'question9', 'question10',
                  'picture1', 'picture2', 'picture3', 'picture4', 'picture5',
                  'picture6', 'picture7', 'picture8', 'picture9', 'picture10',
                  'picture11', 'picture12', 'picture13', 'picture14', 'picture15',
                  'ei', 'sn', 'ft', 'pj']

    def create(self, validated_data):
        question_data = {key: validated_data.pop(key) for key in [
            'question1', 'question2', 'question3', 'question4', 'question5',
            'question6', 'question7', 'question8', 'question9', 'question10'
        ]}

        picture_data = {
            'picture1': validated_data.pop('picture1', None),
            'picture2': validated_data.pop('picture2', None),
            'picture3': validated_data.pop('picture3', None),
            'picture4': validated_data.pop('picture4', None),
            'picture5': validated_data.pop('picture5', None),
            'picture6': validated_data.pop('picture6', None),
            'picture7': validated_data.pop('picture7', None),
            'picture8': validated_data.pop('picture8', None),
            'picture9': validated_data.pop('picture9', None),
            'picture10': validated_data.pop('picture10', None),
            'picture11': validated_data.pop('picture11', None),
            'picture12': validated_data.pop('picture12', None),
            'picture13': validated_data.pop('picture13', None),
            'picture14': validated_data.pop('picture14', None),
            'picture15': validated_data.pop('picture15', None),
        }

        user = validated_data.pop('user')

        user_info_persona, created = UserInfoPersona.objects.update_or_create(user=user, defaults=validated_data)

        # Create or update Question instance
        Question.objects.update_or_create(user_info_persona=user_info_persona, defaults=question_data)

        # Create or update Picture instances
        picture_instance, _ = Picture.objects.update_or_create(user_info_persona=user_info_persona)
        for field, file in picture_data.items():
            if file:
                setattr(picture_instance, field, file)
        picture_instance.save()

        return user_info_persona
