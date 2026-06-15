import requests
import json

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

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# Try the organizations endpoint with different parameter formats
org_urls = [
    "https://api.uber.com/v1/vehicle-suppliers/orgs",
    "https://api.uber.com/v1/vehicle-suppliers/organizations",
]

for url in org_urls:
    print(f"GET {url}")
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"Response: {json.dumps(resp.json(), indent=2)[:1000]}")
        else:
            print(f"Response: {resp.text[:300]}")
    except Exception as e:
        print(f"Error: {e}")
    print()

