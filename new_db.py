from gensim.models.word2vec import Word2Vec
from konlpy.tag import Kkma
import tqdm
from pprint import pprint

#### new_crawl_list :  
new_crawl_list = [['일반공지', '[일반공지] 교내시설 대관 제한 안내', 'https://www.dongguk.edu/mbs/kr/jsp/board/view.jsp?spage=1&boardId=3646&boardSeq=26741219&id=kr_010802000000&column=&search=&categoryDepth=&mcategoryId=0', '2021-12-03 19:47:58.928990'], 
# ['일반공지', '[일반공지] 2021학년도 동계방학 메이커스페이스MARU 근로장학생 [추가...', 'https://www.dongguk.edu/mbs/kr/jsp/board/view.jsp?spage=1&boardId=3646&boardSeq=26741193&id=kr_010802000000&column=&search=&categoryDepth=&mcategoryId=0', '2021-12-03 19:47:59.712425'], 
# ['일반공지', '[일반공지] 2022 에몬스 슬로건 공모전 안내', 'https://www.dongguk.edu/mbs/kr/jsp/board/view.jsp?spage=1&boardId=3646&boardSeq=26741183&id=kr_010802000000&column=&search=&categoryDepth=&mcategoryId=0', '2021-12-03 19:48:00.500311'], 
# ['일반공지', '[일반공지] 인공지능 학습용 데이터 온라인 해커톤 공모전 안내', 'https://www.dongguk.edu/mbs/kr/jsp/board/view.jsp?spage=1&boardId=3646&boardSeq=26741180&id=kr_010802000000&column=&search=&categoryDepth=&mcategoryId=0', '2021-12-03 19:48:01.281635'], 
# ['일반공지', '[일반공지] 2021학년도 2학기 학생증 신규발급 일시중단 안내(2022....', 'https://www.dongguk.edu/mbs/kr/jsp/board/view.jsp?spage=1&boardId=3646&boardSeq=26741159&id=kr_010802000000&column=&search=&categoryDepth=&mcategoryId=0', '2021-12-03 19:48:02.063466'], 
# ['일반공지', '[일반공지] [DUICA]컴활, GTQ, 웹퍼블리셔 자격 특강', 'https://www.dongguk.edu/mbs/kr/jsp/board/view.jsp?spage=1&boardId=3646&boardSeq=26741146&id=kr_010802000000&column=&search=&categoryDepth=&mcategoryId=0', '2021-12-03 19:48:02.849209'], 
# ['일반공지', '[일반공지] [중앙도서관-Making School] 메이커스페이스 MARU...', 'https://www.dongguk.edu/mbs/kr/jsp/board/view.jsp?spage=1&boardId=3646&boardSeq=26741144&id=kr_010802000000&column=&search=&categoryDepth=&mcategoryId=0', '2021-12-03 19:48:03.629960'], 
# ['일반공지', '[일반공지]제1회 일반교양 학생 아이디어 공모전 수상작 발표', 'https://www.dongguk.edu/mbs/kr/jsp/board/view.jsp?spage=1&boardId=3646&boardSeq=26741143&id=kr_010802000000&column=&search=&categoryDepth=&mcategoryId=0', '2021-12-03 19:48:04.408793'], 
# ['일반공지', '[일반공지] [카운슬링센터] 온라인 심리검사 프로그램 안내', 'https://www.dongguk.edu/mbs/kr/jsp/board/view.jsp?spage=1&boardId=3646&boardSeq=26741128&id=kr_010802000000&column=&search=&categoryDepth=&mcategoryId=0','2021-12-03 19:48:05.191510'], 
# ['일반공지', '[일반공지] 2021년 동계 베트남 온라인 해외봉사 단원모집(재안내)', 'https://www.dongguk.edu/mbs/kr/jsp/board/view.jsp?spage=1&boardId=3646&boardSeq=26741116&id=kr_010802000000&column=&search=&categoryDepth=&mcategoryId=0', '2021-12-03 19:48:05.970713'], 
['일반공지','[일반공지] 2021년 동계 필리핀 온라인 해외봉사 단원모집(재안내)', 'https://www.dongguk.edu/mbs/kr/jsp/board/view.jsp?spage=1&boardId=3646&boardSeq=26741115&id=kr_010802000000&column=&search=&categoryDepth=&mcategoryId=0', '2021-12-03 19:48:06.750168']
]

# 불용어 처리 & 토큰화
def tokenized(new_crawl_list):
    stop_words= []
    with open('stopword.txt', encoding='utf-8') as f:
        for i in f:
            stop_words.append(i.strip())

    kkma = Kkma()

    tokenized_data = []
    for sentence in tqdm.tqdm(new_crawl_list):
        tokenized_sentence = kkma.nouns(sentence[1])
        stopwords_removed_sentence = [word for word in tokenized_sentence if not word in stop_words] # 불용어 제거
        stopwords_removed_sentence.append(sentence[2])
        tokenized_data.append(stopwords_removed_sentence)
    return tokenized_data

# 유사단어 찾기
def findSimilar(new_crawl_list):
    synonym = []
    tokenized_data = tokenized(new_crawl_list)
    model=Word2Vec.load('model/Kkma_dataset.model')
    for i in tokenized_data: # [대관, 제한, 링크]
        for j in range(len(i)-1) : # 0, 1
            try :
                a_synonym = model.wv.most_similar(i[j])
                for k in a_synonym:
                    if len(k[0]) == 1:
                        a_synonym.remove(k)
                a_synonym = a_synonym[:5]
                a_synonym.append(i[-1])
                synonym.append(a_synonym)
            except KeyError:
                pass
    return synonym

pprint(findSimilar(new_crawl_list))