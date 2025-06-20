
# def get_best_xi_by_formation(players, budget=1000):
#     import itertools

#     formations = [
#         {"DEF": 3, "MID": 4, "FWD": 3},
#         {"DEF": 3, "MID": 5, "FWD": 2},
#         {"DEF": 4, "MID": 4, "FWD": 2},
#         {"DEF": 4, "MID": 3, "FWD": 3},
#         {"DEF": 5, "MID": 3, "FWD": 2},
#         {"DEF": 5, "MID": 4, "FWD": 1},
#     ]

#     GKs = [p for p in players if p["element_type"] == 1]
#     DEFs = [p for p in players if p["element_type"] == 2]
#     MIDs = [p for p in players if p["element_type"] == 3]
#     FWDs = [p for p in players if p["element_type"] == 4]

#     best_team = []
#     best_score = 0
#     best_formation = ""

#     for f in formations:
#         for gk in sorted(GKs, key=lambda x: -x["smart_score"])[:2]:
#             team = [gk]
#             cost = gk["now_cost"]
#             score = gk["smart_score"]
#             def_sel = sorted(DEFs, key=lambda x: -x["smart_score"])[:f["DEF"]]
#             mid_sel = sorted(MIDs, key=lambda x: -x["smart_score"])[:f["MID"]]
#             fwd_sel = sorted(FWDs, key=lambda x: -x["smart_score"])[:f["FWD"]]
#             team += def_sel + mid_sel + fwd_sel
#             cost += sum(p["now_cost"] for p in def_sel + mid_sel + fwd_sel)
#             score += sum(p["smart_score"] for p in def_sel + mid_sel + fwd_sel)

#             if len(team) == 1 + f["DEF"] + f["MID"] + f["FWD"] and cost <= budget:
#                 if score > best_score:
#                     best_team = team
#                     best_score = score
#                     best_formation = f"1-{f['DEF']}-{f['MID']}-{f['FWD']}"

#     if not best_team:
#         return [], "No valid squad within budget", []

#     subs = []
#     used_ids = {p["id"] for p in best_team}
#     gk_sub = next((p for p in sorted(GKs, key=lambda x: -x["smart_score"]) if p["id"] not in used_ids), None)
#     def_sub = next((p for p in sorted(DEFs + MIDs, key=lambda x: -x["smart_score"]) if p["id"] not in used_ids), None)
#     mid_sub = next((p for p in sorted(DEFs + MIDs, key=lambda x: -x["smart_score"]) if p["id"] not in used_ids and p != def_sub), None)
#     fwd_sub = next((p for p in sorted(FWDs, key=lambda x: -x["smart_score"]) if p["id"] not in used_ids), None)

#     for sub in [gk_sub, def_sub, mid_sub, fwd_sub]:
#         if sub:
#             subs.append(sub)

#     return best_team, best_formation, subs



def get_best_xi_by_formation(players, budget):
    # Simple logic to return best XI by score
    sorted_players = sorted(players, key=lambda x: x.get("smart_score", 0), reverse=True)
    xi = []
    cost = 0
    positions = {1: 0, 2: 0, 3: 0, 4: 0}
    for p in sorted_players:
        pos = p["element_type"]
        if len(xi) >= 11:
            break
        if cost + p["now_cost"] <= budget:
            xi.append(p)
            positions[pos] += 1
            cost += p["now_cost"]
    return xi, "4-4-2", []
