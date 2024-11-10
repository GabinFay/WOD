import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os
from streamlit_extras.switch_page_button import switch_page

load_dotenv()

st.set_page_config(page_title="User Details", page_icon="👤")

USER_DETAILS_QUERY = '''
query UserDetails($userId: ID!) {
    user(id: $userId) {
        id
        lifetimeChestCount
        lifetimePremiumChestCount
        lifetimeTotalChestCount
        isPremiumUser
        chestOpens(orderBy: timestamp, orderDirection: desc, first: 100) {
            timestamp
            isPremium
        }
    }
}
'''

def execute_query(query, variables):
    url = os.getenv('SUBGRAPH_URL')
    response = requests.post(url, json={'query': query, 'variables': variables})
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Query failed with status code {response.status_code}")
        return None

# Back button
if st.button("← Back to Leaderboard"):
    switch_page("Leaderboard")

# Get user_id from query parameters
# query_params = st.experimental_get_query_params()
user_id = st.query_params.get("user_id")

if not user_id:
    st.warning("No user selected. Please select a user from the leaderboard.")
    if st.button("Go to Leaderboard"):
        switch_page("Leaderboard")
else:
    user_data = execute_query(USER_DETAILS_QUERY, {'userId': user_id})
    
    if user_data and 'data' in user_data and user_data['data']['user']:
        user = user_data['data']['user']
        
        # User header
        st.title(f"User Details")
        st.subheader(f"Address: {user['id']}")
        
        # BSCScan button
        bscscan_url = f"https://www.bscscan.com/address/{user['id']}"
        st.markdown(f"[View on BSCScan 🔍]({bscscan_url})")
        
        # User stats in columns
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Regular Chests", user['lifetimeChestCount'])
        with col2:
            st.metric("Premium Chests", user['lifetimePremiumChestCount'])
        with col3:
            st.metric("Total Chests", user['lifetimeTotalChestCount'])
            
        st.write(f"Premium User: {'Yes ✨' if user['isPremiumUser'] else 'No'}")
        
        # Chest opening history
        st.subheader("Recent Chest Opens")
        if user['chestOpens']:
            df = pd.DataFrame(user['chestOpens'])
            df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='s')
            df['chest_type'] = df['isPremium'].map({True: 'Premium', False: 'Regular'})
            df = df.drop('isPremium', axis=1)
            
            st.dataframe(
                df.rename(columns={
                    'timestamp': 'Time',
                    'chest_type': 'Chest Type'
                }).sort_values('Time', ascending=False),
                hide_index=True
            )
        else:
            st.info("No chest opening history available")
    else:
        st.error("Failed to load user data")