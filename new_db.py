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
from konlpy.tag import Kkma
import tqdm
import time

new_db = [["일반공지", "2021학년도 근로장학생 [추가 모집]안내", "https://www.dongguk.edu/mbs/kr/jsp/board/view.jsp?spage=1&boardId=3646&boardSeq=26741193&id=kr_010802000000&column=&search=&categoryDepth=&mcategoryId=0"], 
["일반공지", "2021학년도 [추가 모집]안내", "https://www.dongguk.edu/mbs/kr/jsp/board/view.jsp?spage=1&boardId=3646&boardSeq=26741193&id=kr_010802000000&column=&search=&categoryDepth=&mcategoryId=0"]]
# ["일반공지", "2021학년도 동계방학 메이커스페이스MARU 근로장학생 [추가 모집]안내", "https://www.dongguk.edu/mbs/kr/jsp/board/view.jsp?spage=1&boardId=3646&boardSeq=26741193&id=kr_010802000000&column=&search=&categoryDepth=&mcategoryId=0"]]


# 불용어 처리 & 토큰화
def tokenized():
    stop_words= []
    with open('stopword.txt', encoding='utf-8') as f:
        for i in f:
            stop_words.append(i.strip())

    kkma = Kkma()

    tokenized_data = []
    for sentence in tqdm.tqdm(new_db):
        tokenized_sentence = kkma.nouns(sentence[1])
        stopwords_removed_sentence = [word for word in tokenized_sentence if not word in stop_words] # 불용어 제거
        tokenized_data.append(stopwords_removed_sentence)

    return tokenized_data


def findSimilar():
    most_similar = []
    tokenized_data = tokenized()
    model=Word2Vec.load('model/Kkma_dataset.model')
    for i in tokenized_data:
        for j in i :
            try :
                most_similar.append(model.wv.most_similar(j))
            except KeyError:
                pass
    return most_similar



print(findSimilar())