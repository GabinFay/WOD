import pandas as pd
from datetime import datetime

# Sample data structure after fetching from the subgraph
user_data = [
    {
        "id": "0xUser1",
        "lifetimeChestCount": 100,
        "lifetimePremiumChestCount": 20,
        "chestOpens": [
            {"timestamp": 1672545600, "isPremium": False},
            {"timestamp": 1672632000, "isPremium": True},
            # additional events
        ]
    },
    # more users
]

# Initialize lists to hold features
user_ids, total_chests, premium_chests, avg_time_interval, burst_count, daily_pattern = [], [], [], [], [], []

for user in user_data:
    user_id = user["id"]
    events = user["chestOpens"]
    
    # Feature 1: Total chests opened
    total_chests.append(user["lifetimeChestCount"])
    
    # Feature 2: Total premium chests opened
    premium_chests.append(user["lifetimePremiumChestCount"])
    
    # Feature 3: Average time interval between chests
    timestamps = [event["timestamp"] for event in events]
    if len(timestamps) > 1:
        intervals = [timestamps[i + 1] - timestamps[i] for i in range(len(timestamps) - 1)]
        avg_time_interval.append(sum(intervals) / len(intervals))
    else:
        avg_time_interval.append(None)
    
    # Feature 4: Burst count (multiple chests in <1 minute)
    bursts = sum(1 for i in range(len(intervals)) if intervals[i] < 60) if len(intervals) > 1 else 0
    burst_count.append(bursts)
    
    # Feature 5: Daily activity pattern
    day_counts = pd.Series([datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d') for ts in timestamps]).value_counts()
    daily_pattern.append(day_counts.to_dict())  # Dictionary of counts per day
    
    # Append user ID
    user_ids.append(user_id)

# Build DataFrame
X = pd.DataFrame({
    "user_id": user_ids,
    "total_chests": total_chests,
    "premium_chests": premium_chests,
    "avg_time_interval": avg_time_interval,
    "burst_count": burst_count,
    "daily_pattern": daily_pattern  # To be processed further if needed
})
