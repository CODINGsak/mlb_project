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
        #return값에 이름과 id를 함께 반환하도록 시킴
        return [
            {
                "name": player['person']['fullName'],
                "id": player['person']['id']
            }
            for player in roster
        ]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching roster for {team_name}: {e}")
        return []

#선수별 2개이상 데이터 받는 함수, 선수별 비교 기능 구현 함수
def compare_players_rosters(roster, season='2025'):
    comparison = {}
    for player in roster:
        name = player['name']
        player_id = player['id']
        stats = get_player_stats(player_id, season)
        if stats:
            #주요 추출 지표(타자 기준)
            #stat이라는 변수 안에, stats 리스트의 첫 번째 원소에서 'stat' 키에 해당하는 값을 추출해서 넣기
            stat = stats[0]['stat']
            comparison[name] = {
                "AVG": stat.get("avg"),
                "HR": stat.get("homeRuns"),
                "OPS": stat.get("ops"),
                "RBI": stat.get("rbi")
            }
    return comparison

#api call test
#player_id = 660271  # Shohei Ohtani
#stats = get_player_stats(player_id, season='2025')
#save_stats_json("Shohei_Ohtani", stats)

team_name = "Yankees"
roster = get_team_roster(team_name)
print([p['name'] for p in roster])  # 이름만 출력

selected_players = roster[:2]  # 예시로 상위 2명 비교
result = compare_players_rosters(selected_players)
print(json.dumps(result, indent=4))