## 문제는.. type2는 공지사항으로 설정되면 목록에서 사라진다는 것..
import urllib
import chromedriver_autoinstaller
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
# 엑셀 처리 임포트
import xlsxwriter

options = Options()
options.add_argument('headless');  # headless는 화면이나 페이지 이동을 표시하지 않고 동작하는 모드

# Excel 처리 선언
savePath = "c:/Users/jiwon/Documents/"
name = time.strftime('%H%M%S')+'result.xlsx'
workbook = xlsxwriter.Workbook(savePath + name)

# 워크 시트
worksheet = workbook.add_worksheet()

# 검색 결과가 렌더링 될 때까지 잠시 대기
time.sleep(3)

# 현재 페이지
curPage = 1

# 크롤링할 전체 페이지수
totalPage = 2

# 엑셀 행 수
excel_row = 1

worksheet.set_column('A:A', 10)  # A 열의 너비 설정
worksheet.set_column('B:B', 10)  # B 열의 너비 설정
worksheet.set_column('C:C', 40)  # C 열의 너비 설정
worksheet.set_column('D:D', 80)  # D 열의 너비 설정

worksheet.write(0, 0, '분류')
worksheet.write(0, 1, '글번호')
worksheet.write(0, 2, '제목')
worksheet.write(0, 3, '링크')

url_list = [
    ['https://kor-cre.dongguk.edu/?page_id=282', '문과대학 국어국문문예창작학부']
		, ['https://english.dongguk.edu/?page_id=250', '문과대학 영어영문학부 ']
		, ['https://english.dongguk.edu/?page_id=259', '문과대학 영어영문학부 ']
		, ['https://dj.dongguk.edu/?page_id=203', '문과대학 일본학과 ']
		, ['https://dj.dongguk.edu/?page_id=225', '문과대학 일본학과 ']
		, ['https://china.dongguk.edu/?page_id=208', '문과대학 중어중문학과 ']
		, ['https://sophia.dongguk.edu/?page_id=230', '문과대학 철학과 ']
		, ['https://history.dongguk.edu/?page_id=505', '문과대학 사학과 ']
		, ['https://chem.dongguk.edu/?page_id=288', '이과대학 화학과 ']
		, ['https://chem.dongguk.edu/?page_id=288', '이과대학 통계학과 ']
		, ['https://stat.dongguk.edu/?page_id=437', '이과대학 통계학과 ']
		, ['https://math.dongguk.edu/?page_id=260', '이과대학 수학과']
		, ['https://physics.dongguk.edu/?page_id=324', '이과대학 물리반도체과학부 ']
		, ['https://physics.dongguk.edu/?page_id=326', '이과대학 물리반도체과학부 ']
		, ['https://politics.dongguk.edu/?page_id=18518', '사회과학대학 정치외교학과 ']
		, ['https://politics.dongguk.edu/?page_id=18522', '사회과학대학 정치외교학과 ']
		, ['https://pa.dongguk.edu/?page_id=233', '사회과학대학 행정학과 ']
		, ['https://nk.dongguk.edu/?page_id=225', '사회과학대학 북한학과 ']
		, ['https://econ.dongguk.edu/?page_id=262', '사회과학대학 경제학과 ']
		, ['https://econ.dongguk.edu/?page_id=297', '사회과학대학 경제학과']
		, ['http://itrade.dongguk.edu/?page_id=150', '사회과학대학 국제통상학과 ']
		, ['https://sociology.dongguk.edu/?page_id=211', '사회과학대학 사회학과 ']
		, ['https://welfare.dongguk.edu/?page_id=209', '사회과학대학 사회복지학과 ']
		, ['https://police.dongguk.edu/?page_id=18349', '경찰사법대학 경찰행정학부 ']
		, ['https://mgt.dongguk.edu/?page_id=18326', '경영대학 경영학과 ']
		, ['https://acc.dongguk.edu/?page_id=18334', '경영대학 회계학과 ']
		, ['https://acc.dongguk.edu/?page_id=1087707', '경영대학 회계학과 ']
		, ['https://acc.dongguk.edu/?page_id=18328', '경영대학 회계학과 ']
		, [' http://mis.dongguk.edu/?page_id=269', '경영대학 경영정보학과 ']
		, ['https://bio.dongguk.edu/?page_id=18531', '바이오시스템대학 바이오환경과학과 ']
		, ['https://lifescience.dongguk.edu/?page_id=150', '바이오시스템대학 생명과학과 ']
		, ['https://food.dongguk.edu/?page_id=243', '바이오시스템대학 식품생명공학과 ']
		, [' http://mbt.dongguk.edu/?page_id=241', '바이오시스템대학 의생명공학과 ']
		, ['https://civil.dongguk.edu/?page_id=269', '공과대학 건설환경공학과 ']
		, ['https://civil.dongguk.edu/?page_id=271', '공과대학 건설환경공학과 ']
		, ['https://civil.dongguk.edu/?page_id=273', '공과대학 건설환경공학과 ']
		, [' https://civil.dongguk.edu/?page_id=277', '공과대학 건설환경공학과 ']
		, ['https://archi.dongguk.edu/?page_id=18387', '공과대학 건축공학부 ']
		, ['https://archi.dongguk.edu/?page_id=18394', '공과대학 건축공학부 ']
		, ['https://mecha.dongguk.edu/?page_id=207', '공과대학 기계로봇에너지공학과 ']
		, ['https://mecha.dongguk.edu/?page_id=332', '공과대학 기계로봇에너지공학과 ']
		, ['https://me.dongguk.edu/?page_id=249', '공과대학 융합에너지신소재공학과 ']
		, ['https://dee.dongguk.edu/?page_id=553', '공과대학 전자전기공학부 ']
		, ['https://dee.dongguk.edu/?page_id=555', '공과대학 전자전기공학부 ']
		, ['https://dee.dongguk.edu/?page_id=557', '공과대학 전자전기공학부 ']
		, ['https://ice.dongguk.edu/?page_id=18518', '공과대학 정보통신공학전공 ']
		, ['https://cse.dongguk.edu/?page_id=799', '공과대학 컴퓨터공학전공']
		, ['https://cse.dongguk.edu/?page_id=827', '공과대학 컴퓨터공학전공']
		, ['https://chembioeng.dongguk.edu/?page_id=207', '공과대학 화공생물공학과 ']
		, ['https://chembioeng.dongguk.edu/?page_id=83742', '공과대학 화공생물공학과 ']
		, ['https://education.dongguk.edu/?page_id=230', '사범대학 교육학과 ']
		, ['https://duce.dongguk.edu/?page_id=245', '사범대학 국어교육과 ']
		, ['https://geoedu.dongguk.edu/?page_id=148', '사범대학 지리교육과 ']
		, ['https://dume.dongguk.edu/?page_id=223', '사범대학 수학교육과 ']
		, ['https://homeedu.dongguk.edu/?page_id=211', '사범대학 가정교육과 ']
		, ['https://pe.dongguk.edu/?page_id=230', '사범대학 체육교육과 ']
		, ['https://theatre.dongguk.edu/?page_id=391', '예술대학 연극학부 ']
]

for list in url_list:

    # url_list가 2차원 배열이므로, 공지사항 링크를 변수 url에 저장
    url = list[0]

    # url_list의 loop를 돌면서 url이 변경될 때 마다 현재 페이지를 1로 설정
    curPage = 1

    while curPage <= totalPage:

        # 페이지 번호 출력
        print('\n----- Current Page : {}'.format(curPage), '------')
        print('original url : ' + url)

        # 변경된 url에 페이지 번호를 붙임
        url_change = url + f'&pageid={curPage}'
        print('changed url : ' + url_change)
        print('-------------------------------------------------')

        # 페이지가 변경됨에 따라 delay 발생 시킴
        time.sleep(3)

        # 변경된 url로 이동하여 크롤링하기 위해 html 페이지를 파싱
        html = urllib.request.urlopen(url_change).read()
        soup = BeautifulSoup(html, 'html.parser')

        # 게시글 리스트 선택
        board_list = soup.select('#kboard-default-list > div.kboard-list > table > tbody > tr')

        # 카테고리 정보는 크롤링하지 않고 2차원 배열에 저장한 값을 읽음.
        category = list[1]

        for board in board_list:

            # 게시글이 고정된 공지사항인 경우 크롤링하지 않음
            # 고정된 공지는 td > img 형태인데, 이를 text로 변환하면 공백이 됨
            notice = board.select_one('td').text.strip()

            if notice == "공지사항":  # 공백인 경우 고정공지이므로 크롤링 하지 않음
                continue
            else:  # 값이 있는 경우 일반공지로, 크롤링 진행
                # 게시글 제목, 링크
                name = board.select_one('.kboard-list-title > div > a').text.strip()
                link = board.select_one('.kboard-list-title > div > a').get('href')

                print('[' + notice + ']' + name + ' >> ' + link)

                # 엑셀 저장(텍스트)
                worksheet.write(excel_row, 0, category)  # 분류
                worksheet.write(excel_row, 1, notice)  # 글번호
                worksheet.write(excel_row, 2, name)  # 제목
                worksheet.write(excel_row, 3, link)  # 링크

                # 엑셀 행 증가
                excel_row += 1

        # 현재 페이지의 게시글을 크롤링하는 for loop 종료

        # 페이지 수 증가
        curPage += 1

        if curPage > totalPage:
            print('------------------ ' + category + ' 크롤링 종료 ------------------')
            break

        # 3초간 대기
        time.sleep(3)

# BeautifulSoup 인스턴스 삭제
del soup

# 엑셀 파일 닫기
workbook.close()  # 저장
