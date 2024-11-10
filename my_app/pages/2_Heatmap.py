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
if result:
    chest_opens = result['data']['chestOpeneds']
    df = pd.DataFrame(chest_opens)
    fig = px.scatter(df, x='timestamp', y='isPremium', title='Chest Opening Heatmap')
    st.plotly_chart(fig)
else:
    st.error("Failed to fetch chest opening data")

# ... rest of the file remains the same ...
