import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
import matplotlib.pyplot as plt
import joblib

# Load enriched dataset
df = pd.read_csv("fpl_gw_combined_all_seasons_enriched.csv")

# Drop any rows with missing values
df.dropna(inplace=True)

# Filter out players who didn’t play
df = df[df["minutes"] > 0]

# Features including new ones
features = [
    "minutes", "goals_scored", "assists", "clean_sheets",
    "ict_index", "influence", "creativity", "threat",
    "form", "fixture_difficulty", "opponent_strength", "team_form",
    "price", "transfers_in_gw", "transfers_out_gw",
    "yellow_cards", "red_cards", "bonus"
]

target = "total_points"
X = df[features]
y = df[target]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestRegressor(n_estimators=300, max_depth=12, random_state=42)
model.fit(X_train, y_train)

# Save the model
joblib.dump(model, "gw_score_model.pkl")
print("✅ Model trained and saved as gw_score_model.pkl")

# Evaluation
y_pred = model.predict(X_test)
r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
print(f"📊 R² score: {r2:.4f}")
print(f"📉 Mean Absolute Error (MAE): {mae:.2f}")

# Feature importance plot
importances = model.feature_importances_
feature_importance_df = pd.DataFrame({
    "Feature": features,
    "Importance": importances
}).sort_values(by="Importance", ascending=False)

plt.figure(figsize=(10, 6))
plt.barh(feature_importance_df["Feature"], feature_importance_df["Importance"])
plt.gca().invert_yaxis()
plt.title("Feature Importance")
plt.tight_layout()
plt.show()

# Training performance chart
plt.figure(figsize=(6, 4))
plt.scatter(y_test, y_pred, alpha=0.4)
plt.plot([y.min(), y.max()], [y.min(), y.max()], "r--")
plt.xlabel("Actual Points")
plt.ylabel("Predicted Points")
plt.title("Actual vs Predicted Points")
plt.tight_layout()
plt.show()
