import requests
import pandas as pd

#주요 api 설명
#날짜별 경기목록
#https://statsapi.mlb.com/api/v1/schedule/games?sportId=1&date=MM/DD/YYYY
#특정시즌의 선수
#https://statsapi.mlb.com/api/v1/sports/1/players?season=2023
#실시간 경기데이터
#https://statsapi.mlb.com/api/v1/game/{gamePk}/feed/live

# 2023 시즌 선수목록 api 호출
url = "https://statsapi.mlb.com/api/v1/sports/1/players?season=2023"
response = requests.get(url)
data = response.json()

#호출한 결과에서 선수정보 추출
players = data.get('people', [])
df = pd.DataFrame(players)
df = df[['id', 'fullName', 'primaryPosition', 'birthDate']]
print(df.head())