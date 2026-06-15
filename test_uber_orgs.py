import requests

CLIENT_ID = "5syO_-GOEpq7Ia_TChV9-0X57VtoRlbK"
CLIENT_SECRET = input("Paste your Uber Client Secret: ").strip()

# Get token first
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
    print(f"✅ Got token: {token[:50]}...")
    
    # Try different org endpoints
    org_urls = [
        "https://api.uber.com/v1/vehicle-suppliers/orgs",
        "https://api.uber.com/v1/organizations",
        "https://api.uber.com/v1/fleet/organizations",
    ]
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    for url in org_urls:
        print(f"\nTrying: {url}")
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ SUCCESS!")
            print(f"Response: {response.text[:500]}")
            break
        else:
            print(f"Response: {response.text[:200]}")
            
except Exception as e:
    print(f"Error: {e}")

