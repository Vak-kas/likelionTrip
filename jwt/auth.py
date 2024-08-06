import requests

def verify_jwt(url, cookie):
    headers = {
        'Cookie': cookie
    }

    url = url + "travel-user/reading"

    try:
        print("보내요")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        print(f"jwt검증 : {response}")
        # print(response.json())

        if response.status_code == 200:
            new_cookies = response.headers.get('Set-Cookie')
            # print(f'cookie: {new_cookies}, data: {response.json()}')  # assuming the response data is in JSON format")
            if new_cookies:
                return {
                    'cookie': new_cookies,
                    'data': response.json()  # assuming the response data is in JSON format
                }
            else:
                return {'error': 'Tokens not found in response'}
        else:
            return {'error': f'Unexpected status code: {response.status_code}'}
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}

