import pandas as pd
import requests
import numpy as np
from datetime import datetime
from scipy.stats import entropy
import os
from dotenv import load_dotenv
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to execute GraphQL query
def execute_query(query, variables=None):
    url = os.getenv('SUBGRAPH_URL')
    response = requests.post(url, json={'query': query, 'variables': variables})
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Query failed with status code {response.status_code}")

# GraphQL query to fetch user data
USER_DATA_QUERY = '''
query UserData {
  users {
    id
    lifetimeChestCount
    lifetimePremiumChestCount
    chestOpens(orderBy: timestamp, orderDirection: asc) {
      timestamp
      isPremium
    }
  }
}
'''

# Function to fetch all user data with pagination
def fetch_all_user_data():
    all_users = []
    first = 100
    skip = 0
    max_users = 500  # Limit to the first 500 users
    logging.info("Starting to fetch user data with pagination.")
    while len(all_users) < max_users:
        logging.info(f"Fetching users with skip={skip} and first={first}.")
        variables = {'first': first, 'skip': skip}
        response_data = execute_query(USER_DATA_QUERY, variables)
        users = response_data.get('data', {}).get('users', [])
        if not users:
            logging.info("No more users to fetch. Exiting loop.")
            break
        all_users.extend(users)
        skip += first
        if len(all_users) >= max_users:
            logging.info(f"Reached the limit of {max_users} users. Stopping fetch.")
            all_users = all_users[:max_users]  # Trim to exactly 500 users if exceeded
            break
    logging.info(f"Fetched a total of {len(all_users)} users.")
    return all_users

# Fetch all user data
logging.info("Fetching all user data.")
user_data = fetch_all_user_data()

# Initialize lists to hold features
logging.info("Initializing feature lists.")
user_ids, total_chests, premium_chests, avg_time_interval, burst_count, daily_entropy = [], [], [], [], [], []

for user in user_data:
    logging.info(f"Processing user {user['id']}.")
    user_id = user["id"]
    events = user["chestOpens"]
    
    # Feature 1: Total chests opened
    total_chests.append(user["lifetimeChestCount"])
    
    # Feature 2: Total premium chests opened
    premium_chests.append(user["lifetimePremiumChestCount"])
    
    # Feature 3: Average time interval between chests
    timestamps = [int(event["timestamp"]) for event in events]  # Convert timestamps to integers
    if len(timestamps) > 1:
        intervals = [timestamps[i + 1] - timestamps[i] for i in range(len(timestamps) - 1)]
        avg_time_interval.append(sum(intervals) / len(intervals))
    else:
        avg_time_interval.append(None)
    
    # Feature 4: Burst count (multiple chests in <1 minute)
    bursts = sum(1 for i in range(len(intervals)) if intervals[i] < 60) if len(intervals) > 1 else 0
    burst_count.append(bursts)
    
    # Feature 5: Daily activity pattern entropy
    day_counts = pd.Series([datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d') for ts in timestamps]).value_counts()
    daily_entropy.append(entropy(day_counts))  # Compute entropy of daily activity
    
    # Append user ID
    user_ids.append(user_id)

# Build DataFrame
logging.info("Building DataFrame.")
X = pd.DataFrame({
    "user_id": user_ids,
    "total_chests": total_chests,
    "premium_chests": premium_chests,
    "avg_time_interval": avg_time_interval,
    "burst_count": burst_count,
    "daily_entropy": daily_entropy  # Entropy of daily activity
})

# Save DataFrame to CSV
output_file_path = 'user_data_features.csv'
X.to_csv(output_file_path, index=False)
logging.info(f"DataFrame saved to {output_file_path}")

# Now X can be used for further processing with DBSCAN or other models
