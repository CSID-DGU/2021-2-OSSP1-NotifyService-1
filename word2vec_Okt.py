from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import update
from models import User, Keywords, Crawl

import pandas as pd
import re
from nltk.tokenize import word_tokenize, sent_tokenize
from gensim.models.word2vec import Word2Vec
from konlpy.tag import Okt
import tqdm

import time
import schedule


engine = create_engine('postgresql://jrbysnbvqyvmie:4a2d878446a2864c6c7b9b16b965f58756035fea520bf6f682db34769ff6d053@ec2-44-198-236-169.compute-1.amazonaws.com:5432/db0sh1er7k2vqh')
Session = sessionmaker()
Session.configure(bind=engine)

def findSynonym():
    session = Session()
    train_data=session.query(Crawl.title).all()
    train_data=pd.DataFrame(train_data,columns = ['제목'])
    train_data['제목']= train_data['제목'].str.replace("[^ㄱ-ㅎㅏ-ㅣ가-힣 ]","")#데이터 정규표현식 -> 특수문자 제거

    # 불용어 처리
    stop_words= []
    with open('stopword.txt', encoding='utf-8') as f:
        for i in f:
            stop_words.append(i.strip())

    okt = Okt()

    tokenized_data = []
    for sentence in tqdm.tqdm(train_data['제목']):
        tokenized_sentence = okt.nouns(sentence) # 토큰화 -> noun으로 하는 건 어떰? --> 형태소 말고 명사로 단위로 쪼갬
        stopwords_removed_sentence = [word for word in tokenized_sentence if not word in stop_words] # 불용어 제거
        tokenized_data.append(stopwords_removed_sentence)

    global model
    model = Word2Vec(sentences = tokenized_data, sg=0)# 학습 -> 모든것이 default로 되어있으므로 값 정해야 함 !
        # print(model.wv.vectors.shape)
    # 모델 저장
    model.save('model/CBOW dataset.model')

    word_vectors=model.wv
    vocabs=word_vectors.vocab.keys()# 사전
    remove_key=[]
    for i in vocabs:
        if len(i)==1:
            remove_key.append(i)
    for key in list(vocabs) : ## list와 keys()를 꼭 써야함.
        if key in remove_key :
            del word_vectors.vocab[key]
    vocabs=word_vectors.vocab.keys()
    word_vectors_list=[word_vectors[v] for v in vocabs]
    session.close()
    #return model
    
def findLink(set, keyword): # 학습결과를 model로 저장함
    session = Session()
    model = Word2Vec.load(set)
    similar = model.wv.most_similar(keyword)#사업과 가장 유사한 단어 
    for i in similar:
        train_data=session.query(Crawl.link).filter(Crawl.title.like('%'+i[0]+'%' or '%'+keyword+'%')).all()
        print(train_data)
    session.close()

def findsimilar(set,keyword):
    model=Word2Vec.load(set)
    most_similar=model.wv.most_similar(keyword)
    print(set+"을 사용한 "+keyword+" 와(과) 관련된 유사도 : ")
    print(most_similar) 

def findvocab(set):
    model=Word2Vec.load(set)
    
    word_vectors=model.wv
    vocabs=word_vectors.vocab.keys()# 사전
    remove_key=[]
    print("제거전")
    print(vocabs)
    for i in vocabs:
        if len(i)==1:
            remove_key.append(i)
    for key in list(vocabs) : ## list와 keys()를 꼭 써야함.
        if key in remove_key :
            del word_vectors.vocab[key]
    print("제거후")
    vocabs=word_vectors.vocab.keys()
    print(vocabs)    

schedule.every().monday.at("10:00").do(findSynonym) #매주 월요일 10시에 실행

while True:
    schedule.run_pending()
    time.sleep(1)

#findLink('dataset.model', '장학')
#findsimilar('CBOW dataset.model','전과')# 유사도
#findsimilar('Skip_gram dataset.model','전과')# 유사도
findvocab('model/CBOW dataset.model')
