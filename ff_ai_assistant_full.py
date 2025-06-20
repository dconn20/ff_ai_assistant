
import streamlit as st
from fpl_api import (
    get_top_picks_by_position,
    get_captain_picks,
    get_top_raw_player_by_position,
    get_top_managers,
    get_all_players,
)
from captain_ai import recommend_captain_ai
from formation_logic import get_best_xi_by_formation

st.set_page_config(page_title="FPL AI Assistant", layout="wide")
st.sidebar.success("Login bypassed – Welcome Developer!")

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

all_players = get_all_players()
player_pool = [p for p in all_players if p.get('element_type') in [1, 2, 3, 4]]

def format_player(p):
    return f"**{p['web_name']}** ({p['team_name']}) – £{p['now_cost']/10}m – Score: `{p['smart_score']}`"

with tabs[0]:
    st.header("🏆 Top 3 Picks per Position")
    positions = ["Goalkeeper", "Defender", "Midfielder", "Forward"]
    labels = ["🧤 Goalkeepers", "🛡️ Defenders", "🎯 Midfielders", "🔥 Forwards"]
    for pos_label, section_title in zip(positions, labels):
        st.subheader(section_title)
        top_players = get_top_picks_by_position(pos_label)
        for p in top_players[:3]:
            st.markdown(format_player(p))

with tabs[1]:
    st.header("⭐ Captain Picks")
    for p in get_captain_picks(all_players):
        st.markdown(format_player(p))

with tabs[2]:
    st.header("🤖 AI-Recommended Captains")
    ai_captains = recommend_captain_ai(all_players)
    for p in ai_captains:
        if p.get("element_type") in [1, 2, 3, 4]:
            st.markdown(format_player(p))

with tabs[3]:
    st.header("📊 Compare Players")
    positions_map = {
        "Goalkeepers": "Goalkeeper",
        "Defenders": "Defender",
        "Midfielders": "Midfielder",
        "Forwards": "Forward"
    }
    pos = st.selectbox("Select position to compare", list(positions_map.keys()))
    top = get_top_picks_by_position(positions_map[pos])
    for p in top[:3]:
        st.markdown(format_player(p))

with tabs[4]:
    st.header("🧠 Your Squad")
    st.info("Login-based team import and visualization coming soon!")

with tabs[5]:
    st.header("🔁 Transfer Planner")
    st.info("Upcoming feature: Suggest optimal transfers based on your team.")

with tabs[6]:
    st.header("📈 Raw Top Scorers by Position")
    for pos_id, label in zip([1, 2, 3, 4], ["🧤 Goalkeepers", "🛡️ Defenders", "🎯 Midfielders", "🔥 Forwards"]):
        st.subheader(label)
        top_raw = [p for p in get_top_raw_player_by_position(all_players) if p["element_type"] == pos_id]
        for p in top_raw[:3]:
            st.markdown(format_player(p))

with tabs[7]:
    st.header("🧑‍💼 Top Managers")
    for m in get_top_managers():
        st.markdown(f"🏅 **{m['player_name']}** – Team: _{m['entry_name']}_ – Points: `{m['summary_overall_points']}`")

with tabs[8]:
    st.header("🧮 Recommended XI (with Subs)")
    budget = 1000  # £100.0m
    xi, formation, subs = get_best_xi_by_formation(player_pool, budget)

    if not xi:
        st.error("No valid squad found within the budget.")
    else:
        st.subheader(f"💡 Formation: {formation}")
        gks = [p for p in xi if p['element_type'] == 1]
        defs = [p for p in xi if p['element_type'] == 2]
        mids = [p for p in xi if p['element_type'] == 3]
        fwds = [p for p in xi if p['element_type'] == 4]

        st.markdown("### 🧤 Goalkeeper")
        for p in gks:
            st.markdown(format_player(p))

        st.markdown("### 🛡️ Defenders")
        for p in defs:
            st.markdown(format_player(p))

        st.markdown("### 🎯 Midfielders")
        for p in mids:
            st.markdown(format_player(p))

        st.markdown("### 🔥 Forwards")
        for p in fwds:
            st.markdown(format_player(p))

        st.divider()
        st.markdown("### 🔁 Bench")
        for sub in subs:
            st.markdown(f"🪑 {format_player(sub)}")
