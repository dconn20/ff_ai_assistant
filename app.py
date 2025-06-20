import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from fpl_api import (
    get_top_picks_by_position,
    get_captain_picks,
    get_top_raw_player_by_position,
    get_top_managers,
)

# -------------------------
# Authentication
# -------------------------
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

authenticator.login(location='main')

# -------------------------
# Auth Check Using session_state
# -------------------------
if "authentication_status" in st.session_state:
    if st.session_state["authentication_status"]:
        st.sidebar.success(f"Welcome, {st.session_state['name']}!")
        authenticator.logout("Logout", "sidebar")

        # -------------------------
        # Tabs Layout
        # -------------------------
        tabs = st.tabs(["🏆 Top Picks", "⭐ Captain Picks", "🧠 Your Squad", "📈 Raw Leaders", "🧑‍💼 Top Managers"])

        with tabs[0]:
            st.header("🏆 Top Picks by Position")
            for position in ["Goalkeepers", "Defenders", "Midfielders", "Forwards"]:
                st.subheader(position)
                top_players = get_top_picks_by_position(position)
                for p in top_players:
                    st.markdown(f"""**{p['web_name']}** ({p['team_name']}) – 💰 £{p['now_cost']/10}m –  
📊 Score: `{p['smart_score']}`  
🗓️ {p.get('fixture_info', '')}""")

        with tabs[1]:
            st.header("⭐ Captain Picks")
            captains = get_captain_picks()
            for p in captains:
                st.markdown(f"""**{p['web_name']}** ({p['team_name']}) – 💰 £{p['now_cost']/10}m –  
📊 Score: `{p['smart_score']}`  
🗓️ {p.get('fixture_info', '')}""")

        with tabs[2]:
            st.header("🧠 Your Squad")
            st.markdown("Select up to 15 players from the current FPL pool (free text for now).")
            user_squad = st.text_area("Enter your squad (comma-separated player names)", height=150)
            if st.button("Analyze Squad"):
                st.info("Squad analysis coming soon. This will match your players against top picks and captain suggestions.")

        with tabs[3]:
            st.header("📈 Raw Top Performers (Total Points)")
            for position in ["Goalkeepers", "Defenders", "Midfielders", "Forwards"]:
                best = get_top_raw_player_by_position(position)
                st.markdown(f"""**{position}**: {best['web_name']} ({best['team_name']}) – 🏅 {best['total_points']} points""")

        with tabs[4]:
            st.header("🧑‍💼 Top Managers")
            managers = get_top_managers()
            for m in managers:
                st.markdown(f"""**{m['web_name']}** ({m['team_name']}) – Score: `{m['smart_score']}`""")

    elif st.session_state["authentication_status"] is False:
        st.error("Username or password is incorrect")
    else:
        st.warning("Please log in to continue.")
else:
    st.warning("Please log in to continue.")
