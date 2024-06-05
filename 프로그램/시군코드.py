import requests
from bs4 import BeautifulSoup
import pandas as pd

# API 키 설정 (여기에 실제 API 키를 입력해야 합니다)
API_KEY = "F240513145"
BASE_URL = f"http://www.opinet.co.kr/api/areaCode.do?out=xml&code={API_KEY}&area="

# 시도 코드와 이름을 저장할 딕셔너리
sido_codes = {
    "01": "서울",
    "02": "경기",
    "03": "강원",
    "04": "충북",
    "05": "충남",
    "06": "전북",
    "07": "전남",
    "08": "경북",
    "09": "경남",
    "10": "부산",
    "11": "제주",
    "14": "대구",
    "15": "인천",
    "16": "광주",
    "17": "대전",
    "18": "울산",
    "19": "세종"
}

# 결과를 저장할 리스트
result_list = []

# 각 시도에 대해 요청을 보내고 데이터를 파싱하여 저장
for sido_code, sido_name in sido_codes.items():
    url = BASE_URL + sido_code
    response = requests.get(url)
    soup = BeautifulSoup(response.content,  'lxml-xml')

    items = soup.find_all('OIL')
    for item in items:
        area_cd = item.find('AREA_CD').text if item.find('AREA_CD') else ''
        area_nm = item.find('AREA_NM').text if item.find('AREA_NM') else ''
        result_list.append({"시도": sido_name, "구": area_nm, "코드": area_cd})

# 데이터프레임으로 변환
df = pd.DataFrame(result_list)

# 엑셀 파일로 저장
df.to_excel("area_codes.xlsx", index=False)

print("엑셀 파일이 성공적으로 저장되었습니다.")