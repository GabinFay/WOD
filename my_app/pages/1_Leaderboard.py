import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from streamlit_extras.switch_page_button import switch_page

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
        isPremiumUser
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
        isPremiumUser
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
premium_users_only = st.checkbox('Show Premium Users Only')

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
        
        # Filter for premium users if checkbox is selected
        if premium_users_only:
            df = df[df['isPremiumUser'] == True]
        
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
            'lifetimeTotalChestCount': 'Total Chests',
            'isPremiumUser': 'Premium User'
        })
        
        # Make the dataframe clickable and add BSCScan link
        def make_clickable(address):
            app_link = f'<a href="User_Details?user_id={address}">{address}</a>'
            # Using BSCScan or Binance logo image
            bscscan_link = f'<a href="https://www.bscscan.com/address/{address}" target="_blank"><img src="https://bscscan.com/images/favicon.ico" width="16" height="16" style="vertical-align: middle;"></a>'
            return f'{app_link} {bscscan_link}'
        
        df_display['User Address'] = df_display['User Address'].apply(make_clickable)
        st.write(df_display.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.write('No data available for the selected filters.')

# Add a button to navigate to the Contract Stats page
if st.button("View Contract Stats"):
    switch_page("Contract Stats")
