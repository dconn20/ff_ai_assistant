# train_model.py
# import pandas as pd
# from sklearn.ensemble import RandomForestRegressor
# import joblib

# # Example dataset – replace with your FPL stats
# data = pd.DataFrame({
#     'minutes': [90, 75, 60, 45, 90],
#     'goals_scored': [1, 0, 0, 0, 2],
#     'assists': [0, 1, 0, 1, 0],
#     'clean_sheets': [1, 0, 0, 0, 1],
#     'points_next_gw': [10, 5, 2, 3, 12]  # Target
# })

# X = data.drop('points_next_gw', axis=1)
# y = data['points_next_gw']

# model = RandomForestRegressor()
# model.fit(X, y)

# joblib.dump(model, 'player_score_model.pkl')
# print("Model saved.")

# train_model.py
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib

df = pd.read_csv("fpl_player_data.csv")

# Drop players who haven't played
df = df[df["minutes"] > 0]

features = [
    'minutes', 'goals_scored', 'assists', 'clean_sheets',
    'form', 'ict_index', 'influence', 'creativity', 'threat',
    'now_cost'
]
target = 'total_points'

X = df[features]
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RandomForestRegressor()
model.fit(X_train, y_train)

joblib.dump(model, "player_score_model.pkl")
print("Trained and saved model.")
