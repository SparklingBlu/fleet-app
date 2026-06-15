import requests

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
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json",
}

# Try to get API schema/documentation
schema_urls = [
    "https://api.uber.com/v1/vehicle-suppliers/analytics-data",
    "https://api.uber.com/v1/vehicle-suppliers/analytics-data/schema",
    "https://api.uber.com/v1/vehicle-suppliers/analytics-data/query/schema",
    "https://developer.uber.com/docs/vehicle-suppliers/analytics-data",
]

for url in schema_urls:
    print(f"\nGET {url}")
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"Response: {resp.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")

# Also try OPTIONS to see allowed methods
print(f"\nOPTIONS https://api.uber.com/v1/vehicle-suppliers/analytics-data/query")
try:
    resp = requests.options(
        "https://api.uber.com/v1/vehicle-suppliers/analytics-data/query",
        headers=headers,
        timeout=10
    )
    print(f"Status: {resp.status_code}")
    print(f"Headers: {dict(resp.headers)}")
except Exception as e:
    print(f"Error: {e}")

