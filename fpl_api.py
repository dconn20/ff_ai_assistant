
import requests
from collections import defaultdict

POSITION_MAP = {
    1: "Goalkeeper",
    2: "Defender",
    3: "Midfielder",
    4: "Forward"
}

POSITION_WEIGHT = {
    1: 1.2,
    2: 1.0,
    3: 1.5,
    4: 2.0
}

FIXTURE_DIFFICULTY_MODIFIER = {
    1: 1.0,
    2: 0.5,
    3: 0.0,
    4: -0.5,
    5: -1.0
}

def get_all_players():
    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    response = requests.get(url)
    data = response.json()

    elements = data['elements']
    teams = {team['id']: team['name'] for team in data['teams']}

    players = []
    for p in elements:
        team_name = teams.get(p['team'], "Unknown")
        players.append({
            "id": p['id'],
            "web_name": p['web_name'],
            "now_cost": p['now_cost'],
            "total_points": p['total_points'],
            "minutes": p['minutes'],
            "form": float(p['form']),
            "element_type": p['element_type'],
            "team_name": team_name,
            "fixture_difficulty": 5,  # Placeholder
            "smart_score": round((p['total_points'] / p['now_cost']) * float(p['form']), 2) if p['now_cost'] else 0,
            "value": round(p['total_points'] / p['now_cost'], 2) if p['now_cost'] else 0
        })

    return players

def fetch_data():
    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    return requests.get(url).json()

def fetch_fixtures():
    url = "https://fantasy.premierleague.com/api/fixtures/"
    return requests.get(url).json()

def enrich_players(players, teams):
    team_lookup = {t['id']: t['name'] for t in teams}
    for p in players:
        p['team_name'] = team_lookup.get(p['team'], "Unknown")
    return players

def get_upcoming_fixtures(team_id, fixtures, team_lookup, limit=3):
    team_fixtures = []
    for f in fixtures:
        if not f['finished'] and (f['team_h'] == team_id or f['team_a'] == team_id):
            is_home = f['team_h'] == team_id
            opponent_id = f['team_a'] if is_home else f['team_h']
            opponent = team_lookup.get(opponent_id, "Unknown")
            difficulty = f['team_h_difficulty'] if is_home else f['team_a_difficulty']
            team_fixtures.append((opponent, difficulty))
            if len(team_fixtures) >= limit:
                break
    return team_fixtures

def calculate_smart_score(p, fixtures, team_lookup):
    try:
        form = float(p['form']) if p['form'] else 0
        cost = p['now_cost'] / 10
        total_points = p['total_points'] or 0
        chance = p.get('chance_of_playing_next_round') or 100
        ppm = total_points / cost if cost > 0 else 0

        upcoming = get_upcoming_fixtures(p['team'], fixtures, team_lookup)
        difficulty_mod = sum(FIXTURE_DIFFICULTY_MODIFIER.get(d[1], 0.0) for d in upcoming)
        fixture_str = ', '.join([f"vs {d[0]} (D{d[1]})" for d in upcoming])
        p['fixture_info'] = fixture_str if fixture_str else "No upcoming fixtures"

        base_score = (form * 2.5) + (ppm * 1.5) + (chance / 100) - (cost * 0.4)
        base_score += difficulty_mod

        pos_mult = POSITION_WEIGHT.get(p['element_type'], 1.0)
        score = base_score * pos_mult
        return round(score, 2)
    except:
        return 0

def get_top_picks_by_position(position_label):
    data = fetch_data()
    fixtures = fetch_fixtures()
    team_lookup = {t['id']: t['name'] for t in data['teams']}

    matches = [k for k, v in POSITION_MAP.items() if v.lower() == position_label.lower()]
    if not matches:
        raise ValueError(f"Invalid position label: '{position_label}' – must be one of {list(POSITION_MAP.values())}")
    position_code = matches[0]

    players = [p for p in data['elements'] if p['element_type'] == position_code]
    players = enrich_players(players, data['teams'])

    for p in players:
        p['smart_score'] = calculate_smart_score(p, fixtures, team_lookup)

    return sorted(players, key=lambda x: x['smart_score'], reverse=True)[:3]

def get_top_raw_player_by_position(position_label):
    data = fetch_data()
    position_code = [k for k, v in POSITION_MAP.items() if v == position_label][0]
    players = [p for p in data['elements'] if p['element_type'] == position_code]
    players = enrich_players(players, data['teams'])

    return max(players, key=lambda x: x['total_points'] if x['total_points'] is not None else 0)

def get_captain_picks(players=None):
    data = fetch_data()
    fixtures = fetch_fixtures()
    team_lookup = {t['id']: t['name'] for t in data['teams']}

    if players is None:
        players = [p for p in data['elements'] if p['element_type'] in [1, 2, 3, 4]]
        players = enrich_players(players, data['teams'])

    for p in players:
        p['smart_score'] = calculate_smart_score(p, fixtures, team_lookup)

    return sorted(players, key=lambda x: x['smart_score'], reverse=True)[:3]
    data = fetch_data()
    fixtures = fetch_fixtures()
    team_lookup = {t['id']: t['name'] for t in data['teams']}
    players = [p for p in data['elements'] if p['element_type'] in [1, 2, 3, 4]]
    players = enrich_players(players, data['teams'])

    for p in players:
        p['smart_score'] = calculate_smart_score(p, fixtures, team_lookup)

    return sorted(players, key=lambda x: x['smart_score'], reverse=True)[:3]

def get_top_managers():
    data = fetch_data()
    fixtures = fetch_fixtures()
    team_lookup = {t['id']: t['name'] for t in data['teams']}
    managers = [p for p in data['elements'] if p['element_type'] not in [1, 2, 3, 4]]
    managers = enrich_players(managers, data['teams'])

    for m in managers:
        m['smart_score'] = calculate_smart_score(m, fixtures, team_lookup)

    return sorted(managers, key=lambda x: x['smart_score'], reverse=True)[:3]
