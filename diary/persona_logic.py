import os
import requests
from PIL import Image
from persona.models import UserPersona
from konlpy.tag import Okt
from django.conf import settings
from openai import OpenAI
from collections import Counter
import re

okt = Okt()

def get_api_keys():
    secret_dir = os.path.join(settings.BASE_DIR, 'secret')
    with open(os.path.join(secret_dir, 'img_api_key.txt'), 'r') as file:
        api_key = file.read().strip()
    with open(os.path.join(secret_dir, 'img_secret_key.txt'), 'r') as file:
        api_secret = file.read().strip()
    return api_key, api_secret

def clean_text(text):
    # 정규 표현식을 사용하여 특수문자와 불필요한 공백 제거
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def analyze_text_and_images(diary, user_persona):
    # 제목과 내용을 형태소 분석하여 UserPersona에 추가
    title_words = okt.morphs(clean_text(diary.title))
    content_words = okt.morphs(clean_text(diary.diary))
    all_words = title_words + content_words
    print(all_words)
    word_counts = Counter(all_words)

    for word, count in word_counts.items():
        user_persona_obj, created = UserPersona.objects.get_or_create(user_info_persona=user_persona, word=word)
        if not created:
            count += user_persona_obj.count
        user_persona_obj.count = count
        user_persona_obj.save()

    # 이미지가 존재할 경우 이미지로부터 단어 추출 후 UserPersona에 추가
    # for i in range(1, 11):
    #     picture_field = getattr(diary, f'picture{i}')
    #     if picture_field:
    #         image_tags = tag_image_with_imagga(picture_field.path)
    #         description = process_image_tags_with_gpt(image_tags)
    #         description_words = okt.morphs(clean_text(description))
    #         description_word_counts = Counter(description_words)
    #
    #         for word, count in description_word_counts.items():
    #             user_persona_obj, created = UserPersona.objects.get_or_create(user_info_persona=user_persona, word=word)
    #             if not created:
    #                 count += user_persona_obj.count
    #             user_persona_obj.count = count
    #             user_persona_obj.save()

def tag_image_with_imagga(image_path):
    print("이미지 태그 시작")
    api_key, api_secret = get_api_keys()

    url = "https://api.imagga.com/v2/tags"

    with open(image_path, 'rb') as image_file:
        response = requests.post(
            url,
            auth=(api_key, api_secret),
            files={'image': image_file}
        )

    response_data = response.json()

    if response.status_code == 200:
        tags = [tag['tag']['en'] for tag in response_data['result']['tags']]
        return tags
    else:
        print(f"Error: {response_data['status']['text']}")
        return []

def process_image_tags_with_gpt(tags):
    secret_dir = os.path.join(settings.BASE_DIR, 'secret')
    with open(os.path.join(secret_dir, 'API_KEY.txt'), 'r') as file:
        key = file.read().strip()

    prompt = f"다음 태그들을 사용하여 이미지를 설명해줘: {', '.join(tags)}"

    client = OpenAI(api_key=key)
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    description = ""
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            description += chunk.choices[0].delta.content.strip()

    print(f"설명 : {description}")
    return description

# 유저 프리미엄 유저인지, 아닌지
def maintain_user_persona_count(user_info_persona):
    user = user_info_persona.user
    if hasattr(user, 'model') and user.model:  # user.model이 존재하는지 확인
        max_count = 10000
    else:
        max_count = 1500

    persona_count = UserPersona.objects.filter(user_info_persona=user_info_persona).count()
    if persona_count > max_count:
        over_count = persona_count - max_count
        persona_to_delete = UserPersona.objects.filter(user_info_persona=user_info_persona).order_by('?')[:over_count]
        persona_to_delete.delete()
