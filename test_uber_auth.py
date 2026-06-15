import requests

CLIENT_ID = "5syO_-GOEpq7Ia_TChV9-0X57VtoRlbK"
CLIENT_SECRET = input("Paste your Uber Client Secret: ").strip()

AUTH_URL = "https://auth.uber.com/oauth/v2/token"

payload = {
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "grant_type": "client_credentials",
    "scope": "solutions.suppliers.metrics.read",
}

headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}

print("\nAttempting authentication...")
print(f"Client ID: {CLIENT_ID}")
print(f"Secret length: {len(CLIENT_SECRET)} characters")

try:
    response = requests.post(AUTH_URL, data=payload, headers=headers)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Authentication SUCCESS!")
        print(f"Access Token (first 50 chars): {data.get('access_token', 'N/A')[:50]}...")
        print(f"Token Type: {data.get('token_type')}")
        print(f"Expires In: {data.get('expires_in')} seconds")
        print(f"Scope: {data.get('scope')}")
    else:
        print(f"\n❌ Authentication FAILED")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"\n❌ Connection Error: {e}")
