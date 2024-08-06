import os
import requests
from PIL import Image
from .models import Picture, UserPersona, City
from geopy.geocoders import Nominatim
from openai import OpenAI
from django.conf import settings
from PIL.ExifTags import TAGS, GPSTAGS
from konlpy.tag import Okt

okt = Okt()

def get_api_key(file_name):
    secret_dir = os.path.join(settings.BASE_DIR, 'secret')
    with open(os.path.join(secret_dir, file_name), 'r') as file:
        return file.read().strip()

def get_decimal_from_dms(dms, ref):
    degrees = dms[0]
    minutes = dms[1]
    seconds = dms[2]

    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
    if ref in ['S', 'W']:
        decimal = -decimal
    return decimal

def get_location_from_image(image_path):
    try:
        img = Image.open(image_path)
        info = img._getexif()
        if not info:
            print("No EXIF metadata found")
            return None

        exif = {TAGS.get(tag): value for tag, value in info.items() if tag in TAGS}
        gps_info = exif.get('GPSInfo')
        if not gps_info:
            print("No GPS data found")
            return None

        gps_data = {GPSTAGS.get(tag): value for tag, value in gps_info.items() if tag in GPSTAGS}
        lat_data = gps_data.get('GPSLatitude')
        lat_ref = gps_data.get('GPSLatitudeRef')
        lon_data = gps_data.get('GPSLongitude')
        lon_ref = gps_data.get('GPSLongitudeRef')

        if not lat_data or not lon_data or not lat_ref or not lon_ref:
            print("Incomplete GPS data")
            return None

        lat = get_decimal_from_dms(lat_data, lat_ref)
        lon = get_decimal_from_dms(lon_data, lon_ref)

        print(f"Latitude: {lat}, Longitude: {lon}")

        geolocator = Nominatim(user_agent="geoapiExercises")
        location = geolocator.reverse((lat, lon), language='en')
        if location:
            print(f"Extracted location: {location.address}")
            return location.address
        else:
            print("Location could not be found")
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    return None


# ChatGPT를 사용하여 도시 MBTI를 가져오는 함수
def get_city_mbti(city):
    key = get_api_key('API_KEY.txt')

    prompt = f"""
    {city}의 도시 MBTI가 무엇인지 알려줘.

    INFP, INFJ, INTP, INTJ, ISFP, ISFJ, ISTP, ISTJ, ENFP, ENFJ, ENTP, ENTJ, ESFP, ESFJ, ESTP, ESTJ
    이렇게 16개 중에 하나로 나오겠지?
    도시 mbti 구별법은 
    1. 경제 기반 인구 에너지 원천 : 외부인을 적극적으로 받아들여 에너지를 키울것인가(E) vs 내부 인구를 안정적으로 지키며 나아갈 것인가(I)
    2. 입지적 특성 공간적 환경 : 자연적으로 주어진 것을 적극 활용하여 성장할 것인가(N) vs 기존에 공급된 도시적 자원을 활성화할 것인가(S)
    3. 지역 가치 성장 가치 : 선대의 유산을 적극 활용하여 지역적 차별성을 만들 것인가(T) vs 새로운 경제적 엔진을 만들어 지역 차별화를 만들것인가(F)
    4. 전개 방식 지역 특수성 : 한시적 에너지 집중형으로 소프트웨어 중심의 투입이 필요한가(P) vs 상시적이고 계획적이며 하드웨어 중심의 확대가 필요한가(J)
    로 해당 지역을 잘 판단해서 
    이 16개중에 하나만 설명해주면 돼. 부연설명은 필요없어"""

    client = OpenAI(api_key=key)
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    mbti = ""
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            mbti += chunk.choices[0].delta.content.strip()


    print(f"{city} : {mbti}")

    mbti_dict = {}
    tmp = ["INFP", "INFJ", "INTP", "INTJ", "ISFP", "ISFJ", "ISTP", "ISTJ", "INFP", "INFJ", "ENTP", "ENTJ", "ESFP",
           "ESFJ", "ESTP", "ESTJ"]

    for i in tmp:
        if i in mbti:
            mbti_dict[i[0]] = 3
            mbti_dict[i[1]] = 3
            mbti_dict[i[2]] = 3
            mbti_dict[i[3]] = 3

    return mbti_dict


def get_api_keys():
    api_key = get_api_key('img_api_key.txt')
    api_secret = get_api_key('img_secret_key.txt')
    return api_key, api_secret

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
    key = get_api_key('API_KEY.txt')

    prompt = f"다음 태그들을 사용하여 이미지를 설명해줘: {', '.join(tags)}"

    client = OpenAI(api_key=key)
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    description= ""
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            description += chunk.choices[0].delta.content.strip()

    return description

def picture_logic(user_info_persona):
    # Picture 모델에서 이미지 로드
    pictures = Picture.objects.filter(user_info_persona=user_info_persona)
    images = []

    for picture in pictures:
        for i in range(1, 16):
            picture_path = getattr(picture, f'picture{i}')
            if picture_path:
                images.append(picture_path.path)

    analysis_results = []
    city_mbtis = []

    for image_path in images:
        location = get_location_from_image(image_path)
        if location:
            city_mbti = get_city_mbti(location)
            city_mbtis.append(city_mbti)
            print(f"{location}도시 mbti 추가")

        # Imagga API를 사용하여 이미지 태그 생성
        tags = tag_image_with_imagga(image_path)
        print(f"이미지 태그: {tags}")

        # GPT를 사용하여 태그로부터 이미지 설명 생성
        description = process_image_tags_with_gpt(tags)
        print(f"사진 설명: {description}")
        analysis_results.append(description)

    # 종합된 도시 MBTI 계산
    mbti_counts = {'E': 0, 'I': 0, 'N': 0, 'S': 0, 'T': 0, 'F': 0, 'J': 0, 'P': 0}
    for city_mbti in city_mbtis:
        if city_mbti:
            for key, value in city_mbti.items():
                if key in mbti_counts:
                    mbti_counts[key] += value

    print("사진 종합 mbti 계산 완료")

    # 분석 결과를 UserPersona 모델에 저장
    words = []
    try:
        print("형태소 분석 시작")
        words = [word.strip() for result in analysis_results for word in okt.morphs(result)]  # 형태소 분석 결과에서 추출한 단어들
        print(words)
        for word in words:
            UserPersona.objects.update_or_create(user_info_persona=user_info_persona, word=word, defaults={'count': 1})
    except Exception as e:
        print(f"An error occurred while processing with okt: {e}")

    maintain_user_persona_count(user_info_persona)

    # 예시 반환 값
    return mbti_counts

#유저 프리미엄 유저인지, 아닌지
def maintain_user_persona_count(user_info_persona):
    user = user_info_persona.user
    if user.model:
        max_count = 10000
    else:
        max_count = 1500

    persona_count = UserPersona.objects.filter(user_info_persona=user_info_persona).count()
    if persona_count > max_count:
        over_count = persona_count - max_count
        persona_to_delete = UserPersona.objects.filter(user_info_persona=user_info_persona).order_by('?')[:over_count]
        persona_to_delete.delete()
