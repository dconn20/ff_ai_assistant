
import random

# Placeholder AI-based captain recommendation logic
def recommend_captain_ai(players):
    # Assume each player has smart_score, fixture_difficulty, form, and value
    # Score = smart_score * 0.5 + (10 - fixture_difficulty) * 0.3 + form * 0.2
    recommendations = []
    for p in players:
        score = (
            p.get('smart_score', 0) * 0.5 +
            (10 - p.get('fixture_difficulty', 5)) * 0.3 +
            p.get('form', 0) * 0.2
        )
        p['ai_score'] = round(score, 2)
        recommendations.append(p)
    recommendations.sort(key=lambda x: x['ai_score'], reverse=True)
    return recommendations[:3]
