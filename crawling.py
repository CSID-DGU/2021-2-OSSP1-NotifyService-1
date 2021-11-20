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
    ['https://comm.dongguk.edu/gnuboard4/bbs/board.php?bo_table=2_5', '사회과학대학 미디어커뮤니케이션학과']
    , ['https://comm.dongguk.edu/gnuboard4/bbs/board.php?bo_table=2_5_1', '사회과학대학 미디어커뮤니케이션학과']
    , ['https://comm.dongguk.edu/gnuboard4/bbs/board.php?bo_table=2_5_1', '사회과학대학 미디어커뮤니케이션학과']

]

site_per = 0

for list in url_list:

    # url_list가 2차원 배열이므로, 공지사항 링크를 변수 url에 저장
    url = list[0]

    # url_list의 loop를 돌면서 url이 변경될 때 마다 현재 페이지를 1로 설정
    curPage = 1
    site_per = 0
    while curPage <= totalPage:
        # 페이지 번호 출력
        print('\n----- Current Page : {}'.format(curPage), '------')
        print('original url : ' + url)

        # 변경된 url에 페이지 번호를 붙임
        url_change = url + f'&page={curPage}'
        print('changed url : ' + url_change)
        print('-------------------------------------------------')

        # 페이지가 변경됨에 따라 delay 발생 시킴
        time.sleep(3)

        # 변경된 url로 이동하여 크롤링하기 위해 html 페이지를 파싱
        html = urllib.request.urlopen(url_change).read()
        soup = BeautifulSoup(html, 'html.parser')

        # 게시글 리스트 선택
        board_list = soup.select('.board_list > tr')


        # 카테고리 정보는 크롤링하지 않고 2차원 배열에 저장한 값을 읽음.
        category = list[1]

        for board in board_list:
            notice = board.select_one('.num')

            if notice is None:  # 공백인 경우 고정공지이므로 크롤링 하지 않음
                continue
            else:  # 값이 있는 경우 일반공지로, 크롤링 진행
                notice = notice.text.strip()
                if notice == '공지':
                    continue
                else:
                    # 게시글 제목, 링크
                    name = board.select_one('td.subject > a').text.strip()
                    link = url_change + board.select_one('td.subject > a').get('href')

                    print('[' + notice + ']' + name + ' >> ' + link)

                    # 엑셀 저장(텍스트)
                    worksheet.write(excel_row, 0, category)  # 분류
                    worksheet.write(excel_row, 1, notice)  # 글번호
                    worksheet.write(excel_row, 2, name)  # 제목
                    worksheet.write(excel_row, 3, link)  # 링크

                    # 엑셀 행 증가
                    excel_row += 1
                    site_per += 1

        # 현재 페이지의 게시글을 크롤링하는 for loop 종료

        # 페이지 수 증가
        curPage += 1

        if site_per < 15:
            print('------------------ 게시글 개수가 적어서 현재 페이지에서 크롤링 종료 ------------------')
            break

        if curPage > totalPage:
            print('------------------ ' + category + ' 크롤링 종료 ------------------')
            break

        # 3초간 대기
        time.sleep(3)

print("~~~ 끄읕 !!!")
# BeautifulSoup 인스턴스 삭제
del soup

# 엑셀 파일 닫기
workbook.close()  # 저장
