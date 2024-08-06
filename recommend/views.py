from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import RecommendedPlace, RecommendRoute
from .serializers import RecommendedPlaceSerializer, RecommendRouteSerializer
from persona.models import User, UserPersona
from openai import OpenAI
from django.conf import settings
from django.shortcuts import get_object_or_404
import re
import os

def get_openai_api_key():
    secret_dir = os.path.join(settings.BASE_DIR, 'secret')
    with open(os.path.join(secret_dir, 'API_KEY.txt'), 'r') as file:
        return file.read().strip()

class RecommendTravelPlaceAPIView(APIView):
    def post(self, request, format=None):
        travel_user_id = request.data.get('travel_user_id')
        if not travel_user_id:
            return Response({'error': 'travel_user_id is missing'}, status=status.HTTP_400_BAD_REQUEST)

        # 해당 유저의 UserPersona 가져오기
        user = get_object_or_404(User, travel_user_id=travel_user_id)

        # 기존에 저장된 RecommendPlace 데이터 삭제
        RecommendedPlace.objects.filter(user=user).delete()

        user_personas = UserPersona.objects.filter(user_info_persona__user=user)

        # 유저 페르소나 정보를 수집
        persona_info = [f"{persona.word} (Count: {persona.count})" for persona in user_personas]
        combined_persona_info = ', '.join(persona_info)

        # OpenAI GPT-4 API를 통해 여행지 추천 요청
        recommended_places = self.get_recommendation_from_openai(combined_persona_info)

        # 추천된 여행지 저장
        recommendations = []
        for place in recommended_places:
            recommendation = RecommendedPlace.objects.create(
                user=user,
                place=place['place'],
                latitude=place['latitude'],
                longitude=place['longitude']
            )
            recommendations.append(recommendation)

        serializer = RecommendedPlaceSerializer(recommendations, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    def get_recommendation_from_openai(self, persona_info):
        prompt = (
            f"여기 유저를 나타내는, 유저의 정보를 알려주는 페르소나 또는 단어들이 있어. \n\n{persona_info}\n\n"
            "이 정보들을 기초해서 사용자에게 적절한 여행지, 추천해 줄만한 여행지를 추천해줘. 대한민국(Republic of Korea) 지역으로"
            "예를 들어서 이 유저의 persona에 부산이란 정보가 있으면, 부산과 비슷한 도시들로 추천을 해줬으면 좋겠다는 거야. 10개정도 추천해줄래?"
            "단순히 '경주', '통영' 이렇게 가 아니라 '부산광역시', '경상남도 경주시' 이렇게 '시' 단위로 region을 알려줬으면 좋겠어."
            "이 형식을 지켜줘: {region, latitude, longitude},"
            "{region, latitude, logitude} 이 형식을 지키되, 하나의 형식이 다 출력되면, 엔터로 구분해줘.."
            "각 결과와 결과값 사이에 쉼표를 꼭 붙여주었으면 좋겠고 1, 2 이런 숫자 붙이지마. 그냥 {},{}, 이렇게 출력하는거야. 알았지?"
            "부가 설명은 필요없어"
        )

        key = get_openai_api_key()

        try:
            client = OpenAI(api_key=key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
                temperature=0.7,
                stream=True
            )

            recommended_places_text = ""
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    recommended_places_text += chunk.choices[0].delta.content
            print(recommended_places_text)
            # Parse the response text to extract places and their coordinates
            recommended_places = self.parse_recommended_places(recommended_places_text)
            print(f"여행지 결과는: {recommended_places}")

            return recommended_places
        except Exception as e:
            print(f"OpenAI API 호출 중 오류 발생: {e}")
            return []

    def parse_recommended_places(self, text):
        places = []

        # 각 엔트리를 줄 단위로 분리
        entries = text.split("},")
        for entry in entries:
            entry = entry.replace("{", "").replace("}", "").replace("\"", "").strip()
            parts = [part.strip() for part in entry.split(",")]
            if len(parts) == 3:
                place = parts[0]
                try:
                    latitude = float(parts[1])
                    longitude = float(parts[2])
                    places.append({'place': place, 'latitude': latitude, 'longitude': longitude})
                except ValueError:
                    print(f"Error parsing latitude/longitude for entry: {entry}")
                    continue  # 혹시라도 좌표가 숫자가 아니면 건너뜁니다.

        return places


class RecommendTravelRouteAPIView(APIView):
    def post(self, request, format=None):
        travel_user_id = request.data.get('travel_user_id')
        place = request.data.get('place')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')

        if not travel_user_id or not place or not start_date or not end_date:
            return Response({'error': 'travel_user_id, place, start_date, and end_date are required.'},
                            status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, travel_user_id=travel_user_id)

        # 기존에 추천된 경로 삭제
        RecommendRoute.objects.filter(user=user).delete()

        # 4개의 경로를 추천 받기
        all_routes = []
        for _ in range(3):
            travel_route = self.get_travel_route_from_openai(place, start_date, end_date)
            all_routes.append(travel_route)

        return Response(all_routes, status=status.HTTP_200_OK)

    def get_travel_route_from_openai(self, place, start_date, end_date):
        prompt = (
            f"사용자가 {place}을(를) 여행할 계획입니다. "
            f"여행의 시작 날짜는 {start_date}, 종료 날짜는 {end_date}입니다. "
            f"이 일정에 맞춰 {place}에서 갈 만한 주요 관광지와 그들의 위도와 경도, 그리고 간단한 설명을 포함한 여행 루트를 제안해 주세요. "
            f"결과 형식은 {{location, latitude, longitude, description}}으로 해주세요. "
            f"각 결과는 {{}}로 묶고, 각 결과 간에 쉼표로 구분해 주세요. 6개 정도 추천해줘"
            f"부연설명은 필요 없고, 한국어로 작성해줘"
            "각 결과와 결과값 사이에 쉼표를 꼭 붙여주었으면 좋겠고 1, 2 이런 숫자 붙이지마. 그냥 {},{}, 이렇게 출력하는거야. 알았지?"
            f"간단한 설명은 그냥 건물 이름이나 종류 이런 것을 부연 설명없이 알려주세요"
        )

        key = get_openai_api_key()

        try:
            client = OpenAI(api_key=key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
                temperature=0.7,
                stream=True
            )

            travel_route_text = ""
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    travel_route_text += chunk.choices[0].delta.content

            travel_route = self.parse_travel_route(travel_route_text)

            print(travel_route_text)
            print(travel_route)

            return travel_route
        except Exception as e:
            print(f"OpenAI API 호출 중 오류 발생: {e}")
            return []

    def parse_travel_route(self, text):
        routes = []

        entries = text.split("},")
        for entry in entries:
            entry = entry.replace("{", "").replace("}", "").replace("\"", "").strip()
            parts = [part.strip() for part in entry.split(",")]
            if len(parts) == 4:
                location = parts[0]
                try:
                    # print(type(parts[1]))
                    # print(type(parts[2]))
                    # print(type(parts[3]))
                    latitude = parts[1]
                    longitude = parts[2]
                    description = parts[3]
                    routes.append({
                        'location': location,
                        'latitude': latitude,
                        'longitude': longitude,
                        'description': description
                    })
                except ValueError:
                    print(f"Error parsing latitude/longitude for entry: {entry}")
                    continue

        return routes