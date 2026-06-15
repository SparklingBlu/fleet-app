import requests
import json

CLIENT_ID = "5syO_-GOEpq7Ia_TChV9-0X57VtoRlbK"
CLIENT_SECRET = input("Paste your Uber Client Secret: ").strip()

# Get token
auth_payload = {
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "grant_type": "client_credentials",
    "scope": "solutions.suppliers.metrics.read",
}

auth_headers = {"Content-Type": "application/x-www-form-urlencoded"}

try:
    auth_response = requests.post(
        "https://auth.uber.com/oauth/v2/token",
        data=auth_payload,
        headers=auth_headers
    )
    
    if auth_response.status_code != 200:
        print(f"Auth failed: {auth_response.text}")
        exit()
    
    token = auth_response.json()["access_token"]
    print("✅ Got token successfully\n")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    url = "https://api.uber.com/v1/vehicle-suppliers/analytics-data/query"
    
    # Test with the corrected reportRequests structure
    payloads = [
        # Payload 1: Full reportRequests structure
        {
            "reportRequests": [
                {
                    "reportType": "DRIVER_PERFORMANCE",
                    "dateRange": {
                        "startDate": "2024-01-01",
                        "endDate": "2024-01-07"
                    },
                    "metrics": [
                        "HOURS_ONLINE",
                        "HOURS_ON_TRIP",
                        "TOTAL_TRIPS"
                    ]
                }
            ]
        },
        # Payload 2: Simpler report type
        {
            "reportRequests": [
                {
                    "reportType": "DRIVER",
                    "dateRange": {
                        "startDate": "2024-01-01",
                        "endDate": "2024-01-07"
                    }
                }
            ]
        },
        # Payload 3: Even simpler
        {
            "reportRequests": [
                {
                    "reportType": "PERFORMANCE",
                    "startDate": "2024-01-01",
                    "endDate": "2024-01-07"
                }
            ]
        },
        # Payload 4: Dashboard style
        {
            "dashboard": {
                "type": "DRIVER",
                "start_date": "2024-01-01",
                "end_date": "2024-01-07"
            }
        }
    ]
    
    for i, payload in enumerate(payloads, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        print('='*60)
        
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=15)
            print(f"Status: {resp.status_code}")
            
            if resp.status_code == 200:
                print("✅ SUCCESS!")
                data = resp.json()
                print(f"Response keys: {list(data.keys())}")
                print(f"Full response: {json.dumps(data, indent=2)[:2000]}")
                break
            elif resp.status_code == 400:
                print(f"Bad Request: {resp.text}")
            elif resp.status_code == 401:
                print("Unauthorized")
            else:
                print(f"Response: {resp.text[:500]}")
                
        except Exception as e:
            print(f"Error: {e}")

except Exception as e:
    print(f"Fatal error: {e}")

