from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import update
from models import User, Keywords, Crawl
# 크롤링 관련
import urllib
import chromedriver_autoinstaller
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import threading
import datetime

app = Flask(__name__)
Base = declarative_base()
engine = create_engine(
    'postgresql://jrbysnbvqyvmie:4a2d878446a2864c6c7b9b16b965f58756035fea520bf6f682db34769ff6d053@ec2-44-198-236-169.compute-1.amazonaws.com:5432/db0sh1er7k2vqh')
Session = sessionmaker()
Session.configure(bind=engine)
new_crawl_list = []  # 알림 발송할 신규 크롤링 공지 리스트


@app.route('/')
def index():
    session = Session()
    msg = str(session.query(User.id, User.college, User.department).all())
    session.close()
    return msg


@app.route('/department', methods=['POST'])
def department():
    req = request.get_json()
    session = Session()

    id = req["userRequest"]["user"]["id"]
    college = req["action"]["detailParams"]["college"]["value"]  # json파일 읽기
    department = req["action"]["detailParams"]["department"]["value"]
    answer = str(id) + "\n" + college + "대학\n" + department
    user = session.query(User.id).filter_by(id=id).all();
    if (user == []):
        session.add(User(id=id, college=college, department=department))
        session.commit()
    else:
        conn = engine.connect()
        stmt = update(User).where(User.id == id).values(college=college, department=department)
        conn.execute(stmt)
        conn.close()
    session.close()
    # 답변 설정
    res = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": answer
                    }
                }
            ]
        }
    }
    return jsonify(res)


@app.route('/keywords', methods=['POST'])
def keywords():
    req = request.get_json()
    session = Session()

    id = req["userRequest"]["user"]["id"]
    action = req["action"]["detailParams"]["action"]["value"]
    if (action == "add"):
        keyword = req["action"]["detailParams"]["keyword"]["value"]
        keys = session.query(Keywords.key).filter_by(id=id, key=keyword).all();
        if (keys == []):
            session.add(Keywords(id=id, key=keyword))
            session.commit()
            answer = "(" + keyword + ") 가 등록되었습니다."
        else:
            answer = "이미 등록된 키워드입니다."
    elif (action == "show"):
        keys = session.query(Keywords.key).filter_by(id=id).all();
        answer = str(keys)
    elif (action == "delete"):
        keyword = req["action"]["detailParams"]["keyword"]["value"]
        keys = session.query(Keywords).filter_by(id=id, key=keyword).first();
        if (keys == None):
            answer = "등록되지 않은 키워드입니다."
        else:
            session.delete(keys)
            session.commit()
            answer = "(" + keyword + ") 가 삭제되었습니다."

    session.close()
    res = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": answer
                    }
                }
            ]
        }
    }
    return jsonify(res)


@app.route('/test', methods=['POST'])
def test():
    req = request.get_json()
    answer = str(req)
    res = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": answer
                    }
                }
            ]
        }
    }
    return jsonify(res)


@app.route('/crawl')
def crawl():
    print('======================================')
    print(datetime.datetime.now())
    print('======================================')
    threading.Timer(3600, crawl).start()

    session = Session()  # DB 세션 생성
    options = Options()  # 크롤링 옵션
    options.add_argument('headless')  # headless는 화면이나 페이지 이동을 표시하지 않고 동작하는 모드

    new_crawl_list.clear()  # 알림 발송할 신규 크롤링 공지 리스트 : 새로운 것만 들어가야 하므로, 크롤링 실행 전 초기화
    new_crawl_count = 0  # 신규로 크롤링한 건수 체크

    time.sleep(3)  # 검색 결과가 렌더링 될 때까지 잠시 대기
    curPage = 1  # 현재 페이지
    totalPage = 1  # 크롤링할 전체 페이지수
    site_per = 0  # 한 페이지의 게시글 체크용
    loop_index = 0  # 미융대 게시글 관련

    url_list = [
        [0, 'https://www.dongguk.edu/mbs/kr/jsp/board/list.jsp?boardId=3646&id=kr_010802000000', '일반공지']
        , [0, 'https://www.dongguk.edu/mbs/kr/jsp/board/list.jsp?boardId=3638&id=kr_010801000000', '학사공지']
        , [0, 'https://www.dongguk.edu/mbs/kr/jsp/board/list.jsp?boardId=3654&id=kr_010803000000', '입시공지']
        , [0, 'https://www.dongguk.edu/mbs/kr/jsp/board/list.jsp?boardId=3662&id=kr_010804000000', '장학공지']
        , [0, 'https://www.dongguk.edu/mbs/kr/jsp/board/list.jsp?boardId=9457435&id=kr_010807000000', '국제공지']
        , [0, 'https://www.dongguk.edu/mbs/kr/jsp/board/list.jsp?boardId=11533472&id=kr_010808000000', '학술/행사공지']

        , [1, 'http://bs.dongguk.edu/bbs/board.php?bo_table=bs5_1', '불교학부']
        , [1, 'http://bs.dongguk.edu/bbs/board.php?bo_table=bs5_3', '불교학부']
        , [1, 'http://liberal.dongguk.edu/bbs/board.php?bo_table=lib4_1', '문과대학']
        , [1, 'http://liberal.dongguk.edu/bbs/board.php?bo_table=lib4_3', '문과대학']
        , [1, 'http://science.dongguk.edu/bbs/board.php?bo_table=sci3_1', '이과대학']
        , [1, 'http://science.dongguk.edu/bbs/board.php?bo_table=sci3_2', '이과대학']
        , [1, 'http://law.dongguk.edu/bbs/board.php?bo_table=law2_1', '법과대학']
        , [1, 'http://law.dongguk.edu/bbs/board.php?bo_table=law2_3', '법과대학']
        , [1, 'http://law.dongguk.edu/bbs/board.php?bo_table=law2_7', '법과대학']
        , [1, 'http://social.dongguk.edu/bbs/board.php?bo_table=social3_1', '사회과학대학']
        , [1, 'http://sba.dongguk.edu/bbs/board.php?bo_table=sba4_1', '경영대학']
        , [1, 'http://life.dongguk.edu/bbs/board.php?bo_table=life4_1', '바이오시스템대학']
        , [1, 'http://life.dongguk.edu/bbs/board.php?bo_table=life4_5', '바이오시스템대학']
        , [1, 'http://life.dongguk.edu/bbs/board.php?bo_table=life4_6', '바이오시스템대학']
        , [1, 'http://life.dongguk.edu/bbs/board.php?bo_table=life4_7', '바이오시스템대학']
        , [1, 'http://edu.dongguk.edu/bbs/board.php?bo_table=edu3_1', '사범대학']
        , [1, 'http://historyedu.dongguk.edu/bbs/board.php?bo_table=history6_1', '사범대학 역사교육과']
        , [1, 'http://historyedu.dongguk.edu/bbs/board.php?bo_table=history6_1_2', '사범대학 역사교육과']
        , [1, 'http://historyedu.dongguk.edu/bbs/board.php?bo_table=history6_1_3', '사범대학 역사교육과']
        , [1, 'http://art.dongguk.edu/bbs/board.php?bo_table=art4_1', '예술대학']
        , [1, 'http://pharm.dongguk.edu/bbs/board.php?bo_table=pharm5_7', '약학대학']
        , [1, 'http://pharm.dongguk.edu/bbs/board.php?bo_table=pharm5_1', '약학대학']

        , [2, 'https://kor-cre.dongguk.edu/?page_id=282', '문과대학 국어국문문예창작학부']
        , [2, 'https://english.dongguk.edu/?page_id=250', '문과대학 영어영문학부']
        , [2, 'https://english.dongguk.edu/?page_id=259', '문과대학 영어영문학부']
        , [2, 'https://dj.dongguk.edu/?page_id=203', '문과대학 일본학과']
        , [2, 'https://dj.dongguk.edu/?page_id=225', '문과대학 일본학과']
        , [2, 'https://china.dongguk.edu/?page_id=208', '문과대학 중어중문학과']
        , [2, 'https://sophia.dongguk.edu/?page_id=230', '문과대학 철학과']
        , [2, 'https://history.dongguk.edu/?page_id=505', '문과대학 사학과']
        , [2, 'https://chem.dongguk.edu/?page_id=288', '이과대학 화학과']
        , [2, 'https://stat.dongguk.edu/?page_id=439', '이과대학 통계학과']
        , [2, 'https://stat.dongguk.edu/?page_id=437', '이과대학 통계학과']
        , [2, 'https://math.dongguk.edu/?page_id=260', '이과대학 수학과']
        , [2, 'https://physics.dongguk.edu/?page_id=324', '이과대학 물리반도체과학부']
        , [2, 'https://physics.dongguk.edu/?page_id=326', '이과대학 물리반도체과학부']
        , [2, 'https://politics.dongguk.edu/?page_id=18518', '사회과학대학 정치외교학과']
        , [2, 'https://politics.dongguk.edu/?page_id=18522', '사회과학대학 정치외교학과']
        , [2, 'https://pa.dongguk.edu/?page_id=233', '사회과학대학 행정학과']
        , [2, 'https://nk.dongguk.edu/?page_id=225', '사회과학대학 북한학과']
        , [2, 'https://econ.dongguk.edu/?page_id=262', '사회과학대학 경제학과']
        , [2, 'https://econ.dongguk.edu/?page_id=297', '사회과학대학 경제학과']
        , [2, 'http://itrade.dongguk.edu/?page_id=150', '사회과학대학 국제통상학과']
        , [2, 'https://sociology.dongguk.edu/?page_id=211', '사회과학대학 사회학과']
        , [2, 'https://welfare.dongguk.edu/?page_id=209', '사회과학대학 사회복지학과']
        , [2, 'https://police.dongguk.edu/?page_id=18349', '경찰사법대학 경찰행정학부']
        , [2, 'https://mgt.dongguk.edu/?page_id=18326', '경영대학 경영학과']
        , [2, 'https://acc.dongguk.edu/?page_id=18334', '경영대학 회계학과']
        , [2, 'https://acc.dongguk.edu/?page_id=1087707', '경영대학 회계학과']
        , [2, 'https://acc.dongguk.edu/?page_id=18328', '경영대학 회계학과']
        , [2, 'http://mis.dongguk.edu/?page_id=269', '경영대학 경영정보학과']
        , [2, 'https://bio.dongguk.edu/?page_id=18531', '바이오시스템대학 바이오환경과학과']
        , [2, 'https://lifescience.dongguk.edu/?page_id=150', '바이오시스템대학 생명과학과']
        , [2, 'https://food.dongguk.edu/?page_id=243', '바이오시스템대학 식품생명공학과']
        , [2, 'http://mbt.dongguk.edu/?page_id=241', '바이오시스템대학 의생명공학과']
        , [2, 'https://civil.dongguk.edu/?page_id=269', '공과대학 건설환경공학과']
        , [2, 'https://civil.dongguk.edu/?page_id=271', '공과대학 건설환경공학과']
        , [2, 'https://civil.dongguk.edu/?page_id=273', '공과대학 건설환경공학과']
        , [2, 'https://civil.dongguk.edu/?page_id=277', '공과대학 건설환경공학과']
        , [2, 'https://archi.dongguk.edu/?page_id=18387', '공과대학 건축공학부']
        , [2, 'https://archi.dongguk.edu/?page_id=18394', '공과대학 건축공학부']
        , [2, 'https://mecha.dongguk.edu/?page_id=207', '공과대학 기계로봇에너지공학과']
        , [2, 'https://mecha.dongguk.edu/?page_id=332', '공과대학 기계로봇에너지공학과']
        , [2, 'https://me.dongguk.edu/?page_id=249', '공과대학 융합에너지신소재공학과']
        , [2, 'https://dee.dongguk.edu/?page_id=553', '공과대학 전자전기공학부']
        , [2, 'https://dee.dongguk.edu/?page_id=555', '공과대학 전자전기공학부']
        , [2, 'https://dee.dongguk.edu/?page_id=557', '공과대학 전자전기공학부']
        , [2, 'https://ice.dongguk.edu/?page_id=18518', '공과대학 정보통신공학전공']
        , [2, 'https://cse.dongguk.edu/?page_id=799', '공과대학 컴퓨터공학전공']
        , [2, 'https://cse.dongguk.edu/?page_id=827', '공과대학 컴퓨터공학전공']
        , [2, 'https://chembioeng.dongguk.edu/?page_id=207', '공과대학 화공생물공학과']
        , [2, 'https://chembioeng.dongguk.edu/?page_id=83742', '공과대학 화공생물공학과']
        , [2, 'https://education.dongguk.edu/?page_id=230', '사범대학 교육학과']
        , [2, 'https://duce.dongguk.edu/?page_id=245', '사범대학 국어교육과']
        , [2, 'https://geoedu.dongguk.edu/?page_id=148', '사범대학 지리교육과']
        , [2, 'https://dume.dongguk.edu/?page_id=223', '사범대학 수학교육과']
        , [2, 'https://homeedu.dongguk.edu/?page_id=211', '사범대학 가정교육과']
        , [2, 'https://pe.dongguk.edu/?page_id=230', '사범대학 체육교육과']
        , [2, 'https://theatre.dongguk.edu/?page_id=391', '예술대학 연극학부']

        , [3, 'https://comm.dongguk.edu/gnuboard4/bbs/board.php?bo_table=2_5', '사회과학대학 미디어커뮤니케이션학과']
        , [3, 'https://comm.dongguk.edu/gnuboard4/bbs/board.php?bo_table=2_5_1', '사회과학대학 미디어커뮤니케이션학과']
        , [3, 'https://comm.dongguk.edu/gnuboard4/bbs/board.php?bo_table=2_5_2', '사회과학대학 미디어커뮤니케이션학과']

        , [4, 'http://www.donggukfoodindus-edu.com/bbs/board.php?bo_table=table38', '사회과학대학 식품산업관리학과']
        , [4, 'http://www.donggukfoodindus-edu.com/bbs/board.php?bo_table=table39', '사회과학대학 식품산업관리학과']
        , [4, 'http://www.donggukfoodindus-edu.com/bbs/board.php?bo_table=table40', '사회과학대학 식품산업관리학과']

        , [5, 'http://dguadpr.kr/bbs/board.php?bo_table=table31', '사회과학대학 광고홍보학과']
        , [5, 'http://dguadpr.kr/bbs/board.php?bo_table=table40', '사회과학대학 광고홍보학과']
        , [5, 'http://justice.dongguk.edu/bbs/board.php?bo_table=justice7_1', '경찰사법대학']
        , [5, 'https://movie.dongguk.edu/bbs/board.php?bo_table=movie1_3_1', '예술대학 영화영상학과']

        , [6, 'https://security.dongguk.edu/bbs/data/list.do?menu_idx=30', '미래융합대학 융합보안학과']
        , [6, 'https://swc.dongguk.edu/bbs/data/list.do?menu_idx=46', '미래융합대학 사회복지상담학과']
        , [6, 'https://gt.dongguk.edu/bbs/data/list.do?menu_idx=58', '미래융합대학 글로벌무역학과']

        , [7, 'http://engineer.dongguk.edu/en5_1', '공과대학']

        , [8, 'http://mme.dongguk.edu/k3/sub5/sub1.php?tsort=51&msort=62', '공과대학 멀티미디어공학과']

        , [9, 'https://fc.dongguk.edu/bbs/data/list.do?menu_idx=12', '미래융합대학']

        , [10, 'https://ai.dongguk.edu/aix6_1', 'AI 융합학부']

        , [11, 'http://ise.dongguk.edu/bbs/board.php?bo_table=ise6_1', '공과대학 산업시스템공학과']
        , [11, 'http://ise.dongguk.edu/bbs/board.php?bo_table=ise8_7', '공과대학 산업시스템공학과']
        , [2, 'https://me.dongguk.edu/?page_id=218', '공과대학 융합에너지신소재공학과']
    ]

    # 사이트마다 페이징을 위한 변수가 다름.
    page_list = [
        '&spage='  # 0
        , '&page='  # 1
        , '&pageid='  # 2
        , '&page='  # 3
        , '&page='  # 4
        , '&page='  # 5
        , '&pageIndex='  # 6
        , '/p'  # 7
        , '&page='  # 8
        , '&pageIndex='  # 9
        , ''  # 10
        , '&page='  # 11
    ]

    # 크롤링에 사용할 변수 배열
    crawl_var_list = [
        ['#board_list > tbody > tr', 'td', 'td.title > a']
        , ['#s_right > div > table > tr > td > form > table > tr', 'td', 'td > a']
        , ['#kboard-default-list > div.kboard-list > table > tbody > tr', 'td', '.kboard-list-title > div > a']
        , ['.board_list > tr', '.num', 'td.subject > a']
        , ['#sh_list_tbl > table > tbody > tr', '.num', '.subject > div > a']
        , ['#fboardlist > div > table > tbody > tr', '.td_num', '.td_subject > a']
        , ['.module-content > table > tbody > tr', '.latin', '.cell_type > a']
        , ['#fboardlist > div.bo_list > ul > li', '.mobile_none', '.bo_tit > a']
        , ['#inner_wrap > div.rightW > div.sub_con > div.board_listW > table > tbody > tr', '.w_cell', '.subject > a']
        , ['#dBody > table > tbody > tr', '.latin', '.cell_type > a']
        , ['#fboardlist > div.bo_list > ul > li', '.mobile_none', '.bo_tit > a']
        , ['', 'td', 'td > a']
    ]

    # 데이터베이스에 저장할 게시글의 링크용
    link_list = [
        'https://www.dongguk.edu/mbs/kr/jsp/board/'
        , ''
        , 'origin'
        , ''
        , 'perfect'
        , 'perfect'
        , ''
        , 'perfect'
        , 'origin'
        , ''
        , 'perfect'
        , ''
    ]

    for list in url_list:

        url = list[1]  # url_list가 2차원 배열이므로, 공지사항 링크를 변수 url에 저장
        now_site_type = list[0]  # 현재 사이트 type 저장
        curPage = 1  # url_list의 loop를 돌면서 url이 변경될 때 마다 현재 페이지를 1로 설정
        site_per = 0  # url_list의 loop를 돌면서 url이 변경될 때 마다 크롤링 한 게시글의 개수 파악

        while curPage <= totalPage:

            # 페이지 번호 출력
            print('\n----- Current Page : {}'.format(curPage), '------\noriginal url : ' + url)

            # 변경된 url에 페이지 번호를 붙임
            if now_site_type == 10:
                url_change = url
            else:
                url_change = url + page_list[now_site_type] + f'{curPage}'
            print('changed url : ' + url_change + '\n-------------------------------------------------')

            # 페이지가 변경됨에 따라 delay 발생 시킴
            time.sleep(3)

            # 변경된 url로 이동하여 크롤링하기 위해 html 페이지를 파싱
            html = urllib.request.urlopen(url_change).read()
            soup = BeautifulSoup(html, 'html.parser')

            # 게시글 리스트 선택
            if now_site_type == 11:
                board_list = soup.find('form').find_all('tr')
            else:
                board_list = soup.select(crawl_var_list[now_site_type][0])

            # 카테고리 정보는 크롤링하지 않고 2차원 배열에 저장한 값을 읽음.
            category = list[2]

            for board in board_list:
                # 고정된 공지는 td > img 형태인데, 이를 text로 변환하면 공백이 됨
                # type3는 None 값이 발생하여 예외처리
                if now_site_type == 3:
                    notice = board.select_one(crawl_var_list[now_site_type][1])
                else:
                    notice = board.select_one(crawl_var_list[now_site_type][1]).text.strip()
                    if (now_site_type == 6 or now_site_type == 8 or now_site_type == 9) and notice == "":
                        notice = "공지"

                if notice == "" or notice is None or notice == "번호":  # 공백인 경우 고정공지이므로 크롤링 하지 않음
                    continue
                else:  # 값이 있는 경우 일반공지로, 크롤링 진행
                    # type3는 None 값이 발생하여 예외처리
                    if now_site_type == 3:
                        notice = notice.text.strip()

                    # 게시글 제목
                    name = board.select_one(crawl_var_list[now_site_type][2]).text.strip()

                    # 게시글 링크는 경우에 따라 편집 필요
                    # 1) 공백이면 편집
                    if link_list[now_site_type] == '':
                        if now_site_type == 1 or now_site_type == 3 or now_site_type == 11:
                            link = url_change + '&' + board.select_one(crawl_var_list[now_site_type][2]).get('href')[
                                                      17:]
                        elif now_site_type == 6:
                            link_origin = board.select_one(crawl_var_list[now_site_type][2]).get('href')
                            link1 = link_origin[20:32]
                            link2 = link_origin[35:47]
                            # 미래융합대학 학과별 사이트 상세링크 관련
                            detail_url = [
                                'https://security.dongguk.edu/bbs/data/view.do?menu_idx=30'
                                , 'https://swc.dongguk.edu/bbs/data/view.do?menu_idx=46'
                                , 'https://gt.dongguk.edu/bbs/data/view.do?menu_idx=58'
                            ]
                            link = detail_url[loop_index] + f'&pageIndex={curPage}&bbs_mst_idx={link1}&data_idx={link2}'
                        elif now_site_type == 9:
                            link_origin = board.select_one('.cell_type > a').get('href')
                            link1 = link_origin[20:32]
                            link2 = link_origin[35:47]
                            link = f'https://fc.dongguk.edu/bbs/data/view.do?&pageIndex={curPage}&menu_idx=12&bbs_mst_idx={link1}&data_idx={link2}'

                    # 2) origin이면 기존 사이트 url 사용
                    elif link_list[now_site_type] == 'origin':
                        link = url + board.select_one(crawl_var_list[now_site_type][2]).get('href')

                    # 3) perfect면 a 태그의 url 그대로 사용
                    elif link_list[now_site_type] == 'perfect':
                        link = board.select_one(crawl_var_list[now_site_type][2]).get('href')

                    # 4) 특정 url 사용
                    else:
                        link = link_list[now_site_type] + board.select_one(crawl_var_list[now_site_type][2]).get('href')

                    # DB에 저장
                    results = session.query(Crawl.link).filter_by(category=category, link=link).all()
                    if not results:
                        now_time = str(datetime.datetime.now())
                        session.add(Crawl(category=category, title=name, link=link, crawl_time=now_time))
                        session.commit()
                        print('성공 : [' + category + ']' + name + ' >> ' + link)

                        # new_crawl_list를 2차원 형태로 만들어서 신규 크롤링 데이터 추가
                        new_crawl_list.append([])
                        new_crawl_list[new_crawl_count].append(category)
                        new_crawl_list[new_crawl_count].append(name.replace("\xa0", " "))
                        new_crawl_list[new_crawl_count].append(link)
                        new_crawl_list[new_crawl_count].append(now_time)
                        new_crawl_count += 1
                    else:
                        print('     실패 : [' + category + ']' + name + ' >> ' + link)

                    # 크롤링 한 게시글 개수 증가
                    site_per += 1

            # 현재 페이지의 게시글을 크롤링하는 for loop 종료

            # 페이지 수 증가
            curPage += 1

            if now_site_type == 2 or now_site_type == 6:
                if site_per < 10:
                    print('------------------ 게시글 개수가 적어서 현재 페이지에서 크롤링 종료 (10) ------------------')
                    break
            else:
                if site_per < 15:
                    print('------------------ 게시글 개수가 적어서 현재 페이지에서 크롤링 종료 (15) ------------------')
                    break

            if curPage > totalPage:
                print('------------------ ' + category + ' 크롤링 종료 ------------------')
                break

            # 3초간 대기
            time.sleep(3)

        # 미래융합대학 학과별 사이트 상세링크 관련
        if now_site_type == 6:
            loop_index += 1

    print("~~~ 크롤링 끄읕 !!!")

    del soup  # BeautifulSoup 인스턴스 삭제
    session.close()  # DB 세션 종료

    return "크롤링 페이지"


if __name__ == '__main__':
    app.run('0.0.0.0', port=3000, debug=True)
