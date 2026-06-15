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

auth_response = requests.post(
    "https://auth.uber.com/oauth/v2/token",
    data=auth_payload,
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)

if auth_response.status_code != 200:
    print(f"Auth failed: {auth_response.text}")
    exit()

token = auth_response.json()["access_token"]
print("✅ Authenticated\n")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

url = "https://api.uber.com/v1/vehicle-suppliers/analytics-data/query"

# Test different field name patterns
test_cases = [
    # Test 1: CamelCase fields
    {
        "name": "CamelCase with reportType",
        "payload": {
            "reportRequests": [{
                "reportType": "DRIVER",
                "dateRange": {
                    "startDate": "2024-06-01",
                    "endDate": "2024-06-07"
                }
            }]
        }
    },
    # Test 2: snake_case fields
    {
        "name": "snake_case with report_type",
        "payload": {
            "reportRequests": [{
                "report_type": "DRIVER",
                "date_range": {
                    "start_date": "2024-06-01",
                    "end_date": "2024-06-07"
                }
            }]
        }
    },
    # Test 3: Flat structure
    {
        "name": "Flat structure",
        "payload": {
            "reportRequests": [{
                "type": "DRIVER",
                "startDate": "2024-06-01",
                "endDate": "2024-06-07"
            }]
        }
    },
    # Test 4: Query style
    {
        "name": "Query style",
        "payload": {
            "reportRequests": [{
                "query": {
                    "type": "DRIVER",
                    "start": "2024-06-01",
                    "end": "2024-06-07"
                }
            }]
        }
    },
    # Test 5: Request style
    {
        "name": "Request style",
        "payload": {
            "reportRequests": [{
                "request": {
                    "reportType": "DRIVER",
                    "start": "2024-06-01",
                    "end": "2024-06-07"
                }
            }]
        }
    },
    # Test 6: Filters style
    {
        "name": "Filters style",
        "payload": {
            "reportRequests": [{
                "filters": {
                    "reportType": "DRIVER",
                    "startDate": "2024-06-01",
                    "endDate": "2024-06-07"
                }
            }]
        }
    },
    # Test 7: Metrics only
    {
        "name": "Metrics focused",
        "payload": {
            "reportRequests": [{
                "metrics": ["HOURS_ONLINE"],
                "startDate": "2024-06-01",
                "endDate": "2024-06-07"
            }]
        }
    },
    # Test 8: Time range
    {
        "name": "Time range object",
        "payload": {
            "reportRequests": [{
                "timeRange": {
                    "start": "2024-06-01",
                    "end": "2024-06-07"
                }
            }]
        }
    },
    # Test 9: Period
    {
        "name": "Period based",
        "payload": {
            "reportRequests": [{
                "period": "WEEKLY",
                "weekStart": "2024-06-01"
            }]
        }
    },
    # Test 10: Minimal valid
    {
        "name": "Minimal",
        "payload": {
            "reportRequests": [{}]
        }
    },
]

for test in test_cases:
    print(f"\n{'='*60}")
    print(f"Test: {test['name']}")
    print(f"Payload: {json.dumps(test['payload'], indent=2)}")
    
    try:
        resp = requests.post(url, json=test['payload'], headers=headers, timeout=10)
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            print("🎉 SUCCESS! Found working format!")
            print(f"Response: {json.dumps(resp.json(), indent=2)[:1000]}")
            break
        elif resp.status_code == 400:
            error = resp.json().get('error', '')
            if 'reportRequests' in error:
                print(f"→ Same error: requires reportRequests")
            else:
                print(f"→ NEW ERROR: {error}")
                # This is progress! Different error means we're closer
                if 'reportType' in error.lower():
                    print("  → Issue is with reportType field")
                elif 'date' in error.lower():
                    print("  → Issue is with date fields")
                elif 'metric' in error.lower():
                    print("  → Issue is with metrics")
                else:
                    print("  → Unknown issue - examine this error carefully")
        elif resp.status_code == 401:
            print("Unauthorized")
        elif resp.status_code == 403:
            print("Forbidden - wrong scope")
        elif resp.status_code == 422:
            print(f"Validation Error: {resp.text[:300]}")
        else:
            print(f"Unexpected: {resp.text[:300]}")
            
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "="*60)
print("DIAGNOSTIC COMPLETE")
print("Look for any test that gave a DIFFERENT error from 'required field reportRequests'")
print("That will tell us which field structure is partially correct!")

