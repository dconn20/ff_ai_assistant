import requests
from collections import defaultdict
import pandas as pd
import numpy as np
import joblib


model = joblib.load("gw_score_model.pkl")

POSITION_MAP = {
    1: "Goalkeeper",
    2: "Defender",
    3: "Midfielder",
    4: "Forward"
}

FIXTURE_DIFFICULTY_MODIFIER = {
    1: 1.0,
    2: 0.5,
    3: 0.0,
    4: -0.5,
    5: -1.0
}

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

def get_all_players():
    data = fetch_data()
    players = enrich_players(data['elements'], data['teams'])
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
        form = float(p.get('form', 0))
        cost = p['now_cost'] / 10
        total_points = p.get('total_points', 0)
        chance = p.get('chance_of_playing_next_round', 100)
        ppm = total_points / cost if cost > 0 else 0

        upcoming = get_upcoming_fixtures(p['team'], fixtures, team_lookup)
        difficulty_mod = sum(FIXTURE_DIFFICULTY_MODIFIER.get(d[1], 0.0) for d in upcoming)
        p['fixture_info'] = ', '.join([f"vs {d[0]} (D{d[1]})" for d in upcoming]) or "N/A"

        base_score = (form * 2.5) + (ppm * 1.5) + (chance / 100) - (cost * 0.4) + difficulty_mod
        return round(base_score, 2)
    except:
        return 0

# def get_top_picks_by_position(position_label, top_n=5):
#     position_code = [k for k, v in POSITION_MAP.items() if v.lower() == position_label.lower()]
#     if not position_code:
#         return []

#     code = position_code[0]
#     data = fetch_data()
#     fixtures = fetch_fixtures()
#     team_lookup = {t['id']: t['name'] for t in data['teams']}
#     players = [p for p in data['elements'] if p['element_type'] == code]
#     players = enrich_players(players, data['teams'])

#     for p in players:
#         p['smart_score'] = calculate_smart_score(p, fixtures, team_lookup)

#     return sorted(players, key=lambda x: x['smart_score'], reverse=True)[:top_n]


def get_top_picks_by_position(position_label, top_n=5):
    position_code = [k for k, v in POSITION_MAP.items() if v.lower() == position_label.lower()]
    if not position_code:
        return []

    code = position_code[0]
    data = fetch_data()
    fixtures = fetch_fixtures()
    team_lookup = {t['id']: t['name'] for t in data['teams']}
    players = [p for p in data['elements'] if p['element_type'] == code]
    players = enrich_players(players, data['teams'])

    filtered_players = []

    for p in players:
        minutes = p.get("minutes", 0)

        # ✅ Only include players with at least 270 minutes (3 full games)
        if minutes < 270:
            continue

        try:
            # Build input for prediction
            player_input = {
                "minutes": minutes,
                "goals_scored": p.get("goals_scored", 0),
                "assists": p.get("assists", 0),
                "clean_sheets": p.get("clean_sheets", 0),
                "ict_index": float(p.get("ict_index", 0)),
                "influence": float(p.get("influence", 0)),
                "creativity": float(p.get("creativity", 0)),
                "threat": float(p.get("threat", 0)),
                "form": float(p.get("form", 0)),
                "fixture_difficulty": 3,  # Placeholder for now
                "opponent_strength": 3,  # Placeholder
                "team_form": 3,          # Placeholder
                "price": p.get("now_cost", 0) / 10,
                "transfers_in_gw": p.get("transfers_in_event", 0),
                "transfers_out_gw": p.get("transfers_out_event", 0),
                "yellow_cards": p.get("yellow_cards", 0),
                "red_cards": p.get("red_cards", 0),
                "bonus": p.get("bonus", 0)
            }

            # 👇 Use your model
            predicted_score = get_prediction(player_input)

            # Add prediction info to player
            p["predicted_points"] = predicted_score
            p["predicted_points_per_90"] = (predicted_score * 90) / minutes
            filtered_players.append(p)

        except Exception as e:
            # 🛠️ Log the error
            print(f"❌ Prediction failed for {p.get('web_name', 'Unknown')}: {e}")
            continue



    return sorted(filtered_players, key=lambda x: x["predicted_points_per_90"], reverse=True)[:top_n]


def get_captain_picks(top_n=3):
    data = fetch_data()
    fixtures = fetch_fixtures()
    team_lookup = {t['id']: t['name'] for t in data['teams']}
    players = [p for p in data['elements'] if p['element_type'] in POSITION_MAP]
    players = enrich_players(players, data['teams'])

    for p in players:
        p['smart_score'] = calculate_smart_score(p, fixtures, team_lookup)

    return sorted(players, key=lambda x: x['smart_score'], reverse=True)[:top_n]

def get_top_raw_player_by_position(position_label, players=None):
    code = [k for k, v in POSITION_MAP.items() if v.lower() == position_label.lower()]
    if not code:
        return []
    code = code[0]
    if not players:
        players = get_all_players()
    top_players = [p for p in players if p['element_type'] == code]
    return sorted(top_players, key=lambda x: x.get('total_points', 0), reverse=True)[:3]

def get_top_managers():
    data = fetch_data()
    elements = data["elements"]
    teams = data["teams"]
    team_points = defaultdict(int)
    for player in elements:
        team_points[player["team"]] += player.get("total_points", 0)
    top_teams = sorted(team_points.items(), key=lambda x: x[1], reverse=True)[:3]
    return [{"manager_name": next(t["name"] for t in teams if t["id"] == tid), "points": pts} for tid, pts in top_teams]


# AI
# def get_prediction(player_stats):
#     url = "http://localhost:8000/predict"
#     response = requests.post(url, json=player_stats)
#     return response.json().get("predicted_points")

# def get_prediction(player_stats):
#     url = "http://localhost:8000/predict"  # Ensure FastAPI server is running
#     response = requests.post(url, json=player_stats)
#     if response.status_code == 200:
#         return response.json().get("predicted_points")
#     else:
#         raise Exception(f"API Error {response.status_code}: {response.text}")

def get_prediction(player_features: dict) -> float:

    # Ensure required features are present
    expected_features = [
        "minutes", "goals_scored", "assists", "clean_sheets",
        "ict_index", "influence", "creativity", "threat",
        "form", "fixture_difficulty", "opponent_strength", "team_form",
        "price", "transfers_in_gw", "transfers_out_gw",
        "yellow_cards", "red_cards", "bonus"
    ]

    # Fill missing with 0s if any
    input_data = {f: player_features.get(f, 0) for f in expected_features}

    df = pd.DataFrame([input_data])
    prediction = model.predict(df)[0]
    return prediction
