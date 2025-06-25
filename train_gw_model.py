# # train_gw_model.py
# import pandas as pd
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.model_selection import train_test_split
# import joblib

# df = pd.read_csv("fpl_gw_history.csv")
# df = df[df["minutes"] > 0]  # Filter non-playing GWs

# features = [
#     "minutes", "goals_scored", "assists", "clean_sheets",
#     "ict_index", "influence", "creativity", "threat"
# ]
# target = "total_points"

# X = df[features]
# y = df[target]

# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# model = RandomForestRegressor(n_estimators=200, max_depth=10)
# model.fit(X_train, y_train)

# joblib.dump(model, "gw_score_model.pkl")
# print("Trained and saved GW model.")


import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib

# Load the enriched dataset
df = pd.read_csv("fpl_gw_enriched.csv")

# Filter out players who didn’t play
df = df[df["minutes"] > 0]

# Define input features and target
features = [
    "minutes", "goals_scored", "assists", "clean_sheets",
    "ict_index", "influence", "creativity", "threat",
    "form", "fixture_difficulty"
]
target = "total_points"

X = df[features]
y = df[target]

# Split into training and testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
model.fit(X_train, y_train)

# Save the trained model
joblib.dump(model, "gw_score_model.pkl")
print("✅ Model trained and saved as gw_score_model.pkl")
