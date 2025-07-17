import pandas as pd
from sklearn.linear_model import Ridge
import joblib

# Load the cleaned CSV
df = pd.read_csv("fpl_gw_cleaned.csv")

# Print available columns to debug
print("Available columns:", df.columns.tolist())

# Define fallback features only using what's present
available_features = [
    "minutes", "goals_scored", "assists", "clean_sheets",
    "ict_index", "influence", "creativity", "threat", "form"
]
available_features = [f for f in available_features if f in df.columns]

# Target
target = "total_points"

# Prepare input and target
X = df[available_features]
y = df[target]

# Train model
model = Ridge(alpha=1.0)
model.fit(X, y)

# Print model score
score = model.score(X, y)
print(f"✅ Model trained and saved as gw_score_model.pkl")
print(f"📊 R² Score on training data: {score:.4f}")


# Save model
joblib.dump(model, "gw_score_model.pkl")
print("✅ Model trained and saved as gw_score_model.pkl")
