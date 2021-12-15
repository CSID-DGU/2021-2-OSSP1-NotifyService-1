from gensim.models.word2vec import Word2Vec
from konlpy.tag import Kkma
import tqdm
# 카카오톡 발송 관련
import json
import time
import datetime
import uuid
import hmac
import hashlib
import requests
# DB 연결
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from models import User, Keywords
from pprint import pprint

#### new_crawl_list :
new_crawl_list = ['이과대학 수학과', '제16회 이과대학 재학생 연구프로젝트 경진대회 개최 안내', 'https://math.dongguk.edu/?page_id=260/?page_id=260&pageid=1&uid=60&mod=document', '20211127193112']

# DB 연결
engine = create_engine(
    'postgresql://jrbysnbvqyvmie:4a2d878446a2864c6c7b9b16b965f58756035fea520bf6f682db34769ff6d053@ec2-44-198-236-169.compute-1.amazonaws.com:5432/db0sh1er7k2vqh')
Session = sessionmaker()
Session.configure(bind=engine)

# 카카오톡 발송 관련
# apiKey, apiSecret 입력 필수
apiKey = 'NCSZN8XOQVWIDIJ8'
apiSecret = 'HXNZFVR4RPFRPHDW2FAP2KIRU1ICY1MY'
protocol = 'https'
domain = 'api.solapi.com'
prefix = ''


# 불용어 처리 & 토큰화
def tokenized(new_crawl_list):
    stop_words = []
    with open('stopword.txt', encoding='utf-8') as f:
        for i in f:
            stop_words.append(i.strip())

    kkma = Kkma()

    tokenized_sentence = kkma.nouns(new_crawl_list[1])
    tokenized_data = [word for word in tokenized_sentence if not word in stop_words]  # 불용어 제거
    tokenized_data.append(new_crawl_list[2])
    return tokenized_data
# 형식
# ['대관', '제한', 'https://www.dongguk.edu/mbs/kr/jsp/board/view.jsp?spage=1&boardId=3646&boardSeq=26741219&id=kr_010802000000&column=&search=&categoryDepth=&mcategoryId=0']

# 유사단어 찾기
def findSimilar(new_crawl_list):
    similar_words = []
    tokenized_data = tokenized(new_crawl_list)
    model = Word2Vec.load('model/Kkma_dataset.model')
    link = tokenized_data[-1] # 링크
    for j in range(len(tokenized_data) - 1):  # 링크 뺴고
        try:
            a_synonym = model.wv.most_similar(tokenized_data[j])
            for k in a_synonym:
                if len(k[0]) == 1:
                    a_synonym.remove(k)
            a_synonym = a_synonym[:5]  # 유사단어 5개 [(유사단어1, 확률), ... , (유사단어5, 확률)]

            # 유사단어만 추출
            for i in a_synonym:
                similar_words.append(i[0])

        except KeyError:
            pass

    similar_words = list(set(similar_words))
    similar_words.append(link)
    # print(" >> 유사단어 추출 완료 : " + str(len(similar_words)) + " 개, " + str(similar_words))
    return similar_words
# 형식
# ['경연', '이과', '경진대회', '개별', '경연대회', '경진', '법과', '연구프로젝트', '예술대학', '교수님', '개최', '포트', '실적', '이과대학', '활용', '아이디어', '개별연구', '공과대학', '폴리오', '비교법연구등', '제권', '설계프로젝트', '프로젝트', '대회', '법과대학', '미래융합대학', '어드벤처디자인경진대회', '학술대회', 'https://math.dongguk.edu/?page_id=260/?page_id=260&pageid=1&uid=60&mod=document']

# 카카오톡 발송 관련
# def send_kakao(new_crawl_list):
def send_kakao():
    session = Session()  # DB 세션 생성
    # words_list = findSimilar(new_crawl_list)  # 유사 단어 리턴받을 리스트
    words_list = ['경연', '이과', '경진대회', '개별', '경연대회', '경진', '법과', '연구프로젝트', '예술대학', '교수님', '개최', '포트', '실적', '이과대학', '활용', '아이디어', '개별연구', '공과대학', '폴리오', '비교법연구등', '제권', '설계프로젝트', '프로젝트', '대회', '법과대학', '미래융합대학', '어드벤처디자인경진대회', '학술대회', 'https://math.dongguk.edu/?page_id=260/?page_id=260&pageid=1&uid=60&mod=document']
    link = words_list[-1]  # 현재 크롤링한 데이터의 URL 주소
    words_list.remove(link)  # 리스트에서 링크 제거
    users_id = []  # DB에서 조회할 사용자의 id
    temp_phone = []  # DB에서 조회할 사용자의 핸드폰번호
    users_phone = []  # DB에서 조회할 사용자의 핸드폰번호

    for word in words_list:
        user = session.query(Keywords.id, User.department).filter_by(key= word)
        join_user = user.join(User, Keywords.id == User.id).all()
        if join_user:
            users_id.extend(list(join_user))
    users_id = list(set(users_id))  # 중복 데이터 제거

    for key in users_id:
        phone = session.query(User.phone).filter_by(id=key[0]).all()
        if phone:
            temp_phone.extend(list(phone))
    temp_phone = list(set(temp_phone))  # 중복 데이터 제거

    for phone in temp_phone:
        test = phone[0]
        users_phone.append(test)

    if len(users_phone) > 0:
        print("카카오톡 발송 대상 있음 (" + str(len(users_phone)) + "명)")
        # data = {
        #     'messages': [
        #         {
        #             'to': users_phone,
        #             'from': '01074477163',
        #             'text': '등록하신 키워드와 연관있는 공지가 등록되었습니다. 링크를 클릭하시면 해당 공지로 연결됩니다 :)',
        #             'kakaoOptions': {
        #                 'pfId': 'KA01PF211130075802780LDxZiwnOy9H'
        #                 , 'buttons': [
        #                     {
        #                         'buttonType': 'WL',  # 웹링크
        #                         'buttonName': '공지사항 보러가기',
        #                         'linkMo': link,
        #                         'linkPc': link
        #                     }
        #                 ]
        #             }
        #         }
        #     ]
        # }
        # res = sendMany(data)
        # print(json.dumps(res.json(), indent=2, ensure_ascii=False))
    else:
        print("카카오톡 발송 대상 없음")

    return None

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

# pprint(send_kakao())
send_kakao()
