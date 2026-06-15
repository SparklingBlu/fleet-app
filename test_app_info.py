import requests

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
    
    # Try partner/supplier info endpoints
    info_endpoints = [
        "https://api.uber.com/v1/partners/me",
        "https://api.uber.com/v1/suppliers/me",  
        "https://api.uber.com/v1/vehicle-suppliers/me",
        "https://api.uber.com/v1/fleet/me",
    ]
    
    for url in info_endpoints:
        print(f"GET {url}")
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            print(f"  Status: {resp.status_code}")
            if resp.status_code == 200:
                print(f"  ✅ Response: {resp.text[:500]}")
        except Exception as e:
            print(f"  Error: {e}")

except Exception as e:
    print(f"Fatal error: {e}")

