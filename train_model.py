# train_model.py
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib

# Example dataset – replace with your FPL stats
data = pd.DataFrame({
    'minutes': [90, 75, 60, 45, 90],
    'goals_scored': [1, 0, 0, 0, 2],
    'assists': [0, 1, 0, 1, 0],
    'clean_sheets': [1, 0, 0, 0, 1],
    'points_next_gw': [10, 5, 2, 3, 12]  # Target
})

X = data.drop('points_next_gw', axis=1)
y = data['points_next_gw']

model = RandomForestRegressor()
model.fit(X, y)

joblib.dump(model, 'player_score_model.pkl')
print("Model saved.")
