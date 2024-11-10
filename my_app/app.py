import streamlit as st
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_title="Chest Analysis App", page_icon="📊")

# Directly switch to the Leaderboard page on app start
switch_page("Leaderboard")

# Remove the heatmap button and related text
st.title("Welcome to the Chest Analysis App")

st.write("Use the sidebar to navigate to the Leaderboard page.")

# Navigation button for the leaderboard
if st.button("Go to Leaderboard"):
    switch_page("Leaderboard")
