import requests
import json

url = 'https://kauth.kakao.com/oauth/token'
rest_api_key = '1c59531be6e6ce9c2edbd4a719e2b919'
redirect_uri = 'https://example.com/oauth'
authorize_code = 'fbWAWec0Ul-zU66vvIGBh5S4Vd-N5kSel4BGZRCtESCCtfa7wViD1HaJqtf-NV1cAtp1GQorDNQAAAF9b17w4Q'

data = {
    'grant_type': 'authorization_code',
    'client_id': rest_api_key,
    'redirect_uri': redirect_uri,
    'code': authorize_code,
    }

response = requests.post(url, data=data)
tokens = response.json()
print(tokens)

with open("kakao_code.json", "w") as fp:
    json.dump(tokens, fp)

# -----------------------------------------------------------------------------------


with open("kakao_code.json", "r") as fp:
    tokens = json.load(fp)

url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

headers = {
    "Authorization": "Bearer " + tokens["access_token"]
}

data={
    "template_object": json.dumps({
        "object_type": "text",
        "text": "Hello, world!",
        "link": {
            "web_url": "www.naver.com"
        }
    })
}

response = requests.post(url, headers=headers, data=data)
response.status_code

# -----------------------------------------------------------------------------------

#
with open("kakao_code.json", "r") as fp:
    tokens = json.load(fp)

friend_url = "https://kapi.kakao.com/v1/api/talk/friends"

headers={"Authorization" : "Bearer " + tokens["access_token"]}

result = json.loads(requests.get(friend_url, headers=headers).text)

print(type(result))
print("=============================================")
print(result)
print("=============================================")
friends_list = result.get("elements")
print(friends_list)
# print(type(friends_list))
print("=============================================")
print(friends_list[0].get("uuid"))
friend_id = friends_list[0].get("uuid")
print(friend_id)

send_url= "https://kapi.kakao.com/v1/api/talk/friends/message/default/send"

data={
    'receiver_uuids': '["{}"]'.format(friend_id),
    "template_object": json.dumps({
        "object_type": "text",
        "text": "성공입니다!",
        "link": {
            "web_url":"www.daum.net",
            "web_url":"www.naver.com"
        },
        "button_title": "바로 확인"
    })
}

response = requests.post(send_url, headers=headers, data=data)
response.status_code
