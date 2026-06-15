import requests

CLIENT_ID = "5syO_-GOEpq7Ia_TChV9-0X57VtoRlbK"
CLIENT_SECRET = input("Paste your Uber Client Secret: ").strip()

# Try different auth URLs
auth_urls = [
    "https://auth.uber.com/oauth/v2/token",
    "https://login.uber.com/oauth/v2/token",
    "https://api.uber.com/oauth/v2/token",
]

payload = {
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "grant_type": "client_credentials",
    "scope": "solutions.suppliers.metrics.read",
}

headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}

for url in auth_urls:
    print(f"\nTrying: {url}")
    try:
        response = requests.post(url, data=payload, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS! Token: {data.get('access_token', '')[:50]}...")
            break
        else:
            print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

