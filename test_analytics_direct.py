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
    
    # Try analytics endpoint with different payload structures
    analytics_url = "https://api.uber.com/v1/vehicle-suppliers/analytics-data/query"
    
    test_payloads = [
        # Payload 1: No org_id (maybe not needed)
        {
            "start_date": "2024-01-01",
            "end_date": "2024-01-07"
        },
        # Payload 2: With supplier_id
        {
            "supplier_id": CLIENT_ID,
            "start_date": "2024-01-01",
            "end_date": "2024-01-07"
        },
        # Payload 3: With organization_id as empty
        {
            "organization_id": "",
            "start_date": "2024-01-01",
            "end_date": "2024-01-07"
        },
        # Payload 4: Different date format
        {
            "from": "2024-01-01T00:00:00Z",
            "to": "2024-01-07T23:59:59Z"
        },
    ]
    
    for i, payload in enumerate(test_payloads, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {json.dumps(payload)}")
        print('='*60)
        
        try:
            resp = requests.post(analytics_url, json=payload, headers=headers, timeout=15)
            print(f"Status: {resp.status_code}")
            
            if resp.status_code == 200:
                print("✅ SUCCESS!")
                data = resp.json()
                print(f"Response keys: {list(data.keys())}")
                print(f"Full response: {json.dumps(data, indent=2)[:1000]}")
                break
            elif resp.status_code == 401:
                print("❌ Unauthorized - check scope")
            elif resp.status_code == 400:
                print(f"Bad Request: {resp.text[:300]}")
            elif resp.status_code == 422:
                print(f"Validation Error: {resp.text[:300]}")
            else:
                print(f"Response: {resp.text[:300]}")
                
        except Exception as e:
            print(f"Error: {e}")

except Exception as e:
    print(f"Fatal error: {e}")

