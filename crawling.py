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
workbook = xlsxwriter.Workbook(savePath + 'crawling_result.xlsx')

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

worksheet.set_column('A:A', 40)  # A 열의 너비를 40으로 설정
worksheet.set_column('B:B', 80)  # B 열의 너비를 12로 설정

worksheet.write(0, 0, '타이틀')
worksheet.write(0, 1, '링크')

while curPage <= totalPage:
    url = f'https://www.dongguk.edu/mbs/kr/jsp/board/list.jsp?boardId=11533472&id=kr_010808000000&spage={curPage}'
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')

    # 게시글 리스트 선택
    board_list = soup.select('#board_list > tbody > tr')
    category = soup.select_one('p.location > strong').text.strip()
    print(category)
    # 페이지 번호 출력
    print('----- Current Page : {}'.format(curPage), '------')

    for board in board_list:
        # 게시글 제목, 링크

        name = board.select_one('td.title > a').text.strip()
        link = 'https://www.dongguk.edu/mbs/kr/jsp/board/'+board.select_one('td.title > a').get('href')

        print(name+link)

        # 엑셀 저장(텍스트)
        worksheet.write(excel_row, 0, category)
        worksheet.write(excel_row, 1, name)
        worksheet.write(excel_row, 2, link)

        # 엑셀 행 증가
        excel_row += 1

    print()

    # 페이지 수 증가
    curPage += 1

    if curPage > totalPage:
        print('Crawling succeed!')
        break

    # BeautifulSoup 인스턴스 삭제
    del soup

    # 3초간 대기
    time.sleep(3)


# 엑셀 파일 닫기
workbook.close()  # 저장