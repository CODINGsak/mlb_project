import pandas as pd
import requests
import json
import os
import matplotlib.pyplot as plt
import seaborn as sns

#주요 api 설명
#날짜별 경기목록
#https://statsapi.mlb.com/api/v1/schedule/games?sportId=1&date=MM/DD/YYYY
#특정시즌의 선수
#https://statsapi.mlb.com/api/v1/sports/1/players?season=2023
#실시간 경기데이터
#https://statsapi.mlb.com/api/v1/game/{gamePk}/feed/live

# 선수데이터 수집 api 함수(streamlit 백엔드)
# 이름 + ID 매핑함수
#api가 엉뚱한 선수를 return하기때문에 우선 전체 주석처리
'''
def get_player_id_name(name):
    url = f"https://statsapi.mlb.com/api/v1/people/search?name={name}"
    try:
        response = requests.get(url)
        #raise_for_status 파이썬의 HTTP요청 결과 오류발생 여부 확인
        response.raise_for_status()
        data = response.json()
        people = data.get('people',[])
        #people리스트를 for하면서 fullName이 일치하는 선수만 return
        print(f"[DEBUG] Search result for '{name}': {[p['fullName'] for p in people]}")
        for person in people:
            if person.get('fullName','').lower() == name.lower():
                return person['id']
        print(f"Can't find player name: {name}")
        return None
    except requests.exceptions.RequestException as e :
        print(f"Error fetching stats for player {name}: {e}")
        return None
'''

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

# 팀 이름 → 팀 ID 매핑
team_ids = {
    "Angels": 108,
    "Astros": 117,
    "Athletics": 133,
    "Blue Jays": 141,
    "Braves": 144,
    "Brewers": 158,
    "Cardinals": 138,
    "Cubs": 112,
    "Diamondbacks": 109,
    "Dodgers": 119,
    "Giants": 137,
    "Guardians": 114,
    "Mariners": 136,
    "Marlins": 146,
    "Mets": 121,
    "Nationals": 120,
    "Orioles": 110,
    "Padres": 135,
    "Phillies": 143,
    "Pirates": 134,
    "Rangers": 140,
    "Rays": 139,
    "Red Sox": 111,
    "Reds": 113,
    "Rockies": 115,
    "Royals": 118,
    "Tigers": 116,
    "Twins": 142,
    "White Sox": 145,
    "Yankees": 147
}

# 팀id에서 선수리스트 가져오기
# 타자/투수 자동 구분이 가능하도록 리팩토링
def get_team_roster(team_name):
    team_id = team_ids.get(team_name)
    if not team_id:
        print(f"Unknown team: {team_name}")
        return []

    url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}/roster"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        roster = data.get('roster', [])
        
        enriched_roster = []
        for player in roster:
            player_id = player['person']['id']
            player_name = player['person']['fullName']
            #선수 상세정보 호출 api
            detail_url = f"https://statsapi.mlb.com/api/v1/people/{player_id}"
            detail_resp = requests.get(detail_url)
            detail_resp.raise_for_status()
            detail_data = detail_resp.json()
            position = detail_data.get('people', [{}])[0].get('primaryPosition', {}).get('name', 'Unknown')

            enriched_roster.append({
                "name" : player_name,
                "id" : player_id,
                "position" : position
            })

        return enriched_roster

    except requests.exceptions.RequestException as e:
        print(f"Error fetching roster for {team_name}: {e}")
        return []

#선수별 2개이상 데이터 받는 함수, 선수별 비교 기능 구현 함수
#포지션별로 분기해서 타자/투수별 비교 지표 다르게 구성
def compare_players_rosters(roster, season='2025'):
    comparison = {}
    for player in roster:
        name = player['name']
        player_id = player['id']
        position = player.get("position", "Unknown")
        
        stats = get_player_stats(player_id, season)
        if not stats:
            comparison[name] = {"Note": "No stats available"}
            continue        
        stat = stats[0].get('stat',{})
            
        if position == "Pitcher":    
            comparison[name] = {
                "ERA": stat.get("era") or "N/A",
                "SO": stat.get("strikeOuts") or "N/A",
                "WHIP": stat.get("whip") or "N/A",
                "W": stat.get("wins") or "N/A"
            }
        else :
            comparison[name] = {
                "AVG": stat.get("avg") or "N/A",
                "HR": stat.get("homeRuns") or "N/A",
                "OPS": stat.get("ops") or "N/A",
                "RBI": stat.get("rbi") or "N/A"
            }
    return comparison

#api call test
team_name = "Yankees"
roster = get_team_roster(team_name)
#이름+포지션 확인 test
print("Select team roaster:")
for player in roster[:5]: #상위 5명을 출력
    print(f"- {player['name']} ({player['position']})")

selected_players = roster[:2]  # 예시로 상위 2명 비교

#비교결과 pandas출력 test
#DataFrame변환
result = compare_players_rosters(selected_players)
df = pd.DataFrame.from_dict(result, orient='index')
df_clean = df.replace("N/A", pd.NA).dropna(axis=1, how='all')  # N/A 제거
df_numeric = df_clean.apply(pd.to_numeric, errors='coerce')    # 숫자형 변환
print(df) 

#matplotlib으로 막대그래프 그리기
df_numeric.plot(kind='bar', figsize=(10, 6))
plt.title("MLB 선수별 주요 지표 비교")
plt.ylabel("값")
plt.xlabel("선수 이름")
plt.xticks(rotation=45)
plt.legend(title="지표")
plt.tight_layout()
plt.show()