import streamlit as st
from fpl_api import (
    get_top_picks_by_position,
    get_captain_picks,
    get_top_raw_player_by_position,
    get_top_managers,
    get_all_players,
    POSITION_MAP
)
from captain_ai import recommend_captain_ai
from formation_logic import get_best_xi_by_formation

st.set_page_config(page_title="FPL AI Assistant", layout="wide")
st.sidebar.success("Login bypassed – Welcome Developer!")

# Load all player data
all_players = get_all_players()
player_pool = [p for p in all_players if p.get("element_type") in [1, 2, 3, 4]]

def format_player(p):
    return f"**{p['web_name']}** ({p['team_name']}) – £{p['now_cost']/10}m – Score: `{p.get('smart_score', 0)}`"

# Tab layout
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
    st.header("Top 3 Picks per Position")
    for pos in ["Goalkeeper", "Defender", "Midfielder", "Forward"]:
        st.subheader(pos)
        for p in get_top_picks_by_position(pos):
            st.markdown(format_player(p))

with tabs[1]:
    st.header("Captain Picks")
    picks = get_captain_picks()
    if picks:
        for p in picks:
            st.markdown(f"{format_player(p)}\nFixtures: {p.get('fixture_info', 'N/A')}")
    else:
        st.warning("No captain picks available.")

with tabs[2]:
    st.header("AI-Recommended Captains")
    picks = recommend_captain_ai(all_players)
    if picks:
        for p in picks:
            st.markdown(f"{format_player(p)}\nFixtures: {p.get('fixture_info', 'N/A')}")
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
        pos_label = POSITION_MAP[pos_id]
        top_raw = get_top_raw_player_by_position(pos_label, all_players)
        for p in top_raw[:3]:
            st.markdown(format_player(p))

with tabs[7]:
    st.header("Top Managers")
    managers = get_top_managers()
    sorted_mgrs = sorted(managers, key=lambda m: m.get("points", 0), reverse=True)
    for m in sorted_mgrs:
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
