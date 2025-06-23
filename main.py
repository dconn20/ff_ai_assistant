# main.py
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI()
model = joblib.load('player_score_model.pkl')

class PlayerStats(BaseModel):
    minutes: int
    goals_scored: int
    assists: int
    clean_sheets: int

@app.post("/predict")
def predict_score(player: PlayerStats):
    df = pd.DataFrame([player.dict()])
    prediction = model.predict(df)[0]
    return {"predicted_points": round(prediction, 2)}
