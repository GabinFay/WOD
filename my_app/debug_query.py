import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import json

load_dotenv()

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
    print(f"Using URL: {url}")
    
    print("\nSending request with variables:", variables)
    response = requests.post(url, json={'query': query, 'variables': variables})
    
    print(f"\nStatus Code: {response.status_code}")
    print("Response Headers:", response.headers)
    
    if response.status_code == 200:
        result = response.json()
        print("\nResponse JSON:", json.dumps(result, indent=2))
        return result
    else:
        print("\nError Response:", response.text)
        return None

def main():
    # Get timestamps for last 30 days
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    start_timestamp = int(datetime.combine(start_date, datetime.min.time()).timestamp())
    
    print(f"\nQuerying for data from timestamp: {start_timestamp}")
    print(f"Date range: {start_date} to {end_date}")
    
    variables = {'startTime': start_timestamp}
    result = execute_query(CHEST_OPENS_QUERY, variables)
    
    if result:
        if 'data' in result:
            chest_opens = result['data'].get('chestOpens', [])
            print(f"\nFound {len(chest_opens)} chest opens")
            if chest_opens:
                print("\nFirst chest open:", chest_opens[0])
        else:
            print("\nNo 'data' field in response")
            print("Full response:", result)

if __name__ == "__main__":
    print("Starting debug script...")
    print(f"Environment variables loaded: {os.environ.get('SUBGRAPH_URL') is not None}")
    main()