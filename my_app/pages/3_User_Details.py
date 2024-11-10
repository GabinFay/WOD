import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from streamlit_extras.switch_page_button import switch_page
import plotly.express as px

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
        chestOpens(orderBy: timestamp, orderDirection: desc) {
            timestamp
            isPremium
        }
    }
}
'''

CHEST_OPENS_QUERY = '''
query GetChestOpens($startTime: BigInt!, $endTime: BigInt!, $user: String!, $first: Int!, $skip: Int!) {
    chestOpeneds(
        orderBy: timestamp, 
        orderDirection: asc, 
        where: {
            timestamp_gte: $startTime,
            timestamp_lte: $endTime,
            user: $user
        },
        first: $first,
        skip: $skip
    ) {
        timestamp
        isPremium
        user
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

def fetch_all_chest_opens(startTime, endTime, user):
    all_chest_opens = []
    first = 100
    skip = 0
    while True:
        variables = {
            'startTime': startTime,
            'endTime': endTime,
            'user': user,
            'first': first,
            'skip': skip
        }
        result = execute_query(CHEST_OPENS_QUERY, variables)
        if result and 'data' in result:
            chest_opens = result['data'].get('chestOpeneds', [])
            if not chest_opens:
                break
            all_chest_opens.extend(chest_opens)
            skip += first
        else:
            break
    return all_chest_opens

# Back button
if st.button("← Back to Leaderboard"):
    switch_page("Leaderboard")

# Get user_id from query parameters
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
        
        # Set default start and end dates
        default_start_date = datetime(2024, 10, 9)
        default_end_date = datetime(2024, 11, 11)

        # Add a date range slider to the Streamlit app
        start_date, end_date = st.slider(
            "Select Date Range",
            min_value=default_start_date,
            max_value=default_end_date,
            value=(default_start_date, default_end_date),
            format="YYYY-MM-DD"
        )

        # Fetch chest opening data for heatmap
        variables = {
            'startTime': int(datetime.combine(start_date, datetime.min.time()).timestamp()),
            'endTime': int(datetime.combine(end_date, datetime.max.time()).timestamp()),
            'user': user['id']
        }
        chest_opens = fetch_all_chest_opens(variables['startTime'], variables['endTime'], variables['user'])

        # Process the result for heatmap
        if chest_opens:
            df = pd.DataFrame(chest_opens)
            df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='s')
            df['date'] = df['timestamp'].dt.date
            df['hour'] = df['timestamp'].dt.hour
            
            st.subheader(f'Total Chest Opens for {user["id"]}: {len(df)}')
            
            # Determine the full date range from the data
            min_date = df['date'].min()
            max_date = df['date'].max()
            
            # Create heatmaps for both chest types
            for chest_type in [False, True]:
                chest_data = df[df['isPremium'] == chest_type]
                pivot_data = pd.pivot_table(
                    chest_data,
                    values='timestamp',
                    index='date',
                    columns='hour',
                    aggfunc='count',
                    fill_value=0
                ).reindex(index=pd.date_range(min_date, max_date), columns=range(24), fill_value=0)
                
                fig = px.imshow(
                    pivot_data,
                    title=f'{"Premium" if chest_type else "Regular"} Chest Opens - Full Date Range',
                    labels=dict(x='Hour of Day', y='Date', color='Number of Opens'),
                    aspect='auto',
                    x=list(range(24))
                )
                st.plotly_chart(fig)
        else:
            st.warning(f"No chest opens found for {user['id']} in the available data range")
    else:
        st.error("Failed to load user data")