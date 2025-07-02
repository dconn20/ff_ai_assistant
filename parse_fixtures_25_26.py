import re
import pandas as pd
from datetime import datetime, timedelta

# Input/output file paths
input_file = "fixture_25_26.txt"
output_file = "parsed_fixtures_25_26.csv"

# Helper patterns
mw_pattern = re.compile(r"^MW?(\d+)")
date_pattern = re.compile(r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday) (\d{1,2}) (\w+)")
match_pattern = re.compile(r"^(\d{2}:\d{2}) (.+?) v (.+?)(?: \((.+)\))?$")

# Defaults
current_matchweek = None
current_date = None
year = 2025
month_map = {
    'August': 8, 'September': 9, 'October': 10, 'November': 11,
    'December': 12, 'January': 1, 'February': 2, 'March': 3,
    'April': 4, 'May': 5
}

# Results
fixtures = []

with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()

        # Matchweek
        mw_match = mw_pattern.match(line)
        if mw_match:
            current_matchweek = int(mw_match.group(1))
            continue

        # Date line
        date_match = date_pattern.match(line)
        if date_match:
            day = int(date_match.group(2))
            month_name = date_match.group(3)
            month = month_map[month_name]
            if month < 6:  # Jan-May are 2026
                current_date = datetime(2026, month, day)
            else:
                current_date = datetime(2025, month, day)
            continue

        # Match line
        match_match = match_pattern.match(line)
        if match_match:
            kickoff = match_match.group(1)
            home_team = match_match.group(2).strip()
            away_team = match_match.group(3).strip()
            broadcaster = match_match.group(4) if match_match.group(4) else ""

            match_date = current_date.strftime("%Y-%m-%d") if current_date else ""
            kickoff_dt = f"{match_date} {kickoff}" if current_date else ""

            fixtures.append({
                "matchweek": current_matchweek,
                "date": match_date,
                "kickoff_time": kickoff_dt,
                "home_team": home_team,
                "away_team": away_team,
                "broadcaster": broadcaster
            })

# Save to CSV
df = pd.DataFrame(fixtures)
df.to_csv(output_file, index=False)

print(f"✅ Parsed {len(df)} fixtures to {output_file}")
