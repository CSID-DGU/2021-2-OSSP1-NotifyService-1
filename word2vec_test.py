import pandas as pd
import re
from nltk.tokenize import word_tokenize, sent_tokenize
from gensim.models.word2vec import Word2Vec
from konlpy.tag import Okt
import tqdm

train_data = pd.read_excel('203820result.xlsx')#자신의 파일 이름으로 바꿀것

print(train_data.isnull().values.any())

train_data['제목'] = train_data['제목'].str.replace("[^ㄱ-ㅎㅏ-ㅣ가-힣 ]","")

stopwords = ['시리즈','안내','참가자','모집','과정','을','활용','프로그램','년','및','의','가','이','은','들','는','좀','잘','걍','과','도','를','으로','자','에','와','한','하다']

okt = Okt()

tokenized_data = []
for sentence in tqdm.tqdm(train_data['제목']):
    tokenized_sentence = okt.morphs(sentence, stem=True) # 토큰화
    stopwords_removed_sentence = [word for word in tokenized_sentence if not word in stopwords] # 불용어 제거
    tokenized_data.append(stopwords_removed_sentence)

print(tokenized_data)

model = Word2Vec(sentences = tokenized_data)
print(model.wv.vectors.shape)

word_vectors=model.wv
vocabs=word_vectors.vocab.keys()
word_vectors_list=[word_vectors[v] for v in vocabs]

print(vocabs)
print(model.wv.most_similar("사업"))

