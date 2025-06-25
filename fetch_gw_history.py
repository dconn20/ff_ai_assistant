# fetch_gw_history.py
import requests
import pandas as pd
import time


# Difficulty ratings (adjust or fetch from official FDR endpoint)
team_difficulty = {
    1: 3,  # Arsenal
    2: 2,  # Aston Villa
    3: 3,  # Bournemouth
    4: 5,  # Brentford
    5: 4,  # Brighton
    6: 4,  # Burnley
    7: 2,  # Chelsea
    8: 3,  # Crystal Palace
    9: 1,  # Everton
    10: 4, # Fulham
    11: 1, # Liverpool
    12: 2, # Luton
    13: 1, # Man City
    14: 1, # Man Utd
    15: 3, # Newcastle
    16: 4, # Nott'm Forest
    17: 5, # Sheffield Utd
    18: 4, # Spurs
    19: 2, # West Ham
    20: 3  # Wolves
}


def fetch_bootstrap():
    base_url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    res = requests.get(base_url)
    res.raise_for_status()
    return res.json()["elements"]

def fetch_player_history(player_id):
    url = f"https://fantasy.premierleague.com/api/element-summary/{player_id}/"
    res = requests.get(url)
    if res.status_code == 200:
        return res.json()["history"]
    return []

# def build_gw_dataset():
#     all_players = fetch_bootstrap()
#     records = []

#     for player in all_players:
#         player_id = player["id"]
#         web_name = player["web_name"]
#         team = player["team"]
#         try:
#             history = fetch_player_history(player_id)
#             for match in history:
#                 records.append({
#                     "player_id": player_id,
#                     "web_name": web_name,
#                     "team": team,
#                     "gw": match["round"],
#                     "minutes": match["minutes"],
#                     "goals_scored": match["goals_scored"],
#                     "assists": match["assists"],
#                     "clean_sheets": match["clean_sheets"],
#                     "ict_index": float(match["ict_index"]),
#                     "influence": float(match["influence"]),
#                     "creativity": float(match["creativity"]),
#                     "threat": float(match["threat"]),
#                     "opponent_team": match["opponent_team"],
#                     "was_home": match["was_home"],
#                     "total_points": match["total_points"]
#                 })
#         except Exception as e:
#             print(f"Error for player {web_name}: {e}")
#         time.sleep(0.2)  # Be kind to the API

#     df = pd.DataFrame(records)
#     df.to_csv("fpl_gw_history.csv", index=False)
#     print(f"Saved {len(df)} rows of match data.")

def build_gw_dataset():
    all_players = fetch_bootstrap()
    records = []

    # Difficulty scores – adjust if needed
    team_difficulty = {
        1: 3, 2: 2, 3: 3, 4: 5, 5: 4,
        6: 4, 7: 2, 8: 3, 9: 1, 10: 4,
        11: 1, 12: 2, 13: 1, 14: 1, 15: 3,
        16: 4, 17: 5, 18: 4, 19: 2, 20: 3
    }

    from collections import defaultdict
    player_gw_history = defaultdict(list)

    for player in all_players:
        player_id = player["id"]
        web_name = player["web_name"]
        team = player["team"]

        try:
            history = fetch_player_history(player_id)
            history_sorted = sorted(history, key=lambda x: x["round"])  # sort by GW

            for i, match in enumerate(history_sorted):
                gw = match["round"]
                total_points = match["total_points"]

                # FORM: avg last 3 gameweeks
                prev_points = [g["total_points"] for g in history_sorted[max(0, i-3):i]]
                form = sum(prev_points) / len(prev_points) if prev_points else 0

                # FIXTURE DIFFICULTY
                opponent_team = match["opponent_team"]
                was_home = match["was_home"]
                raw_difficulty = team_difficulty.get(opponent_team, 3)
                difficulty = raw_difficulty - 0.5 if was_home else raw_difficulty + 0.5

                records.append({
                    "player_id": player_id,
                    "web_name": web_name,
                    "team": team,
                    "gw": gw,
                    "minutes": match["minutes"],
                    "goals_scored": match["goals_scored"],
                    "assists": match["assists"],
                    "clean_sheets": match["clean_sheets"],
                    "ict_index": float(match["ict_index"]),
                    "influence": float(match["influence"]),
                    "creativity": float(match["creativity"]),
                    "threat": float(match["threat"]),
                    "opponent_team": opponent_team,
                    "was_home": was_home,
                    "fixture_difficulty": difficulty,
                    "form": form,
                    "total_points": total_points
                })
        except Exception as e:
            print(f"Error with player {web_name}: {e}")
        time.sleep(0.2)  # to avoid API rate limits

    df = pd.DataFrame(records)
    df.to_csv("fpl_gw_enriched.csv", index=False)
    print(f"Saved {len(df)} rows of enriched match data.")


if __name__ == "__main__":
    build_gw_dataset()
