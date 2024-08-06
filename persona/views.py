from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserInfoPersonaSerializer
from .models import User, City, UserInfoPersona, Picture
from .logic import picture_logic, get_city_mbti
from .question import question_logic
from django.db import transaction

score = 20

class CreateUserInfo(APIView):
    @transaction.atomic
    def post(self, request, format=None):
        travel_user_id = request.data.get('travel_user_id')
        if not travel_user_id:
            return Response({'error': 'travel_user_id is missing'}, status=status.HTTP_400_BAD_REQUEST)

        user, created = User.objects.get_or_create(travel_user_id=travel_user_id)

        validated_data = request.data.copy()
        validated_data['user'] = user.id
        print(f"데이터 : {validated_data}")

        serializer = UserInfoPersonaSerializer(data=validated_data)
        if serializer.is_valid():
            try:
                user_info_persona = serializer.save()

                questions = {key: int(request.data.get(key)) for key in [
                    'question1', 'question2', 'question3', 'question4', 'question5',
                    'question6', 'question7', 'question8', 'question9', 'question10'
                ]}
                self.process_persona_and_tendency(user_info_persona, questions)

                # 유저의 tendency를 반환
                return Response({'tendency': user_info_persona.tendency}, status=status.HTTP_201_CREATED)
            except Exception as e:
                transaction.set_rollback(True)
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        print(f"에러 : {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def process_persona_and_tendency(self, user_info_persona, questions):
        mbti = user_info_persona.mbti
        visited_places = user_info_persona.visited_places.split(', ')
        desired_places = user_info_persona.desired_places.split(', ')
        question_mbti_counts = question_logic(questions)
        picture_mbti_counts = picture_logic(user_info_persona)

        print(f"visited_places : {visited_places}")
        print(f"desired_places : {desired_places}")
        print(f"question_mbti_count : {question_mbti_counts}")
        print(f"picture_mbti_count : {picture_mbti_counts}")

        def get_mbti_counts_from_mbti(mbti):
            mbti_counts = {'E': 0, 'I': 0, 'N': 0, 'S': 0, 'T': 0, 'F': 0, 'J': 0, 'P': 0}
            for char in mbti:
                mbti_counts[char] = 3
            return mbti_counts

        mbti_counts_from_input = get_mbti_counts_from_mbti(mbti)

        def get_combined_mbti_counts(places):
            mbti_counts = {'E': 0, 'I': 0, 'N': 0, 'S': 0, 'T': 0, 'F': 0, 'J': 0, 'P': 0}
            for place in places:
                try:
                    city = City.objects.get(city=place)
                    city_mbti = city.mbti
                    counts = {
                        'E': 5 if 'E' in city_mbti else 0,
                        'I': 5 if 'I' in city_mbti else 0,
                        'N': 5 if 'N' in city_mbti else 0,
                        'S': 5 if 'S' in city_mbti else 0,
                        'T': 5 if 'T' in city_mbti else 0,
                        'F': 5 if 'F' in city_mbti else 0,
                        'J': 5 if 'J' in city_mbti else 0,
                        'P': 5 if 'P' in city_mbti else 0,
                    }
                    for key in counts:
                        mbti_counts[key] += counts[key]
                except City.DoesNotExist:
                    city_mbti = get_city_mbti(place)
                    mbti_type = ''.join(city_mbti.keys())
                    City.objects.create(
                        city=place,
                        mbti=mbti_type,
                    )
                    counts = {
                        'E': 5 if 'E' in mbti_type else 0,
                        'I': 5 if 'I' in mbti_type else 0,
                        'N': 5 if 'N' in mbti_type else 0,
                        'S': 5 if 'S' in mbti_type else 0,
                        'T': 5 if 'T' in mbti_type else 0,
                        'F': 5 if 'F' in mbti_type else 0,
                        'J': 5 if 'J' in mbti_type else 0,
                        'P': 5 if 'P' in mbti_type else 0,
                    }
                    for key in counts:
                        mbti_counts[key] += counts[key]
            return mbti_counts

        visited_places_mbti_counts = get_combined_mbti_counts(visited_places)
        desired_places_mbti_counts = get_combined_mbti_counts(desired_places)

        combined_mbti_counts = {key: picture_mbti_counts.get(key, 0) +
                                     visited_places_mbti_counts.get(key, 0) +
                                     desired_places_mbti_counts.get(key, 0) +
                                     mbti_counts_from_input.get(key, 0) +
                                     question_mbti_counts.get(key, 0)
                                for key in question_mbti_counts}

        def get_tendency_and_scores(mbti_counts):
            tendency = ''
            scores = {}
            for pair in [('E', 'I'), ('S', 'N'), ('T', 'F'), ('J', 'P')]:
                if mbti_counts[pair[0]] > mbti_counts[pair[1]]:
                    tendency += pair[0]
                    scores[pair[0].lower()] = round(
                        mbti_counts[pair[0]] / (mbti_counts[pair[0]] + mbti_counts[pair[1]]) * 100)
                else:
                    tendency += pair[1]
                    scores[pair[1].lower()] = round(
                        mbti_counts[pair[1]] / (mbti_counts[pair[0]] + mbti_counts[pair[1]]) * 100)
            return tendency, scores

        tendency, scores = get_tendency_and_scores(combined_mbti_counts)
        print(f"{user_info_persona}은 {tendency} 이고, 점수는 {scores}")

        user_info_persona.tendency = tendency
        user_info_persona.ei = scores.get(tendency[0].lower(), 0)
        user_info_persona.sn = scores.get(tendency[1].lower(), 0)
        user_info_persona.ft = scores.get(tendency[2].lower(), 0)
        user_info_persona.pj = scores.get(tendency[3].lower(), 0)
        user_info_persona.save()


class RecommendUserInfo(APIView):
    def get(self, request, travel_user_id, format=None):
        try:
            user = User.objects.get(travel_user_id=travel_user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            user_info_persona = UserInfoPersona.objects.get(user=user)
        except UserInfoPersona.DoesNotExist:
            return Response({'error': 'User info persona not found'}, status=status.HTTP_404_NOT_FOUND)

        user_tendency = user_info_persona.tendency

        # 성향이 같은 사용자들 목록 가져오기
        similar_personas = UserInfoPersona.objects.filter(tendency=user_tendency).exclude(user=user)

        # 유사도를 계산하기 위해 점수 차이 계산
        def calculate_similarity(persona):
            score_diff = (
                abs(user_info_persona.ei - persona.ei) +
                abs(user_info_persona.sn - persona.sn) +
                abs(user_info_persona.ft - persona.ft) +
                abs(user_info_persona.pj - persona.pj)
            )

            # print(score_diff)
            compatibility = 100 - (score_diff // 4)
            # print(compatibility)
            return score_diff, compatibility

        # 유사도에 따라 정렬
        sorted_personas_with_compatibility = sorted(
            [(persona, *calculate_similarity(persona)) for persona in similar_personas],
            key=lambda x: x[1]
        )

        # 상위 10명의 사용자 정보 가져오기
        top_similar_users = [{
            "travel_user_id": persona.user.travel_user_id,
            "tendency": persona.tendency,
            "ei": persona.ei,
            "sn": persona.sn,
            "ft": persona.ft,
            "pj": persona.pj,
            "compatibility": compatibility
        } for persona, score_diff, compatibility in sorted_personas_with_compatibility[:10]]

        # 현재 사용자의 정보
        self_info = {
            "travel_user_id": user_info_persona.user.travel_user_id,
            "tendency": user_info_persona.tendency,
            "ei": user_info_persona.ei,
            "sn": user_info_persona.sn,
            "ft": user_info_persona.ft,
            "pj": user_info_persona.pj
        }

        return Response({"list": top_similar_users, "self": self_info}, status=status.HTTP_200_OK)



class ListUserInfo(APIView):
    def get(self, request, travel_user_id, format=None):
        try:
            user = User.objects.get(travel_user_id=travel_user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            user_info_persona = UserInfoPersona.objects.get(user=user)
        except UserInfoPersona.DoesNotExist:
            return Response({'error': 'User info persona not found'}, status=status.HTTP_404_NOT_FOUND)

        user_tendency = user_info_persona.tendency

        # 성향이 같은 사용자들 목록 가져오기
        similar_personas = UserInfoPersona.objects.filter(tendency=user_tendency).exclude(user=user)

        # 유사도를 계산하기 위해 점수 차이 계산
        def calculate_similarity(persona):
            score_diff = (
                abs(user_info_persona.ei - persona.ei) +
                abs(user_info_persona.sn - persona.sn) +
                abs(user_info_persona.ft - persona.ft) +
                abs(user_info_persona.pj - persona.pj)
            )
            return score_diff

        # 유사도에 따라 정렬
        sorted_personas = sorted(similar_personas, key=calculate_similarity)

        # 상위 10명의 travel_user_id만 리스트로 가져오기
        top_similar_user_ids = [
            persona.user.travel_user_id for persona in sorted_personas[:score]
            if persona.user.travel_user_id != travel_user_id
        ]

        return Response({"list": top_similar_user_ids}, status=status.HTTP_200_OK)


