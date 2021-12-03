from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import update
from models import User, Keywords, Crawl

import pandas as pd
import re
from gensim.models.word2vec import Word2Vec
from konlpy.tag import Kkma
import tqdm

import time
import schedule


engine = create_engine('postgresql://jrbysnbvqyvmie:4a2d878446a2864c6c7b9b16b965f58756035fea520bf6f682db34769ff6d053@ec2-44-198-236-169.compute-1.amazonaws.com:5432/db0sh1er7k2vqh')
Session = sessionmaker()
Session.configure(bind=engine)

# DB에서 데이터 가져오기
def getDB():
    session = Session()
    db_data=session.query(Crawl.title).all()
    session.close()
    return db_data


# 불용어 & 토큰화
def tokenizeData():
    db_data = getDB() # 데이터 가져오기
    db_data=pd.DataFrame(db_data,columns = ['제목'])
    db_data['제목']= db_data['제목'].str.replace("[^ㄱ-ㅎㅏ-ㅣ가-힣 ]","")#데이터 정규표현식 -> 특수문자 제거

    # 불용어 파일 불러오기
    stop_words= []
    with open('stopword.txt', encoding='utf-8') as f:
        for i in f:
            stop_words.append(i.strip())

    # okt = Okt()
    kkma = Kkma()

    tokenized_data = []
    for sentence in tqdm.tqdm(db_data['제목']):
        tokenized_sentence = kkma.nouns(sentence) # 토큰화 -> noun으로 하는 건 어떰? --> 형태소 말고 명사로 단위로 쪼갬
        stopwords_removed_sentence = [word for word in tokenized_sentence if not word in stop_words] # 불용어 제거
        tokenized_data.append(stopwords_removed_sentence)
    return tokenized_data

def setModel():
    tokenized_data = tokenizeData()
    global model
    model = Word2Vec(sentences = tokenized_data, sg=1)# 학습 -> 모든것이 default로 되어있으므로 값 정해야 함 !
    # 모델 저장
    model.save('model/new_Kkma_dataset.model')
    return model
    
def findLink(set, keyword): 
    session = Session()
    model = Word2Vec.load(set)
    similar = model.wv.most_similar(keyword)
    for i in similar:
        links=session.query(Crawl.link).filter(Crawl.title.like('%'+i[0]+'%' or '%'+keyword+'%')).all()
    session.close()
    return links

# def findSimilar(set,keyword):
#     model=Word2Vec.load(set)
#     most_similar=model.wv.most_similar(keyword)
#     print(set+"을 사용한 "+keyword+" 와(과) 관련된 유사도 : ")
#     print(most_similar) 

def findVocab(set):
    model=Word2Vec.load(set)
    word_vectors=model.wv
    vocabs=word_vectors.vocab.keys()# 사전
    remove_key=[]
    # print("제거전")
    # print(vocabs)
    for i in vocabs:
        if len(i)==1:
            remove_key.append(i)
    for key in list(vocabs) :
        if key in remove_key :
            del word_vectors.vocab[key]
    # print("제거후")
    vocabs=word_vectors.vocab.keys()
    # print(vocabs)   
    return vocabs   
  
# findVocab('model/Kkma_dataset.model')

setModel()

schedule.every().monday.at("10:00").do(setModel) #매주 월요일 10시에 실행

while True:
    schedule.run_pending()
    time.sleep(1)


# findSynonym()
# print("----------------기존 방법")
# findLink('model/Okt_dataset.model', '편입학')
# print("----------------새로운 방법")
# findLink('model/Kkma_dataset.model', '편입학')
# print("CBOW방식으로 했을 때 학습 결과 : ")
# print(findsimilar('CBOW dataset.model','학기'))# 유사도
# print("Skip-gram 방식으로 했을 때 학습 결과 : ")
# print(findsimilar('Skip_gram dataset.model','학기'))# 유사도
