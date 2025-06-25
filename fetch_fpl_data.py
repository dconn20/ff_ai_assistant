# fetch_fpl_data.py
import requests
import pandas as pd

def fetch_player_data():
    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    res = requests.get(url)
    res.raise_for_status()

    data = res.json()
    players = data["elements"]
    df = pd.DataFrame(players)

    # Keep only useful columns (customize this)
    columns = [
        'first_name', 'second_name', 'web_name', 'team', 'minutes',
        'goals_scored', 'assists', 'clean_sheets', 'total_points',
        'form', 'ict_index', 'influence', 'creativity', 'threat',
        'now_cost', 'selected_by_percent'
    ]
    df = df[columns]
    
    # Save locally
    df.to_csv("fpl_player_data.csv", index=False)
    print(f"Fetched and saved {len(df)} players.")

if __name__ == "__main__":
    fetch_player_data()
