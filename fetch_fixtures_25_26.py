import requests
import pandas as pd

# URLs
fixture_url = "https://fantasy.premierleague.com/api/fixtures/"
bootstrap_url = "https://fantasy.premierleague.com/api/bootstrap-static/"

# Fetch live data
fixtures = requests.get(fixture_url).json()
bootstrap = requests.get(bootstrap_url).json()

# Map team IDs to names
team_id_map = {team["id"]: team["name"] for team in bootstrap["teams"]}

# Prepare fixtures
fixture_df = pd.DataFrame(fixtures)
fixture_df = fixture_df[fixture_df["kickoff_time"].notnull()]
fixture_df["kickoff_time"] = pd.to_datetime(fixture_df["kickoff_time"])
fixture_df = fixture_df[fixture_df["kickoff_time"] > pd.Timestamp.now()]

fixture_df["home_team"] = fixture_df["team_h"].map(team_id_map)
fixture_df["away_team"] = fixture_df["team_a"].map(team_id_map)
fixture_df["gw"] = fixture_df["event"]

# Save to CSV for later use in your app
fixture_df.to_csv("future_fixtures_25_26.csv", index=False)
print("✅ Fixtures saved as future_fixtures_25_26.csv")
