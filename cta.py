import json
import time
import datetime
import uuid
import hmac
import hashlib
import requests

# apiKey, apiSecret 입력 필수
apiKey = 'NCSZN8XOQVWIDIJ8'
apiSecret = 'HXNZFVR4RPFRPHDW2FAP2KIRU1ICY1MY'

# 아래 값은 필요시 수정
protocol = 'https'
domain = 'api.solapi.com'
prefix = ''

def unique_id():
    return str(uuid.uuid1().hex)

def get_iso_datetime():
    utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
    utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
    return datetime.datetime.now().replace(tzinfo=datetime.timezone(offset=utc_offset)).isoformat()

def get_signature(key, msg):
    return hmac.new(key.encode(), msg.encode(), hashlib.sha256).hexdigest()

def get_headers(apiKey, apiSecret):
    date = get_iso_datetime()
    salt = unique_id()
    data = date + salt
    return {
      'Authorization': 'HMAC-SHA256 ApiKey=' + apiKey + ', Date=' + date + ', salt=' + salt + ', signature=' +
                             get_signature(apiSecret, data),
      'Content-Type': 'application/json; charset=utf-8'
    }

def getUrl(path):
  url = '%s://%s' % (protocol, domain)
  if prefix != '':
    url = url + prefix
  url = url + path
  return url

def sendMany(data):
  return requests.post(getUrl('/messages/v4/send-many'), headers=get_headers(apiKey, apiSecret), json=data)

# 한번 요청으로 1만건의 메시지 발송이 가능합니다.
if __name__ == '__main__':
  data = {
    'messages': [
      # 알림톡 발송
      {
        'to': [ '01074477163'], # array 사용으로 동일한 내용을 여러 수신번호에 전송 가능
        'from': '01074477163',
        'text': '카카오톡채널 친구로 추가되어 있어야 친구톡 발송이 가능합니다.',
        'kakaoOptions': {
          'pfId': 'KA01PF200323182344986oTFz9CIabcx'
          # , 'buttons': [
          #   {
          #     'buttonType': 'WL', # 웹링크
          #     'buttonName': '버튼 이름',
          #     'linkMo': 'https://m.example.com',
          #     'linkPc': 'https://example.com'     # 템플릿 등록 시 모바일링크만 입력하였다면 linkPc 값은 입력하시면 안됩니다.
          #   }
          # ]
        }
      }
    ]
  }
  res = sendMany(data)
  print(json.dumps(res.json(), indent=2, ensure_ascii=False))
