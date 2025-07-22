
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import joblib

# Load the enriched dataset
df = pd.read_csv("fpl_gw_combined_all_seasons_enriched_ready.csv")

# Define the target variable
target = "total_points"

# Features to use
features = [
    "minutes", "goals_scored", "assists", "clean_sheets", "ict_index",
    "influence", "creativity", "threat", "fixture_difficulty", "form",
    "opponent_strength", "team_form", "price", "transfers_in_gw",
    "transfers_out_gw", "yellow_cards", "red_cards", "bonus"
]

# Drop rows with missing data in selected features
df = df.dropna(subset=features + [target])

# Split data
X = df[features]
y = df[target]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train LightGBM model
model = lgb.LGBMRegressor(n_estimators=200, learning_rate=0.05, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
print(f"Validation MAE: {mae:.2f}")

# Save the model
joblib.dump(model, "gw_score_model_lightgbm.pkl")
print("✅ Model saved as gw_score_model_lightgbm.pkl")
