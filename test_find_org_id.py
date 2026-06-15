import requests
import json
import base64

CLIENT_ID = "5syO_-GOEpq7Ia_TChV9-0X57VtoRlbK"
CLIENT_SECRET = input("Paste your Uber Client Secret: ").strip()

# Get token
auth_response = requests.post(
    "https://auth.uber.com/oauth/v2/token",
    data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials",
        "scope": "solutions.suppliers.metrics.read",
    },
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)

if auth_response.status_code != 200:
    print(f"Auth failed: {auth_response.text}")
    exit()

token = auth_response.json()["access_token"]
print("✅ Authenticated\n")

# Decode the JWT token - it might contain org info
print("=" * 60)
print("DECODING JWT TOKEN FOR ORG INFO")
print("=" * 60)
try:
    parts = token.split('.')
    if len(parts) == 3:
        # Decode payload
        payload = parts[1] + '=' * (4 - len(parts[1]) % 4)
        decoded = base64.b64decode(payload)
        jwt_data = json.loads(decoded)
        print(json.dumps(jwt_data, indent=2))
        
        # Look for any ID fields
        print("\n🔍 Searching for potential org IDs in token...")
        search_keys = ['org_uuid', 'org_id', 'organization_id', 'supplier_id', 
                      'partner_id', 'sub', 'iss', 'aud']
        for key in search_keys:
            if key in jwt_data:
                print(f"  Found '{key}': {jwt_data[key]}")
except Exception as e:
    print(f"Token decode error: {e}")

# Try to get app/partner info
print("\n" + "=" * 60)
print("CHECKING PARTNER/SUPPLIER INFO")
print("=" * 60)

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json",
}

# Sometimes the partner endpoint reveals org info
try:
    resp = requests.get("https://api.uber.com/v1/partners/me", headers=headers, timeout=10)
    print(f"GET /v1/partners/me: {resp.status_code}")
    if resp.status_code == 200:
        print(f"Response: {json.dumps(resp.json(), indent=2)[:500]}")
    elif resp.status_code != 404:
        print(f"Response: {resp.text[:300]}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("MANUAL ORG UUID INPUT")
print("=" * 60)
print("\nLook in your Uber Developer Dashboard under:")
print("  - Organization tab")
print("  - Fleet tab") 
print("  - Settings tab")
print("\nLook for a UUID that looks like:")
print("  abc123de-f456-7890-1234-567890abcdef")
print()

org_uuid = input("Paste your Org UUID here (or press Enter to skip): ").strip()

if org_uuid:
    print(f"\nTesting with org UUID: {org_uuid}")
    
    from datetime import datetime, timedelta
    
    start_date = "2026-06-08"  # Last week
    end_date = "2026-06-15"    # Today
    
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
    
    payload = {
        "reportRequests": [
            {
                "timeRanges": [
                    {
                        "startsAt": int(start_dt.timestamp() * 1000),
                        "endsAt": int(end_dt.timestamp() * 1000)
                    }
                ],
                "dimensions": [
                    {
                        "name": "vs:driver"
                    }
                ],
                "metrics": [
                    {
                        "expression": "vs:HoursOnline"
                    },
                    {
                        "expression": "vs:HoursOnTrip"
                    },
                    {
                        "expression": "vs:TotalTrips"
                    }
                ],
                "pagination_options": {
                    "pageSize": 10
                }
            }
        ],
        "orgId": {
            "orgUuid": org_uuid
        }
    }
    
    print("\nSending analytics request...")
    print(f"Payload: {json.dumps(payload, indent=2)[:500]}...")
    
    resp = requests.post(
        "https://api.uber.com/v1/vehicle-suppliers/analytics-data/query",
        json=payload,
        headers=headers,
        timeout=15
    )
    
    print(f"\nStatus: {resp.status_code}")
    if resp.status_code == 200:
        print("🎉 SUCCESS! API is working!")
        print(f"Response: {json.dumps(resp.json(), indent=2)[:2000]}")
    else:
        print(f"Response: {resp.text[:500]}")

