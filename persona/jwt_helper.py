import requests
from django.conf import settings


def verify_jwt_and_get_user_id(jwt_token):
    url = settings.AUTH_SERVER_URL  # 인증 서버 URL을 설정
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data.get('travel_user_id')
    else:
        return None
