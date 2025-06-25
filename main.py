# main.py
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI()
model = joblib.load('gw_score_model.pkl')

class PlayerStats(BaseModel):
    minutes: int
    goals_scored: int
    assists: int
    clean_sheets: int
    ict_index: float
    influence: float
    creativity: float
    threat: float
    form: float
    fixture_difficulty: float

@app.post("/predict")
def predict_score(player: PlayerStats):
    df = pd.DataFrame([player.dict()])
    prediction = model.predict(df)[0]
    return {"predicted_points": round(prediction, 2)}
