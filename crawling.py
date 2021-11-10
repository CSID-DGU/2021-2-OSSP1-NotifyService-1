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

worksheet.set_column('A:A', 20)  # A 열의 너비를 40으로 설정
worksheet.set_column('B:B', 40)  # B 열의 너비를 12로 설정
worksheet.set_column('C:C', 80)  # B 열의 너비를 12로 설정

worksheet.write(0, 0, '카테고리')
worksheet.write(0, 1, '타이틀')
worksheet.write(0, 2, '링크')

url_list = [
    'https://www.dongguk.edu/mbs/kr/jsp/board/list.jsp?boardId=3646&id=kr_010802000000' #일반
    , 'https://www.dongguk.edu/mbs/kr/jsp/board/list.jsp?boardId=3638&id=kr_010801000000' #학사
    , 'https://www.dongguk.edu/mbs/kr/jsp/board/list.jsp?boardId=3654&id=kr_010803000000' #입시
    , 'https://www.dongguk.edu/mbs/kr/jsp/board/list.jsp?boardId=3662&id=kr_010804000000' #장학
    , 'https://www.dongguk.edu/mbs/kr/jsp/board/list.jsp?boardId=9457435&id=kr_010807000000' #국제
    , 'https://www.dongguk.edu/mbs/kr/jsp/board/list.jsp?boardId=11533472&id=kr_010808000000' #학술/행사
]

for url in url_list:
    curPage = 1
    while curPage <= totalPage:
        time.sleep(3)
        # 페이지 번호 출력
        print('----- Current Page : {}'.format(curPage), '------')
        print('original url : '+url)

        url_change = url + f'&spage={curPage}'
        print('changed url : '+url_change)

        time.sleep(3)

        html = urllib.request.urlopen(url_change).read()
        soup = BeautifulSoup(html, 'html.parser')

        # 게시글 리스트 선택
        board_list = soup.select('#board_list > tbody > tr')
        category = soup.select_one('p.location > strong').text.strip()

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


        # 3초간 대기
        time.sleep(3)


# BeautifulSoup 인스턴스 삭제
del soup

# 엑셀 파일 닫기
workbook.close()  # 저장
