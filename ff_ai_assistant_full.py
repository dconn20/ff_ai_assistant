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
    calculate_smart_score,
    get_prediction
)
from captain_ai import recommend_captain_ai
from formation_logic import get_best_xi_by_formation
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from math import pi
import seaborn as sns


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

def get_player_image_url(player):
    code = player.get("photo", "").split(".")[0]
    return f"https://resources.premierleague.com/premierleague/photos/players/110x140/p{code}.png"

def plot_radar_chart(player1, player2, labels):
    stats1 = [player1.get(l, 0) for l in labels]
    stats2 = [player2.get(l, 0) for l in labels]

    angles = [n / float(len(labels)) * 2 * pi for n in range(len(labels))]
    stats1 += stats1[:1]
    stats2 += stats2[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)

    plt.xticks(angles[:-1], labels)
    ax.plot(angles, stats1, linewidth=0.1, linestyle='solid', label=player1['web_name'])
    ax.fill(angles, stats1, alpha=0.1)

    ax.plot(angles, stats2, linewidth=0.1, linestyle='solid', label=player2['web_name'])
    ax.fill(angles, stats2, alpha=0.1)

    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    st.pyplot(fig)

# Define a utility function to prepare the comparison data
def prepare_comparison_data(player1, player2):
    stats = ['goals_scored', 'assists', 'minutes', 'total_points', 'smart_score']
    data = {
        'Stat': stats,
        player1['web_name']: [player1.get(stat, 0) for stat in stats],
        player2['web_name']: [player2.get(stat, 0) for stat in stats]
    }
    return pd.DataFrame(data)

# Grouped Bar Chart Function
def plot_grouped_bar_chart(df, player1_name, player2_name):
    df_melted = df.melt(id_vars='Stat', var_name='Player', value_name='Value')
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Stat', y='Value', hue='Player', data=df_melted)
    plt.title('Player Stat Comparison')
    plt.xticks(rotation=45)
    st.pyplot(plt.gcf())
    plt.clf()

# Heatmap Function
def plot_comparison_heatmap(df):
    df_copy = df.copy()
    df_copy.set_index('Stat', inplace=True)
    plt.figure(figsize=(8, 4))
    sns.heatmap(df_copy, annot=True, fmt=".1f", cmap="coolwarm")
    plt.title('Stat Heatmap')
    st.pyplot(plt.gcf())
    plt.clf()


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

# with tabs[3]:
#     st.header("Compare Players")
#     team_names = sorted(set(p["team_name"] for p in player_pool))
#     selected_team = st.selectbox("Select Team", team_names)
#     team_players = [p for p in player_pool if p["team_name"] == selected_team]
#     selected_player = st.selectbox("Select Player", [p["web_name"] for p in team_players])
#     for p in team_players:
#         if p["web_name"] == selected_player:
#             st.markdown(f"**Selected Player Details:**\n{format_player(p)}\nFixtures: {p.get('fixture_info', 'N/A')}")

with tabs[3]:
    st.header("📊 Compare Players")

    team_names = sorted(set(p["team_name"] for p in player_pool))

    col1, col2 = st.columns(2)

    with col1:
        team1 = st.selectbox("Select Team 1", team_names, key="team1")
        players1 = [p for p in player_pool if p["team_name"] == team1]
        player1_name = st.selectbox("Select Player from Team 1", [p["web_name"] for p in players1], key="player1")

    with col2:
        team2 = st.selectbox("Select Team 2", team_names, index=1 if team_names[0] == team1 else 0, key="team2")
        players2 = [p for p in player_pool if p["team_name"] == team2]
        player2_name = st.selectbox("Select Player from Team 2", [p["web_name"] for p in players2], key="player2")

    # Retrieve player data
    player1 = next(p for p in players1 if p["web_name"] == player1_name)
    player2 = next(p for p in players2 if p["web_name"] == player2_name)

    st.markdown("## 🆚 Player Comparison")
    col1, col2 = st.columns(2)

    # with col1:
    #     st.markdown("### 🔵 Player 1")
    #     st.markdown(format_player_detailed(player1))

    # with col2:
    #     st.markdown("### 🔴 Player 2")
    #     st.markdown(format_player_detailed(player2))

    with col1:
        st.markdown("### 🔵 Player 1")
        st.image(get_player_image_url(player1), width=100)
        st.markdown(format_player_detailed(player1))

    with col2:
        st.markdown("### 🔴 Player 2")
        st.image(get_player_image_url(player2), width=100)
        st.markdown(format_player_detailed(player2))

    st.markdown(f"### 🔍 Comparing **{player1['web_name']}** vs **{player2['web_name']}**")

    comp_df = prepare_comparison_data(player1, player2)

    st.markdown("#### 📊 Grouped Bar Chart")
    plot_grouped_bar_chart(comp_df, player1['web_name'], player2['web_name'])

    st.markdown("#### 🌡️ Performance Heatmap")
    plot_comparison_heatmap(comp_df)

    # Side-by-side table
    # metrics = ["total_points", "now_cost", "minutes", "goals_scored", "assists", "clean_sheets"]
    # data = {
    #     "Stats 24/25": metrics,
    #     player1["web_name"]: [player1.get(m, 0) for m in metrics],
    #     player2["web_name"]: [player2.get(m, 0) for m in metrics],
    # }
    # df = pd.DataFrame(data)
    # st.table(df)


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