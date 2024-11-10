import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Contract Stats Debug", page_icon="🔍")

# Define a query to fetch all DailyChestOpen entities
FETCH_ALL_DAILY_CHEST_OPENS_QUERY = '''
query FetchAllDailyChestOpens {
    dailyChestOpens(orderBy: date, orderDirection: asc) {
        date
        regularChestCount
        premiumChestCount
        totalChestCount
    }
}
'''

def execute_query(query):
    url = os.getenv('SUBGRAPH_URL')
    response = requests.post(url, json={'query': query})
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Query failed with status code {response.status_code}")
        return None

def fetch_all_daily_chest_opens():
    result = execute_query(FETCH_ALL_DAILY_CHEST_OPENS_QUERY)
    if result and 'data' in result:
        return result['data'].get('dailyChestOpens', [])
    else:
        return []

st.title('Daily Chest Opens Debug')

# Fetch all DailyChestOpen entities
daily_chest_opens = fetch_all_daily_chest_opens()

if daily_chest_opens:
    # Convert the data to a DataFrame
    df = pd.DataFrame(daily_chest_opens)
    
    # Convert 'date' to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Set 'date' as the index
    df.set_index('date', inplace=True)
    
    # Display the DataFrame for debugging
    st.write("DataFrame:", df)

    # Plotting
    fig, ax = plt.subplots(figsize=(10, 6))
    df[['regularChestCount', 'premiumChestCount']].plot(kind='bar', stacked=True, ax=ax, color=['#1f77b4', '#ff7f0e'])
    ax.set_title('Daily Chest Opens')
    ax.set_xlabel('Date')
    ax.set_ylabel('Number of Opens')
    ax.legend(title='Chest Type')
    plt.xticks(rotation=45)
    st.pyplot(fig)
else:
    st.warning("No DailyChestOpen entities found.")