# import streamlit as st
# from fpl_api import (
#     get_top_picks_by_position,
#     get_captain_picks,
#     get_top_raw_player_by_position,
#     get_top_managers,
#     get_all_players,
#     POSITION_MAP
# )
# from captain_ai import recommend_captain_ai
# from formation_logic import get_best_xi_by_formation

# st.set_page_config(page_title="FPL AI Assistant", layout="wide")
# st.sidebar.success("Login bypassed – Welcome Developer!")

# # Load all player data
# all_players = get_all_players()
# player_pool = [p for p in all_players if p.get("element_type") in [1, 2, 3, 4]]

# def format_player(p):
#     return f"**{p['web_name']}** ({p['team_name']}) – £{p['now_cost']/10}m – Score: `{p.get('smart_score', 0)}`"

# # Tab layout
# tabs = st.tabs([
#     "🏆 Top Picks",
#     "⭐ Captain Picks",
#     "🤖 AI Captain",
#     "📊 Compare Players",
#     "🧠 Your Squad",
#     "🔁 Transfer Planner",
#     "📈 Raw Leaders",
#     "🧑‍💼 Top Managers",
#     "🧮 Recommended XI"
# ])

# with tabs[0]:
#     st.header("Top 3 Picks per Position")
#     for pos in ["Goalkeeper", "Defender", "Midfielder", "Forward"]:
#         st.subheader(pos)
#         for p in get_top_picks_by_position(pos):
#             st.markdown(format_player(p))

# with tabs[1]:
#     st.header("Captain Picks")
#     picks = get_captain_picks()
#     if picks:
#         for p in picks:
#             st.markdown(f"{format_player(p)}\nFixtures: {p.get('fixture_info', 'N/A')}")
#     else:
#         st.warning("No captain picks available.")

# with tabs[2]:
#     st.header("AI-Recommended Captains")
#     picks = recommend_captain_ai(all_players)
#     if picks:
#         for p in picks:
#             st.markdown(f"{format_player(p)}\nFixtures: {p.get('fixture_info', 'N/A')}")
#     else:
#         st.warning("AI captain picks not available.")

# with tabs[3]:
#     st.header("Compare Players")
#     team_names = sorted(set(p["team_name"] for p in player_pool))
#     selected_team = st.selectbox("Select Team", team_names)
#     team_players = [p for p in player_pool if p["team_name"] == selected_team]
#     selected_player = st.selectbox("Select Player", [p["web_name"] for p in team_players])
#     for p in team_players:
#         if p["web_name"] == selected_player:
#             st.markdown(f"**Selected Player Details:**\n{format_player(p)}\nFixtures: {p.get('fixture_info', 'N/A')}")

# with tabs[4]:
#     st.header("Your Squad")
#     st.info("Login-based team import and visual formation coming soon.")

# with tabs[5]:
#     st.header("Transfer Planner")
#     st.info("Will suggest optimal transfers based on user team.")

# with tabs[6]:
#     st.header("Raw Top Scorers by Position")
#     for pos_id, label in zip([1, 2, 3, 4], ["Goalkeepers", "Defenders", "Midfielders", "Forwards"]):
#         st.subheader(label)
#         pos_label = POSITION_MAP[pos_id]
#         top_raw = get_top_raw_player_by_position(pos_label, all_players)
#         for p in top_raw[:3]:
#             st.markdown(format_player(p))

# with tabs[7]:
#     st.header("Top Managers")
#     managers = get_top_managers()
#     sorted_mgrs = sorted(managers, key=lambda m: m.get("points", 0), reverse=True)
#     for m in sorted_mgrs:
#         st.markdown(f"🏅 **{m['manager_name']}** – Total Points: `{m['points']}`")

# with tabs[8]:
#     st.header("Recommended XI (with Subs)")
#     budget = 1000
#     xi, formation, subs = get_best_xi_by_formation(player_pool, budget)

#     if not xi:
#         st.error("No valid squad found within the budget.")
#     else:
#         st.subheader(f"Formation: {formation}")
#         for label, type_id in zip(["Goalkeeper", "Defenders", "Midfielders", "Forwards"], [1, 2, 3, 4]):
#             st.markdown(f"### {label}")
#             for p in [pl for pl in xi if pl['element_type'] == type_id]:
#                 st.markdown(format_player(p))

#         st.markdown("### Bench")
#         for sub in subs:
#             st.markdown(f"🧦 {format_player(sub)}")


import streamlit as st
from fpl_api import (
    get_top_picks_by_position,
    get_captain_picks,
    get_top_raw_player_by_position,
    get_top_managers,
    get_all_players,
    fetch_data,
    fetch_fixtures,
    calculate_smart_score
)
from captain_ai import recommend_captain_ai
from formation_logic import get_best_xi_by_formation

st.set_page_config(page_title="FPL AI Assistant", layout="wide")
st.sidebar.success("Login bypassed – Welcome Developer!")

all_players = get_all_players()
# Enrich all players with smart_score and fixture info
data = fetch_data()
fixtures = fetch_fixtures()
team_lookup = {t['id']: t['name'] for t in data['teams']}

for p in all_players:
    p['smart_score'] = calculate_smart_score(p, fixtures, team_lookup)

player_pool = [p for p in all_players if p.get("element_type") in [1, 2, 3, 4]]

# def format_player(p):
    # return f"**{p['web_name']}** ({p['team_name']}) – £{p['now_cost']/10}m – Score: `{p['smart_score']}`"

def format_player(p):
    return (
        f"**{p['web_name']}** ({p['team_name']}) – "
        f"£{p['now_cost']/10}m – "
        f"Form: `{p.get('form', 0)}` – "
        f"Points: `{p.get('total_points', 0)}` – "
        f"Score: `{p['smart_score']}` – "
        f"Min: `{p.get('minutes', 0)}` – "
        f"Play Chance: `{p.get('chance_of_playing_next_round', '100')}%`"
    )

def format_player_detailed(p):
    # Convert fields safely
    cost = p.get('now_cost', 0) / 10
    form = p.get('form', '0')
    total_points = p.get('total_points', 0)
    minutes = p.get('minutes', 0)
    chance = p.get('chance_of_playing_next_round', 100)
    smart_score = p.get('smart_score', 0)
    fixtures = p.get('fixture_info', '')

    # Fixtures as emoji string (🟢 Easy, 🟡 Medium, 🔴 Hard)
    emoji_difficulty = ''
    if fixtures:
        for word in fixtures.split():
            if "(D1)" in word or "(D2)" in word:
                emoji_difficulty += "🟢"
            elif "(D3)" in word:
                emoji_difficulty += "🟡"
            elif "(D4)" in word or "(D5)" in word:
                emoji_difficulty += "🔴"

    # Add warning if playing chance < 100
    warn_icon = "⚠️" if isinstance(chance, (int, float)) and chance < 100 else ""

    # Create display string
    return (
        f"**{p['web_name']}** ({p['team_name']}) {warn_icon}\n"
        f"💰 £{cost:.1f}m | 🔥 Form: `{form}` | 🧮 Score: `{smart_score}`\n"
        f"🎯 Total Points: `{total_points}` | 🕒 Minutes: `{minutes}`\n"
        f"🧠 Playing Chance: `{chance}%` | 📆 Fixtures: {emoji_difficulty or 'N/A'}"
    )


tabs = st.tabs([
    "🏆 Top Picks",
    "⭐ Captain Picks",
    "🤖 AI Captain",
    "📊 Compare Players",
    "🧠 Your Squad",
    "🔁 Transfer Planner",
    "📈 Raw Leaders",
    "🧑‍💼 Top Managers",
    "🧮 Recommended XI"
])

with tabs[0]:
    st.header("Top Picks per Position")
    for pos in ["Goalkeeper", "Defender", "Midfielder", "Forward"]:
        st.subheader(pos)
        top_players = get_top_picks_by_position(pos, top_n=5)
        # for p in top_players:
        #     # st.markdown(format_player(p))
        #     st.markdown(f"{format_player(p)}\nFixtures: {p.get('fixture_info', 'N/A')}")
        for player in top_players:
            with st.container():
                col1, col2 = st.columns([0.15, 0.85])
                with col1:
                    st.image("https://resources.premierleague.com/premierleague/photos/players/110x140/p" + str(player["code"]) + ".png", width=60)
                with col2:
                    st.markdown(format_player_detailed(player))


with tabs[1]:
    st.header("Captain Picks")
    picks = get_captain_picks(top_n=5)
    if picks:
        for player in picks:
            # st.markdown(f"{format_player(p)}\nFixtures: {p.get('fixture_info', 'N/A')}")
            with st.container():
                col1, col2 = st.columns([0.15, 0.85])
                with col1:
                    st.image("https://resources.premierleague.com/premierleague/photos/players/110x140/p" + str(player["code"]) + ".png", width=60)
                with col2:
                    st.markdown(format_player_detailed(player))
    else:
        st.warning("No captain picks available.")

with tabs[2]:
    st.header("AI-Recommended Captains")
    picks = recommend_captain_ai(all_players)
    if picks:
        for player in picks:
            # st.markdown(f"{format_player(p)}\nFixtures: {p.get('fixture_info', 'N/A')}")
            with st.container():
                col1, col2 = st.columns([0.15, 0.85])
                with col1:
                    st.image("https://resources.premierleague.com/premierleague/photos/players/110x140/p" + str(player["code"]) + ".png", width=60)
                with col2:
                    st.markdown(format_player_detailed(player))
    else:
        st.warning("AI captain picks not available.")

with tabs[3]:
    st.header("Compare Players")
    team_names = sorted(set(p["team_name"] for p in player_pool))
    selected_team = st.selectbox("Select Team", team_names)
    team_players = [p for p in player_pool if p["team_name"] == selected_team]
    selected_player = st.selectbox("Select Player", [p["web_name"] for p in team_players])
    for p in team_players:
        if p["web_name"] == selected_player:
            st.markdown(f"**Selected Player Details:**\n{format_player(p)}\nFixtures: {p.get('fixture_info', 'N/A')}")

with tabs[4]:
    st.header("Your Squad")
    st.info("Login-based team import and visual formation coming soon.")

with tabs[5]:
    st.header("Transfer Planner")
    st.info("Will suggest optimal transfers based on user team.")

with tabs[6]:
    st.header("Raw Top Scorers by Position")
    for pos_id, label in zip([1, 2, 3, 4], ["Goalkeepers", "Defenders", "Midfielders", "Forwards"]):
        st.subheader(label)
        top_raw = [p for p in get_top_raw_player_by_position(label) if p["element_type"] == pos_id]
        for p in top_raw[:3]:
            st.markdown(format_player(p))

with tabs[7]:
    st.header("Top Managers")
    managers = get_top_managers()
    for m in managers:
        st.markdown(f"🏅 **{m['manager_name']}** – Total Points: `{m['points']}`")

with tabs[8]:
    st.header("Recommended XI (with Subs)")
    budget = 1000
    xi, formation, subs = get_best_xi_by_formation(player_pool, budget)

    if not xi:
        st.error("No valid squad found within the budget.")
    else:
        st.subheader(f"Formation: {formation}")
        for label, type_id in zip(["Goalkeeper", "Defenders", "Midfielders", "Forwards"], [1, 2, 3, 4]):
            st.markdown(f"### {label}")
            for p in [pl for pl in xi if pl['element_type'] == type_id]:
                st.markdown(format_player(p))

        st.markdown("### Bench")
        for sub in subs:
            st.markdown(f"🧦 {format_player(sub)}")