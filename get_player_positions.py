import requests
import pandas as pd

# Step 1: Download data from the FPL API
bootstrap_url = "https://fantasy.premierleague.com/api/bootstrap-static/"
response = requests.get(bootstrap_url)
data = response.json()

# Step 2: Extract player info and map element_type to position
players_df = pd.DataFrame(data["elements"])
position_map = {
    1: "GK",
    2: "DEF",
    3: "MID",
    4: "FWD"
}

# Step 3: Build position DataFrame
position_df = players_df[["id", "element_type"]].rename(columns={"id": "player_id"})
position_df["position"] = position_df["element_type"].map(position_map)
position_df.drop(columns=["element_type"], inplace=True)

# Step 4: Save to CSV
position_df.to_csv("fpl_player_positions.csv", index=False)
print("✅ Player positions saved to fpl_player_positions.csv")
