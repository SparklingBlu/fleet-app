import requests
import json
import base64

print("=" * 60)
print("DECODING JWT TOKEN DEEPLY")
print("=" * 60)

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

# Full JWT decode
try:
    parts = token.split('.')
    if len(parts) == 3:
        # Header
        header_padded = parts[0] + '=' * (4 - len(parts[0]) % 4)
        header = json.loads(base64.b64decode(header_padded))
        print(f"\nHeader: {json.dumps(header, indent=2)}")
        
        # Payload
        payload_padded = parts[1] + '=' * (4 - len(parts[1]) % 4)
        payload = json.loads(base64.b64decode(payload_padded))
        print(f"\nPayload: {json.dumps(payload, indent=2)}")
        
        # Look for ANY UUID-like fields
        print("\n🔍 ALL UUID-like fields found in token:")
        for key, value in payload.items():
            if isinstance(value, str) and len(value) > 30:
                print(f"  {key}: {value}")
            elif isinstance(value, dict):
                for k2, v2 in value.items():
                    if isinstance(v2, str) and len(v2) > 30:
                        print(f"  {key}.{k2}: {v2}")
except Exception as e:
    print(f"Decode error: {e}")

# Try with a broader scope
print("\n" + "=" * 60)
print("TRYING WITH BROADER SCOPE REQUEST")
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

print(f"Status: {auth_response.status_code}")
if auth_response.status_code == 200:
    print(f"Scope: {auth_response.json().get('scope')}")
else:
    print(f"Response: {auth_response.text}")

