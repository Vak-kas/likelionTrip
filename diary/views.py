from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import TripDiary
from .serializers import TripDiarySerializer, TripDiarySummarySerializer
from persona.models import UserInfoPersona, User
from django.shortcuts import get_object_or_404
from openai import OpenAI
from django.conf import settings
from django.core.files.base import ContentFile
from base64 import b64decode
import os


def get_openai_api_key():
    secret_dir = os.path.join(settings.BASE_DIR, 'secret')
    with open(os.path.join(secret_dir, 'API_KEY.txt'), 'r') as file:
        return file.read().strip()


class TripDiaryListCreateAPIView(APIView):

    def get(self, request, travel_user_id, format=None):
        user = get_object_or_404(User, travel_user_id=travel_user_id)
        user_persona = get_object_or_404(UserInfoPersona, user=user)

        # 최신 순으로 정렬
        diaries = TripDiary.objects.filter(user_info_persona=user_persona).order_by('-created_at').only('id',
            'title',
             'diary',
             'created_at',
             'real_picture',
             'like')


        serializer = TripDiarySummarySerializer(diaries, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, travel_user_id, format=None):
        user = get_object_or_404(User, travel_user_id=travel_user_id)
        user_persona = get_object_or_404(UserInfoPersona, user=user)

        validated_data = request.data.copy()
        validated_data['user_info_persona'] = user_persona.id

        questions_and_answers = []
        for i in range(1, 11):
            question = request.data.get(f'question{i}')
            answer = request.data.get(f'answer{i}')
            if question and answer:
                questions_and_answers.append(f"{i}번 질문: {question}\n{i}번 답변: {answer}")

        content = self.generate_diary_content(questions_and_answers)

        title = request.data.get('title')
        validated_data['title'] = title
        validated_data['diary'] = content

        serializer = TripDiarySerializer(data=validated_data)
        if serializer.is_valid():
            diary = serializer.save()
            self.generate_and_save_image(diary)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def generate_diary_content(self, questions_and_answers):
        prompt = (
                "아래 질문과 답변들을 기반으로 여행일기를 작성해 주세요:\n\n" +
                "\n\n".join(questions_and_answers) +
                "\n\n이 내용을 바탕으로 여행일기를 작성해 주세요."
                "단 **특별한점 ** 이런 식의 부가설명은 없이 해주세요"
                "2~3문장으로 요약해줘"
        )
        key = get_openai_api_key()

        try:
            client = OpenAI(api_key=key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7,
                stream=True
            )
            content = ""
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    content += chunk.choices[0].delta.content
            return content
        except Exception as e:
            print(f"OpenAI API 호출 중 오류 발생: {e}")
            return "내용 생성에 실패했습니다."

    def generate_and_save_image(self, diary):
        try:
            key = get_openai_api_key()
            client = OpenAI(api_key=key)

            # Generating an image using the diary content as a prompt
            response = client.images.generate(
                prompt=diary.diary,
                n=1,
                size="1024x1024",
                quality="hd",
                response_format="b64_json"
            )

            image_data = b64decode(response.data[0].b64_json)
            image_file = f"{diary.id}.png"

            # Save the image file to the desired location
            save_path = os.path.join('media', f'user_{diary.user_info_persona.user.id}', 'diary', image_file)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            with open(save_path, 'wb') as file:
                file.write(image_data)

            # Save the URL to the picture field
            diary.picture = save_path  # 경로를 저장하거나 이미지 URL을 저장하는 로직을 여기에 추가하세요
            diary.save()

            # Save the image to the real_picture field in the model
            diary.real_picture.save(image_file, ContentFile(image_data))
            diary.save()

        except Exception as e:
            print(f"OpenAI API 호출 중 오류 발생: {e}")


class TripDiaryDetailAPIView(APIView):
    def get_object(self, pk, user_persona):
        return get_object_or_404(TripDiary, pk=pk, user_info_persona=user_persona)

    def get(self, request, travel_user_id, pk, format=None):
        user = get_object_or_404(User, travel_user_id=travel_user_id)
        user_persona = get_object_or_404(UserInfoPersona, user=user)

        diary = self.get_object(pk, user_persona)

        serializer = TripDiarySerializer(diary, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


    def delete(self, request, travel_user_id, pk, format=None):
        user = get_object_or_404(User, travel_user_id=travel_user_id)
        user_persona = get_object_or_404(UserInfoPersona, user=user)

        diary = self.get_object(pk, user_persona)
        diary.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, travel_user_id, pk, format=None):
        user = get_object_or_404(User, travel_user_id=travel_user_id)
        user_persona = get_object_or_404(UserInfoPersona, user=user)

        diary = self.get_object(pk, user_persona)

        # 요청에서 like 값을 가져와 업데이트
        like_status = request.data.get('like')
        if like_status is not None:
            diary.like = like_status
            diary.save()

        serializer = TripDiarySerializer(diary, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class LikedTripDiaryListAPIView(APIView):
    def get(self, request, travel_user_id, format=None):
        user = get_object_or_404(User, travel_user_id=travel_user_id)
        user_persona = get_object_or_404(UserInfoPersona, user=user)

        # 좋아요가 달린 일기만 필터링하고, 최신순으로 정렬
        liked_diaries = TripDiary.objects.filter(user_info_persona=user_persona, like=True).order_by(
            '-created_at').only('id', 'title', 'diary', 'created_at', 'real_picture', 'like')

        serializer = TripDiarySummarySerializer(liked_diaries, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)