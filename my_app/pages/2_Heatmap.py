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
query GetChestOpens($startTime: BigInt!) {
    chestOpeneds(orderBy: timestamp, orderDirection: asc, where: {timestamp_gte: $startTime}) {
        timestamp
        isPremium
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

st.title('Chest Opening Heatmaps')

# Date range selection
end_date = st.date_input('End date', datetime.now().date())
start_date = st.date_input('Start date', end_date - timedelta(days=30))

# Convert dates to timestamps
start_timestamp = int(datetime.combine(start_date, datetime.min.time()).timestamp())
end_timestamp = int(datetime.combine(end_date, datetime.max.time()).timestamp())

# Fetch chest opening data
variables = {'startTime': start_timestamp}

# Execute the query
result = execute_query(CHEST_OPENS_QUERY, variables)

# Process the result
if result and 'data' in result:
    chest_opens = result['data'].get('chestOpeneds', [])
    if chest_opens:
        # Convert timestamps to datetime and create DataFrame
        df = pd.DataFrame(chest_opens)
        df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='s')
        df['hour'] = df['timestamp'].dt.hour
        df['day'] = df['timestamp'].dt.day_name()
        
        # Create separate heatmaps for regular and premium chests
        st.subheader(f'Total Chest Opens: {len(chest_opens)}')
        
        # Aggregate data for heatmap
        heatmap_data = df.groupby(['day', 'hour', 'isPremium']).size().reset_index(name='count')
        
        # Create heatmaps for both chest types
        for chest_type in [False, True]:
            chest_data = heatmap_data[heatmap_data['isPremium'] == chest_type]
            pivot_table = chest_data.pivot(index='day', columns='hour', values='count').fillna(0)
            
            # Order days correctly
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            pivot_table = pivot_table.reindex(days_order)
            
            fig = px.imshow(pivot_table,
                           title=f'{"Premium" if chest_type else "Regular"} Chest Opens Heatmap',
                           labels=dict(x='Hour of Day', y='Day of Week', color='Number of Opens'),
                           aspect='auto')
            st.plotly_chart(fig)
    else:
        st.warning("No chest opens found in the selected time period")
else:
    st.error("Failed to fetch chest opening data or invalid response format")

# ... rest of the file remains the same ...
