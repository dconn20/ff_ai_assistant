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

#     filtered_players = []

#     for p in players:
#         minutes = p.get("minutes", 0)

#         # ✅ Only include players with at least 270 minutes (3 full games)
#         if minutes < 270:
#             continue

#         try:
#             # Build input for prediction
#             player_input = {
#                 "minutes": minutes,
#                 "goals_scored": p.get("goals_scored", 0),
#                 "assists": p.get("assists", 0),
#                 "clean_sheets": p.get("clean_sheets", 0),
#                 "ict_index": float(p.get("ict_index", 0)),
#                 "influence": float(p.get("influence", 0)),
#                 "creativity": float(p.get("creativity", 0)),
#                 "threat": float(p.get("threat", 0)),
#                 "form": float(p.get("form", 0)),
#                 "fixture_difficulty": 3,  # Placeholder for now
#                 "opponent_strength": 3,  # Placeholder
#                 "team_form": 3,          # Placeholder
#                 "price": p.get("now_cost", 0) / 10,
#                 "transfers_in_gw": p.get("transfers_in_event", 0),
#                 "transfers_out_gw": p.get("transfers_out_event", 0),
#                 "yellow_cards": p.get("yellow_cards", 0),
#                 "red_cards": p.get("red_cards", 0),
#                 "bonus": p.get("bonus", 0)
#             }

#             # 👇 Use your model
#             predicted_score = get_prediction(player_input)

#             # Add prediction info to player
#             p["predicted_points"] = predicted_score
#             p["predicted_points_per_90"] = (predicted_score * 90) / minutes
#             filtered_players.append(p)

#         except Exception as e:
#             # 🛠️ Log the error
#             print(f"❌ Prediction failed for {p.get('web_name', 'Unknown')}: {e}")
#             continue



#     return sorted(filtered_players, key=lambda x: x["predicted_points_per_90"], reverse=True)[:top_n]

def enrich_player_with_prediction(player, fixtures, team_lookup):
    try:
        minutes = player.get("minutes", 0)
        if minutes < 270:  # Require 3+ full matches for validity
            return None

        upcoming_fixtures = get_upcoming_fixtures(player["team"], fixtures, team_lookup, limit=3)

        fixture_difficulty = np.mean([f[1] for f in upcoming_fixtures]) if upcoming_fixtures else 3
        opponent_strength = upcoming_fixtures[0][1] if upcoming_fixtures else 3

        player_input = {
            "minutes": minutes,
            "goals_scored": player.get("goals_scored", 0),
            "assists": player.get("assists", 0),
            "clean_sheets": player.get("clean_sheets", 0),
            "ict_index": player.get("ict_index", 0.0),
            "influence": player.get("influence", 0.0),
            "creativity": player.get("creativity", 0.0),
            "threat": player.get("threat", 0.0),
            "form": float(player.get("form", 0.0)),
            "fixture_difficulty": fixture_difficulty,
            "opponent_strength": opponent_strength,
            "team_form": float(player.get("form", 0.0)),  # Placeholder
            "price": player.get("now_cost", 0) / 10.0,
            "transfers_in_gw": player.get("transfers_in_event", 0),
            "transfers_out_gw": player.get("transfers_out_event", 0),
            "yellow_cards": player.get("yellow_cards", 0),
            "red_cards": player.get("red_cards", 0),
            "bonus": player.get("bonus", 0)
        }

        predicted_score = get_prediction(player_input)
        player["predicted_points"] = predicted_score
        player["predicted_points_per_90"] = round((predicted_score * 90) / minutes, 2)

        player["fixture_info"] = ', '.join([f"vs {f[0]} (D{f[1]})" for f in upcoming_fixtures]) or "N/A"

        return player
    except Exception as e:
        print(f"⚠️ Prediction failed for {player.get('web_name')}: {e}")
        return None


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
        print(f"{p['web_name']}: Predicted Points = {p.get('predicted_points')}, Per 90 = {p.get('predicted_points_per_90')}, Minutes = {p.get('minutes')}")
        enriched = enrich_player_with_prediction(p, fixtures, team_lookup)
        if enriched:
            filtered_players.append(enriched)


    # filtered_players = []
    # for p in players:
    #     minutes = p.get("minutes", 0)

    #     # Skip low-minute players entirely
    #     if minutes < 270:
    #         continue

    #     try:
    #         player_input = {
    #             "minutes": minutes,
    #             "goals_scored": p.get("goals_scored", 0),
    #             "assists": p.get("assists", 0),
    #             "clean_sheets": p.get("clean_sheets", 0),
    #             "ict_index": float(p.get("ict_index") or 0),
    #             "influence": float(p.get("influence") or 0),
    #             "creativity": float(p.get("creativity") or 0),
    #             "threat": float(p.get("threat") or 0),
    #             "form": float(p.get("form") or 0),
    #             "fixture_difficulty": 3,
    #             "opponent_strength": 3,
    #             "team_form": 3,
    #             "price": p.get("now_cost", 0) / 10,
    #             "transfers_in_gw": p.get("transfers_in_event", 0),
    #             "transfers_out_gw": p.get("transfers_out_event", 0),
    #             "yellow_cards": p.get("yellow_cards", 0),
    #             "red_cards": p.get("red_cards", 0),
    #             "bonus": p.get("bonus", 0)
    #         }

    #         predicted_score = get_prediction(player_input)

    #         # Optional: weight the score
    #         weighted_score = (
    #             predicted_score * 1.5 +
    #             float(p.get("form", 0)) * 1.2 +
    #             float(p.get("total_points", 0)) * 0.8
    #         )

    #         p["predicted_points"] = round(predicted_score, 2)
    #         p["weighted_score"] = round(weighted_score, 2)
    #         filtered_players.append(p)

    #         # 🔍 Debug top 3 predictions
    #         for p in sorted(filtered_players, key=lambda x: x["weighted_score"], reverse=True)[:3]:
    #             print(f"{p.get('web_name')} | Minutes: {p.get('minutes')} | Predicted: {p.get('predicted_points')} | Weighted: {p.get('weighted_score')}")


    #     except Exception as e:
    #         print(f"❌ Error predicting for {p.get('web_name', 'unknown')}: {e}")
    #         continue

    # return sorted(filtered_players, key=lambda x: x["weighted_score"], reverse=True)[:top_n]
    # return sorted(filtered_players, key=lambda x: x.get("predicted_points_per_90", 0), reverse=True)[:top_n]
    # return sorted(filtered_players, key=lambda x: x.get("predicted_points", 0), reverse=True)[:top_n]
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

# def get_prediction(player_features: dict) -> float:

#     # Ensure required features are present
#     expected_features = [
#         "minutes", "goals_scored", "assists", "clean_sheets",
#         "ict_index", "influence", "creativity", "threat",
#         "form", "fixture_difficulty", "opponent_strength", "team_form",
#         "price", "transfers_in_gw", "transfers_out_gw",
#         "yellow_cards", "red_cards", "bonus"
#     ]

#     # Fill missing with 0s if any
#     input_data = {f: player_features.get(f, 0) for f in expected_features}

#     df = pd.DataFrame([input_data])
#     prediction = model.predict(df)[0]
#     return prediction

# def get_prediction(player_features: dict) -> float:
#     expected_features = [
#         "minutes", "goals_scored", "assists", "clean_sheets",
#         "ict_index", "influence", "creativity", "threat",
#         "form", "fixture_difficulty", "opponent_strength", "team_form",
#         "price", "transfers_in_gw", "transfers_out_gw",
#         "yellow_cards", "red_cards", "bonus"
#     ]

#     # Build the input with safe defaults
#     input_data = {f: player_features.get(f, 0) for f in expected_features}

#     try:
#         # Convert to DataFrame and ensure proper types
#         df = pd.DataFrame([input_data])
#         df = df.astype(float)  # Force numeric types
#         prediction = model.predict(df)[0]
#         return prediction
#     except Exception as e:
#         print(f"[Prediction ERROR] Input: {input_data}")
#         print(f"[Prediction ERROR] Exception: {e}")
#         return None

# def get_prediction(player_features: dict) -> float:
#     # Features used in the trained model
#     expected_features = [
#         "minutes", "goals_scored", "assists", "clean_sheets",
#         "ict_index", "influence", "creativity", "threat",
#         "form", "fixture_difficulty", "opponent_strength", "team_form",
#         "now_cost", "transfers_in_event", "transfers_out_event",
#         "yellow_cards", "red_cards", "bonus"
#     ]

#     # Build input using real values or fallback to 0
#     input_data = {f: player_features.get(f, 0) for f in expected_features}

#     # Optional debug output
#     print("Prediction input:", input_data)

#     # Convert to DataFrame for model
#     df = pd.DataFrame([input_data])

#     try:
#         prediction = model.predict(df)[0]
#         return prediction
#     except Exception as e:
#         print(f"Prediction error: {e}")
#         return None

# def get_prediction(player_features: dict) -> float:
#     expected_features = [
#         "minutes", "goals_scored", "assists", "clean_sheets",
#         "ict_index", "influence", "creativity", "threat",
#         "form", "fixture_difficulty", "opponent_strength", "team_form",
#         "price", "transfers_in_gw", "transfers_out_gw",
#         "yellow_cards", "red_cards", "bonus"
#     ]

#     # Create a DataFrame using only expected features
#     clean_features = {key: player_features[key] for key in expected_features if key in player_features}
#     df = pd.DataFrame([clean_features])

#     return model.predict(df)[0]

def get_prediction(player_features: dict) -> float:
    expected_features = [
        "minutes", "goals_scored", "assists", "clean_sheets",
        "ict_index", "influence", "creativity", "threat",
        "form", "fixture_difficulty", "opponent_strength", "team_form",
        "price", "transfers_in_gw", "transfers_out_gw",
        "yellow_cards", "red_cards", "bonus"
    ]

    try:
        # Ensure all features exist
        input_data = {}
        for f in expected_features:
            val = player_features.get(f, 0)

            # Convert strings to float if necessary
            if isinstance(val, str):
                try:
                    val = float(val)
                except ValueError:
                    print(f"⚠️ Cannot convert feature '{f}' with value '{val}' to float")
                    val = 0

            input_data[f] = val

        df = pd.DataFrame([input_data])

        prediction = model.predict(df)[0]

        return prediction

    except Exception as e:
        print(f"Prediction error for input {player_features.get('web_name', 'Unknown')}: {e}")
        return None






