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
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User, Keywords

#### new_crawl_list :
# new_crawl_list = [['일반공지', '[일반공지] 교내시설 대관 제한 안내', 'https://www.dongguk.edu/mbs/kr/jsp/board/view.jsp?spage=1&boardId=3646&boardSeq=26741219&id=kr_010802000000&column=&search=&categoryDepth=&mcategoryId=0', '2021-12-03 19:47:58.928990'],
# ['일반공지', '[일반공지] 2021학년도 동계방학 메이커스페이스MARU 근로장학생 [추가...', 'https://www.dongguk.edu/mbs/kr/jsp/board/view.jsp?spage=1&boardId=3646&boardSeq=26741193&id=kr_010802000000&column=&search=&categoryDepth=&mcategoryId=0', '2021-12-03 19:47:59.712425'],
# ['일반공지', '[일반공지] 2022 에몬스 슬로건 공모전 안내', 'https://www.dongguk.edu/mbs/kr/jsp/board/view.jsp?spage=1&boardId=3646&boardSeq=26741183&id=kr_010802000000&column=&search=&categoryDepth=&mcategoryId=0', '2021-12-03 19:48:00.500311'],
# ['일반공지', '[일반공지] 인공지능 학습용 데이터 온라인 해커톤 공모전 안내', 'https://www.dongguk.edu/mbs/kr/jsp/board/view.jsp?spage=1&boardId=3646&boardSeq=26741180&id=kr_010802000000&column=&search=&categoryDepth=&mcategoryId=0', '2021-12-03 19:48:01.281635'],
# ['일반공지', '[일반공지] 2021학년도 2학기 학생증 신규발급 일시중단 안내(2022....', 'https://www.dongguk.edu/mbs/kr/jsp/board/view.jsp?spage=1&boardId=3646&boardSeq=26741159&id=kr_010802000000&column=&search=&categoryDepth=&mcategoryId=0', '2021-12-03 19:48:02.063466'],
# ['일반공지', '[일반공지] [DUICA]컴활, GTQ, 웹퍼블리셔 자격 특강', 'https://www.dongguk.edu/mbs/kr/jsp/board/view.jsp?spage=1&boardId=3646&boardSeq=26741146&id=kr_010802000000&column=&search=&categoryDepth=&mcategoryId=0', '2021-12-03 19:48:02.849209'],
# ['일반공지', '[일반공지] [중앙도서관-Making School] 메이커스페이스 MARU...', 'https://www.dongguk.edu/mbs/kr/jsp/board/view.jsp?spage=1&boardId=3646&boardSeq=26741144&id=kr_010802000000&column=&search=&categoryDepth=&mcategoryId=0', '2021-12-03 19:48:03.629960'],
# ['일반공지', '[일반공지]제1회 일반교양 학생 아이디어 공모전 수상작 발표', 'https://www.dongguk.edu/mbs/kr/jsp/board/view.jsp?spage=1&boardId=3646&boardSeq=26741143&id=kr_010802000000&column=&search=&categoryDepth=&mcategoryId=0', '2021-12-03 19:48:04.408793'],
# ['일반공지', '[일반공지] [카운슬링센터] 온라인 심리검사 프로그램 안내', 'https://www.dongguk.edu/mbs/kr/jsp/board/view.jsp?spage=1&boardId=3646&boardSeq=26741128&id=kr_010802000000&column=&search=&categoryDepth=&mcategoryId=0','2021-12-03 19:48:05.191510'],
# ['일반공지', '[일반공지] 2021년 동계 베트남 온라인 해외봉사 단원모집(재안내)', 'https://www.dongguk.edu/mbs/kr/jsp/board/view.jsp?spage=1&boardId=3646&boardSeq=26741116&id=kr_010802000000&column=&search=&categoryDepth=&mcategoryId=0', '2021-12-03 19:48:05.970713'],
# ['일반공지','[일반공지] 2021년 동계 필리핀 온라인 해외봉사 단원모집(재안내)', 'https://www.dongguk.edu/mbs/kr/jsp/board/view.jsp?spage=1&boardId=3646&boardSeq=26741115&id=kr_010802000000&column=&search=&categoryDepth=&mcategoryId=0', '2021-12-03 19:48:06.750168']
# ]

# DB 연결
engine = create_engine('postgresql://jrbysnbvqyvmie:4a2d878446a2864c6c7b9b16b965f58756035fea520bf6f682db34769ff6d053@ec2-44-198-236-169.compute-1.amazonaws.com:5432/db0sh1er7k2vqh')
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

    tokenized_data = []
    for sentence in tqdm.tqdm(new_crawl_list):
        tokenized_sentence = kkma.nouns(sentence[1])
        stopwords_removed_sentence = [word for word in tokenized_sentence if not word in stop_words]  # 불용어 제거
        stopwords_removed_sentence.append(sentence[2])
        tokenized_data.append(stopwords_removed_sentence)
    return tokenized_data


# 유사단어 찾기
def findSimilar(new_crawl_list):
    synonym = []
    similar_words = []
    link = None
    tokenized_data = tokenized(new_crawl_list)
    model = Word2Vec.load('model/Kkma_dataset.model')
    for i in tokenized_data:  # [대관, 제한, 링크]
        link = i[-1]
        for j in range(len(i) - 1):  # 0, 1
            try:
                a_synonym = model.wv.most_similar(i[j])
                for k in a_synonym:
                    if len(k[0]) == 1:
                        a_synonym.remove(k)
                a_synonym = a_synonym[:5]  # 유사단어 5개 [(유사단어1, 확률), ... , (유사단어5, 확률)]
                a_synonym.append(i[-1])  # 링크
                synonym.append(a_synonym)

                # 유사단어만 추출
                if i[j] != i[-1]:
                    similar_words.append(i[j])

                for h in a_synonym[:5]:
                    similar_words.append(h[0])

            except KeyError:
                pass

    similar_words = list(set(similar_words))
    similar_words.append(link)
    print(" >> 유사단어 추출 완료 : " + str(len(similar_words)) + " 개, " + str(similar_words))
    return similar_words


# 카카오톡 발송 관련
def send_kakao(new_crawl_list):
    session = Session()                             # DB 세션 생성
    words_list = findSimilar(new_crawl_list)        # 유사 단어 리턴받을 리스트
    link = words_list[-1]                           # 현재 크롤링한 데이터의 URL 주소
    words_list.remove(link)                         # 리스트에서 링크 제거
    users_id = []                                   # DB에서 조회할 사용자의 id
    temp_phone = []                                 # DB에서 조회할 사용자의 핸드폰번호
    users_phone = []                                # DB에서 조회할 사용자의 핸드폰번호

    for word in words_list:
        user = session.query(Keywords.id).filter_by(key=word).all()
        if user:
            users_id.extend(list(user))
    users_id = list(set(users_id))                  # 중복 데이터 제거

    for key in users_id:
        phone = session.query(User.phone).filter_by(id=key[0]).all()
        if phone:
            temp_phone.extend(list(phone))
    temp_phone = list(set(temp_phone))              # 중복 데이터 제거

    for phone in temp_phone:
        test = phone[0]
        users_phone.append(test)
        
    if len(users_phone) > 0:
        print("카카오톡 발송 대상 있음 (" + str(len(users_phone)) + "명")
        data = {
            'messages': [
                {
                    'to': users_phone,
                    'from': '01074477163',
                    'text': '등록하신 키워드와 연관있는 공지가 등록되었습니다. 링크를 클릭하시면 해당 공지로 연결됩니다 :)',
                    'kakaoOptions': {
                        'pfId': 'KA01PF211130075802780LDxZiwnOy9H'
                        , 'buttons': [
                            {
                                'buttonType': 'WL',  # 웹링크
                                'buttonName': '공지사항 보러가기',
                                'linkMo': link,
                                'linkPc': link
                            }
                        ]
                    }
                }
            ]
        }
        res = sendMany(data)
        print(json.dumps(res.json(), indent=2, ensure_ascii=False))
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


# 한번 요청으로 1만건의 메시지 발송이 가능합니다.
if __name__ == '__main__':
    data = {
        'messages': [
            # 알림톡 발송
            {
                'to': ['01074477163'],  # array 사용으로 동일한 내용을 여러 수신번호에 전송 가능
                'from': '01074477163',
                'text': '카카오톡채널 테스트 지원❤',
                'kakaoOptions': {
                    'pfId': 'KA01PF211130075802780LDxZiwnOy9H'
                    , 'buttons': [
                        {
                            'buttonType': 'WL',  # 웹링크
                            'buttonName': '공지사항 보러가기',
                            'linkMo': 'https://www.dongguk.edu/mbs/kr/jsp/board/view.jsp?spage=1&boardId=3646&boardSeq=26740812&id=kr_010802000000&column=&search=&categoryDepth=&mcategoryId=0',
                            'linkPc': 'https://www.dongguk.edu/mbs/kr/jsp/board/view.jsp?spage=1&boardId=3646&boardSeq=26740812&id=kr_010802000000&column=&search=&categoryDepth=&mcategoryId=0'
                            # 템플릿 등록 시 모바일링크만 입력하였다면 linkPc 값은 입력하시면 안됩니다.
                        }
                    ]
                }
            }
        ]
    }
    res = sendMany(data)
    print(json.dumps(res.json(), indent=2, ensure_ascii=False))