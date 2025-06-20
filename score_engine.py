# Placeholder for future scoring models or ML integration
def calculate_score(player):
    form = float(player['form']) if player['form'] else 0
    cost = player['now_cost'] / 10
    chance = player.get('chance_of_playing_next_round') or 100
    return (form * 2) + (chance / 100) - (cost * 0.5)
