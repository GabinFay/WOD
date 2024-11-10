import streamlit as st
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_title="Chest Analysis App", page_icon="📊")

st.title("Welcome to the Chest Analysis App")

st.write("Use the sidebar to navigate between the Leaderboard and Heatmap pages.")

# Navigation buttons
if st.button("Go to Leaderboard"):
    switch_page("Leaderboard")

if st.button("Go to Heatmap"):
    switch_page("Heatmap")
