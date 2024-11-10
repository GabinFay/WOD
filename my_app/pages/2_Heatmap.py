import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(page_title="Chest Opening Heatmaps", page_icon="📅")

CHEST_OPENS_QUERY = '''
query GetChestOpens($startTime: BigInt!, $endTime: BigInt!, $user: String!) {
    chestOpeneds(
        orderBy: timestamp, 
        orderDirection: asc, 
        where: {
            timestamp_gte: $startTime,
            timestamp_lte: $endTime,
            user: $user
        }
    ) {
        timestamp
        isPremium
        user
    }
}
'''

# Add query to fetch users
USERS_QUERY = '''
query GetUsers {
    users {
        id
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

st.title('User Chest Opening Heatmaps')

# Fetch users first
users_result = execute_query(USERS_QUERY, {})
if users_result and 'data' in users_result:
    users = [user['id'] for user in users_result['data']['users']]
    selected_user = st.selectbox('Select User', users)

    # Set date range (last 30 days)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)

    # Fetch chest opening data for selected user
    variables = {
        'startTime': int(datetime.combine(start_date, datetime.min.time()).timestamp()),
        'endTime': int(datetime.combine(end_date, datetime.max.time()).timestamp()),
        'user': selected_user
    }

    # Execute the query
    result = execute_query(CHEST_OPENS_QUERY, variables)

    # Process the result
    if result and 'data' in result:
        chest_opens = result['data'].get('chestOpeneds', [])
        if chest_opens:
            df = pd.DataFrame(chest_opens)
            df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='s')
            df['date'] = df['timestamp'].dt.date
            df['hour'] = df['timestamp'].dt.hour
            
            st.subheader(f'Total Chest Opens for {selected_user}: {len(df)}')
            
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
                ).reindex(columns=range(24), fill_value=0)
                
                fig = px.imshow(
                    pivot_data,
                    title=f'{"Premium" if chest_type else "Regular"} Chest Opens - Last 30 Days',
                    labels=dict(x='Hour of Day', y='Date', color='Number of Opens'),
                    aspect='auto',
                    x=list(range(24))
                )
                st.plotly_chart(fig)
        else:
            st.warning(f"No chest opens found for {selected_user} in the last 30 days")
else:
    st.error("Failed to fetch users data")

# ... rest of the file remains the same ...
