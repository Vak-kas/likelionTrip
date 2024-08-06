from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Chat
from .serializers import ChatSerializer
from persona.models import User, UserInfoPersona, UserPersona
from django.shortcuts import get_object_or_404
from openai import OpenAI
from django.conf import settings
from konlpy.tag import Okt
from collections import Counter
import re
import os

okt = Okt()

def get_openai_api_key():
    secret_dir = os.path.join(settings.BASE_DIR, 'secret')
    with open(os.path.join(secret_dir, 'API_KEY.txt'), 'r') as file:
        return file.read().strip()

def clean_text(text):
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def maintain_user_persona_count(user_info_persona):
    user = user_info_persona.user
    if hasattr(user, 'model') and user.model:
        max_count = 10000
    else:
        max_count = 1500

    persona_count = UserPersona.objects.filter(user_info_persona=user_info_persona).count()
    if persona_count > max_count:
        over_count = persona_count - max_count
        persona_to_delete = UserPersona.objects.filter(user_info_persona=user_info_persona).order_by('?')[:over_count]
        persona_to_delete.delete()

class AIChatAPIView(APIView):
    def get(self, request, travel_user_id, format=None):
        user = get_object_or_404(User, travel_user_id=travel_user_id)
        chats = Chat.objects.filter(user=user).order_by('timestamp')

        if not chats.exists():
            ai_tell = self.get_initial_ai_question(user)
            Chat.objects.create(user=user, ai_tell=ai_tell)
            return Response({"ai_tell": ai_tell, "history": []}, status=status.HTTP_200_OK)

        chat_history = []
        for chat in chats:
            chat_history.append(f"AI: {chat.ai_tell}")
            chat_history.append(f"User: {chat.person_tell}")

        return Response({"history": chat_history}, status=status.HTTP_200_OK)

    def post(self, request, travel_user_id, format=None):
        user_input = request.data.get("person_tell", "")
        if not user_input:
            return Response({"error": "User input is required."}, status=status.HTTP_400_BAD_REQUEST)

        # 가장 최근의 Chat 객체에 사용자 입력 저장
        last_chat = Chat.objects.filter(user_id=travel_user_id).last()
        last_chat.person_tell = user_input
        last_chat.save()

        # 사용자 입력을 바탕으로 AI 응답 생성
        new_ai_question = self.generate_ai_response(travel_user_id, user_input)

        # 새로 생성된 질문을 새로운 Chat 객체로 저장
        Chat.objects.create(user_id=travel_user_id, ai_tell=new_ai_question)

        # 질문/답변이 25개를 초과하면 오래된 것부터 삭제
        self.ensure_chat_limit(travel_user_id, limit=25)

        # 유저 페르소나 업데이트
        self.update_user_persona(travel_user_id, user_input)

        return Response({"AI": new_ai_question}, status=status.HTTP_200_OK)

    def ensure_chat_limit(self, travel_user_id, limit):
        chats = Chat.objects.filter(user_id=travel_user_id).order_by('timestamp')
        if chats.count() > limit:
            # 오래된 것부터 삭제
            excess_count = chats.count() - limit
            chats[:excess_count].delete()
    def generate_ai_response(self, travel_user_id, user_input):
        persona = UserInfoPersona.objects.filter(user_id=travel_user_id).first()
        persona_info = f"이 사람의 Persona는 {persona.mbti}이며, {persona.tendency} 성향입니다." if persona else ""
        prompt = (
            f"이 사람의 답변은 다음과 같습니다: '{user_input}'\n"
            f"{persona_info}\n"
            "이 사람에게 어울리는 말투로 다음 질문을 해주세요."
        )

        key = get_openai_api_key()
        client = OpenAI(api_key=key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7,
            stream=True
        )
        content = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content += chunk.choices[0].delta.content
        return content

    def get_initial_ai_question(self, user):
        user_persona = get_object_or_404(UserInfoPersona, user=user)
        prompt = (
            f"이 사용자의 페르소나는: {user_persona} 입니다. "
            "이 사용자에게 어울리는 첫 번째 질문을 만들어주세요. "
            "사용자의 페르소나에 어울리는 말투로 질문해 주세요."
        )
        key = get_openai_api_key()

        client = OpenAI(api_key=key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=150,
            temperature=0.7,
            stream=True
        )
        content = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content += chunk.choices[0].delta.content
        return content

    def get_ai_response(self, user_persona, messages):
        prompt = (
            f"이 사용자의 페르소나는: {user_persona} 입니다. "
            "다음 대화를 기반으로 적절한 질문 또는 답변을 생성해 주세요. "
            "사용자의 페르소나에 어울리는 말투로 대답해 주세요."
        )
        key = get_openai_api_key()

        client = OpenAI(api_key=key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}] + messages,
            max_tokens=150,
            temperature=0.7,
            stream=True
        )
        content = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content += chunk.choices[0].delta.content
        return content

    def update_user_persona(self, travel_user_id, text):
        user_persona = get_object_or_404(UserInfoPersona, user_id=travel_user_id)
        words = okt.morphs(clean_text(text))
        word_counts = Counter(words)

        for word, count in word_counts.items():
            user_persona_obj, created = UserPersona.objects.get_or_create(
                user_info_persona=user_persona,
                word=word,
                defaults={'count': 0}  # count를 0으로 초기화
            )
            if not created:
                if user_persona_obj.count is None:
                    user_persona_obj.count = 0
                user_persona_obj.count += count
            else:
                user_persona_obj.count = count
            user_persona_obj.save()

        maintain_user_persona_count(user_persona)
