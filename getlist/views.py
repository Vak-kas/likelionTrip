from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from persona.models import User, UserInfoPersona
from django.shortcuts import get_object_or_404
from django.db.models import Q


def calculate_similarity(persona1, persona2):
    score_diff = (
            abs(persona1.ei - persona2.ei) +
            abs(persona1.sn - persona2.sn) +
            abs(persona1.ft - persona2.ft) +
            abs(persona1.pj - persona2.pj)
    )
    compatibility = 100 - (score_diff // 4)
    return compatibility


class FriendUserInfo(APIView):
    def post(self, request, travel_user_id, format=None):
        friend_ids = request.data.get('list', [])

        user = get_object_or_404(User, travel_user_id=travel_user_id)
        user_persona = get_object_or_404(UserInfoPersona, user=user)

        friend_personas = UserInfoPersona.objects.filter(user__travel_user_id__in=friend_ids)

        similar_users = [{
            "travel_user_id": persona.user.travel_user_id,
            "tendency": persona.tendency,
            "ei": persona.ei,
            "sn": persona.sn,
            "ft": persona.ft,
            "pj": persona.pj,
            "compatibility": calculate_similarity(user_persona, persona)
        } for persona in friend_personas]

        # 본인 정보 추가
        self_info = {
            "travel_user_id": user_persona.user.travel_user_id,
            "tendency": user_persona.tendency,
            "ei": user_persona.ei,
            "sn": user_persona.sn,
            "ft": user_persona.ft,
            "pj": user_persona.pj
        }

        return Response({"list": similar_users, "self": self_info}, status=status.HTTP_200_OK)


class NoFriendUserInfo(APIView):
    def post(self, request, travel_user_id, format=None):
        friend_ids = request.data.get('list', [])

        user = get_object_or_404(User, travel_user_id=travel_user_id)
        user_persona = get_object_or_404(UserInfoPersona, user=user)

        # 친구 목록에 없는 사용자 중에서 20명을 선택
        no_friend_personas = UserInfoPersona.objects.filter(~Q(user__travel_user_id__in=friend_ids)).exclude(user=user)[
                             :20]

        similar_users = [{
            "travel_user_id": persona.user.travel_user_id,
            "tendency": persona.tendency,
            "ei": persona.ei,
            "sn": persona.sn,
            "ft": persona.ft,
            "pj": persona.pj,
            "compatibility": calculate_similarity(user_persona, persona)
        } for persona in no_friend_personas]

        # 본인 정보 추가
        self_info = {
            "travel_user_id": user_persona.user.travel_user_id,
            "tendency": user_persona.tendency,
            "ei": user_persona.ei,
            "sn": user_persona.sn,
            "ft": user_persona.ft,
            "pj": user_persona.pj
        }

        return Response({"list": similar_users, "self": self_info}, status=status.HTTP_200_OK)
