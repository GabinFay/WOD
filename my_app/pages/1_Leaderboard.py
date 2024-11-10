import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(page_title="Leaderboard", page_icon="🏆")

LEADERBOARD_QUERY = '''
query GetChestLeaderboard($startTime: BigInt!, $isPremium: Boolean!) {
    users(
        orderBy: lifetimeTotalChestCount, 
        orderDirection: desc, 
        where: {
            chestOpens_: {isPremium: $isPremium, timestamp_gte: $startTime},
            lifetimeTotalChestCount_gt: 0
        }
    ) {
        id
        lifetimeChestCount
        lifetimePremiumChestCount
        lifetimeTotalChestCount
    }
}
'''

USER_HISTORY_QUERY = '''
query UserStats($userId: ID!) {
    user(id: $userId) {
        id
        lifetimeChestCount
        lifetimePremiumChestCount
        lifetimeTotalChestCount
        chestOpens(orderBy: timestamp, orderDirection: desc) {
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

st.title('Chest Leaderboard')

# Filter options
days = st.slider('Number of days to look back', 1, 30, 7)
is_premium = st.radio('Chest Type', ('Premium', 'Regular'))

# Calculate start time based on the number of days
start_time = int((datetime.now() - timedelta(days=days)).timestamp())
is_premium_bool = True if is_premium == 'Premium' else False

# Add sorting option after the chest type selection
sort_by = st.radio('Sort By', ('Total Chests', 'Regular Chests', 'Premium Chests'))

# Fetch leaderboard data
variables = {'startTime': start_time, 'isPremium': is_premium_bool}
data = execute_query(LEADERBOARD_QUERY, variables)

if data:
    users = data.get('data', {}).get('users', [])
    if users:
        df = pd.DataFrame(users)
        
        # Sort based on user selection
        if sort_by == 'Total Chests':
            df = df.sort_values('lifetimeTotalChestCount', ascending=False)
        elif sort_by == 'Regular Chests':
            df = df.sort_values('lifetimeChestCount', ascending=False)
        else:  # Premium Chests
            df = df.sort_values('lifetimePremiumChestCount', ascending=False)
            
        st.subheader('Leaderboard')
        
        # Rename columns for better display
        df_display = df.rename(columns={
            'id': 'User Address',
            'lifetimeChestCount': 'Regular Chests',
            'lifetimePremiumChestCount': 'Premium Chests',
            'lifetimeTotalChestCount': 'Total Chests'
        })
        
        st.dataframe(df_display)
    else:
        st.write('No data available for the selected filters.')

# User selection
user_ids = [user['id'] for user in users]
selected_user = st.selectbox('Select a user to view history', user_ids)

if selected_user:
    user_data = execute_query(USER_HISTORY_QUERY, {'userId': selected_user})
    if user_data:
        user_info = user_data.get('data', {}).get('user', {})
        if user_info:
            st.subheader(f"User: {user_info['id']}")
            st.write(f"Lifetime Chest Count: {user_info['lifetimeChestCount']}")
            st.write(f"Lifetime Premium Chest Count: {user_info['lifetimePremiumChestCount']}")
            st.write(f"Lifetime Total Chest Count: {user_info['lifetimeTotalChestCount']}")

            # Display chest opening history
            chest_opens = user_info.get('chestOpens', [])
            if chest_opens:
                history_df = pd.DataFrame(chest_opens)
                history_df['timestamp'] = pd.to_datetime(history_df['timestamp'], unit='s')
                st.subheader('Chest Opening History')
                st.dataframe(history_df)
            else:
                st.write('No chest opening history available.')
        else:
            st.write('User not found.')
