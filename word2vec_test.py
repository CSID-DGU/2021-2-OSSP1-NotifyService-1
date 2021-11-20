import pandas as pd
import re
from nltk.tokenize import word_tokenize, sent_tokenize
from gensim.models.word2vec import Word2Vec
from konlpy.tag import Okt
import tqdm

# 파일 불러오기
train_data = pd.read_excel('203820result.xlsx')#엑셀 불러옴
file = train_data.values.tolist() # 리스트로 정리

# print(train_data.isnull().values.any())

train_data['제목']= train_data['제목'].str.replace("[^ㄱ-ㅎㅏ-ㅣ가-힣 ]","")#데이터 표현 정규화 -> 특수문자 제거

# 불용어 처리
stop_words= []
with open('stopword.txt', encoding='utf-8') as f:
    for i in f:
        stop_words.append(i.strip())
# stopwords = ['시리즈','안내','참가자','모집','과정','을','활용','프로그램','년','및','의','가','이','은','들','는','좀','잘','걍','과','도','를','으로','자','에','와','한','하다']


okt = Okt()

tokenized_data = []
for sentence in tqdm.tqdm(train_data['제목']):
    tokenized_sentence = okt.nouns(sentence) # 토큰화 -> noun으로 하는 건 어떰? --> 형태소 말고 명사로 단위로 쪼갬
    # tokenized_sentence = okt.morphs(sentence, stem=True) # 토큰화
    stopwords_removed_sentence = [word for word in tokenized_sentence if not word in stop_words] # 불용어 제거
    tokenized_data.append(stopwords_removed_sentence)

# print(tokenized_data)

model = Word2Vec(sentences = tokenized_data)# 학습 -> 모든것이 default로 되어있으므로 값 정해야 함 !
# print(model.wv.vectors.shape)

word_vectors=model.wv
vocabs=word_vectors.vocab.keys()# 사전
word_vectors_list=[word_vectors[v] for v in vocabs]

# print(vocabs)
similar = model.wv.most_similar("사업")#사업과 가장 유사한 단어 
print(similar)
for elm in similar:
    for i in range(len(tokenized_data)):
        for j in tokenized_data[i]:
            if elm[0] == j:
                print(file[i][3])

