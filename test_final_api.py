import requests
import json
from datetime import datetime, timedelta

CLIENT_ID = "5syO_-GOEpq7Ia_TChV9-0X57VtoRlbK"
CLIENT_SECRET = input("Paste your Uber Client Secret: ").strip()

ORG_UUID = "8B4z_AZXs0G7Vto_3jq_bGHEfZ3iy78wmMjlJU_SnvhuBn71eN64PJdqgxbSxJGY5GyPghQ-PNsBLM5tuJfq5HBYb28tWmQYtrwV1bwXBxIDmtEPDDdWZD13dOaq6xt0_Q=="

print("=" * 60)
print("STEP 1: Get token with both scopes")
print("=" * 60)

auth_response = requests.post(
    "https://auth.uber.com/oauth/v2/token",
    data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials",
        "scope": "vehicle_suppliers.organizations.read solutions.suppliers.metrics.read",
    },
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)

if auth_response.status_code != 200:
    print(f"Auth failed: {auth_response.text}")
    exit()

token = auth_response.json()["access_token"]
print(f"✅ Got token with scope: {auth_response.json().get('scope')}")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

print("\n" + "=" * 60)
print("STEP 2: Fetch driver analytics for SparklingBlu Moto")
print("=" * 60)

# Use recent dates (last 7 days)
end_date = datetime.now()
start_date = end_date - timedelta(days=7)

payload = {
    "reportRequests": [
        {
            "timeRanges": [
                {
                    "startsAt": int(start_date.timestamp() * 1000),
                    "endsAt": int(end_date.timestamp() * 1000)
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
                "pageSize": 100
            }
        }
    ],
    "orgId": {
        "orgUuid": ORG_UUID
    }
}

print(f"Date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
print(f"\nSending request...")

resp = requests.post(
    "https://api.uber.com/v1/vehicle-suppliers/analytics-data/query",
    json=payload,
    headers=headers,
    timeout=30
)

print(f"Status: {resp.status_code}")

if resp.status_code == 200:
    print("🎉 SUCCESS! Driver data received!")
    data = resp.json()
    
    # Pretty print the response
    print("\n" + "=" * 60)
    print("FULL RESPONSE:")
    print("=" * 60)
    print(json.dumps(data, indent=2)[:3000])
    
    # Parse and display drivers
    print("\n" + "=" * 60)
    print("PARSED DRIVER DATA:")
    print("=" * 60)
    
    body = data.get("body", data)
    reports = body.get("reports", [])
    
    for report in reports:
        column_header = report.get("columnHeader", {})
        dimension_headers = column_header.get("dimensionHeaderEntries", [])
        metric_headers = column_header.get("metricHeaderEntries", [])
        
        print(f"\nDimensions: {[h.get('name') for h in dimension_headers]}")
        print(f"Metrics: {[h.get('name') for h in metric_headers]}")
        
        time_range_data = report.get("data", {}).get("timeRangeData", [])
        
        for time_range in time_range_data:
            rows = time_range.get("rows", [])
            print(f"\nFound {len(rows)} drivers:")
            
            for row in rows:
                dim_values = row.get("dimensionValues", [])
                met_values = row.get("metricValues", [])
                
                # Build name
                first = dim_values[0] if len(dim_values) > 0 else ""
                last = dim_values[1] if len(dim_values) > 1 else ""
                name = f"{first} {last}".strip()
                
                hours_online = met_values[0] if len(met_values) > 0 else "0"
                hours_trip = met_values[1] if len(met_values) > 1 else "0"
                trips = met_values[2] if len(met_values) > 2 else "0"
                
                print(f"  {name}: {hours_online}h online, {hours_trip}h trip, {trips} trips")
    
elif resp.status_code == 400:
    print(f"Bad Request: {resp.text}")
elif resp.status_code == 403:
    print(f"Forbidden: {resp.text}")
else:
    print(f"Response: {resp.text[:500]}")

