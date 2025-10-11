import requests
import json
import os

#주요 api 설명
#날짜별 경기목록
#https://statsapi.mlb.com/api/v1/schedule/games?sportId=1&date=MM/DD/YYYY
#특정시즌의 선수
#https://statsapi.mlb.com/api/v1/sports/1/players?season=2023
#실시간 경기데이터
#https://statsapi.mlb.com/api/v1/game/{gamePk}/feed/live

# 선수데이터 수집 api 함수(streamlit 백엔드)
# 이름 + ID 매핑함수
def get_player_id_name(name):
    url = f"https://statsapi.mlb.com/api/v1/people/search?name={name}"
    try:
        response = requests.get(url)
        #raise_for_status 파이썬의 HTTP요청 결과 오류발생 여부 확인
        response.raise_for_status()
        data = response.json()
        people = data.get('people',[])
        if people:
            return people[0]['id']
        else:
            print(f"Can't find player name: {name}")
            return None
    except requests.exceptions.RequestException as e :
        print(f"Error fetching stats for player {name}: {e}")
        return None

# 선수ID + 통계 조회함수
def get_player_stats(player_id , season='2025'):
    url = f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats?stats=season&season={season}&gameType=R"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        stats = data.get('stats',[])
        #stats리스트의 첫 원소값에서 splits이라는 이름의 성적 데이터 추출하기
        if stats and 'splits' in stats[0]:
            return stats[0]['splits']
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching stats for player {player_id}: {e}")
        return None

#데이터 저장 함수
def save_stats_json(player_name, stats, season='2025'):
    os.makedirs("data", exist_ok=True)
    filename = f"data/{player_name.lower()}_{season}_stats.json"
    with open(filename,"w") as f:
        json.dump(stats,f,indent=4)
    print(f"Saved to {filename}")

# api call test
player_id = 660271  # Shohei Ohtani
stats = get_player_stats(player_id, season='2025')
save_stats_json("Shohei_Ohtani", stats)