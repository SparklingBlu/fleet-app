import requests
import json

CLIENT_ID = "5syO_-GOEpq7Ia_TChV9-0X57VtoRlbK"
CLIENT_SECRET = input("Paste your Uber Client Secret: ").strip()

# Try getting token with BOTH scopes
scopes_to_try = [
    "solutions.suppliers.metrics.read vehicle_suppliers.organizations.read",
    "vehicle_suppliers.organizations.read solutions.suppliers.metrics.read",
    "solutions.suppliers.metrics.read",
    "vehicle_suppliers.organizations.read",
]

for scope in scopes_to_try:
    print(f"\n{'='*60}")
    print(f"Trying scope: {scope}")
    print('='*60)
    
    auth_response = requests.post(
        "https://auth.uber.com/oauth/v2/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "client_credentials",
            "scope": scope,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    print(f"Status: {auth_response.status_code}")
    
    if auth_response.status_code == 200:
        token_data = auth_response.json()
        print(f"✅ Got token!")
        print(f"Scope returned: {token_data.get('scope')}")
        
        token = token_data["access_token"]
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
        
        # Try the orgs endpoint
        resp = requests.get(
            "https://api.uber.com/v1/vehicle-suppliers/orgs",
            headers=headers,
            timeout=10
        )
        
        print(f"\nGET /v1/vehicle-suppliers/orgs: {resp.status_code}")
        if resp.status_code == 200:
            print("🎉 ORGANIZATIONS FOUND!")
            data = resp.json()
            print(json.dumps(data, indent=2)[:2000])
            
            # Extract org UUIDs
            orgs = data.get("organizations", [])
            for org in orgs:
                print(f"\nOrg: {org}")
                if "orgUuid" in org:
                    print(f"  → Use this UUID: {org['orgUuid']}")
        else:
            print(f"Response: {resp.text[:300]}")
    else:
        print(f"Failed: {auth_response.text[:300]}")

