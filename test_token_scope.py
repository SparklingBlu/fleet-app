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
    
    token_data = auth_response.json()
    token = token_data["access_token"]
    
    print("=" * 60)
    print("TOKEN INFORMATION")
    print("=" * 60)
    print(f"Scope: {token_data.get('scope')}")
    print(f"Expires: {token_data.get('expires_in')} seconds")
    print(f"Token (first 100 chars): {token[:100]}...")
    
    # Decode the JWT to see permissions (if it's a JWT)
    try:
        import base64
        import json
        
        # JWT has 3 parts: header.payload.signature
        parts = token.split('.')
        if len(parts) == 3:
            # Add padding
            payload = parts[1] + '=' * (4 - len(parts[1]) % 4)
            decoded = base64.b64decode(payload)
            jwt_data = json.loads(decoded)
            print(f"\nJWT Decoded:")
            print(json.dumps(jwt_data, indent=2))
    except:
        print("Token is not a standard JWT")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    # Test various fleet endpoints
    print("\n" + "=" * 60)
    print("TESTING ENDPOINTS")
    print("=" * 60)
    
    endpoints = [
        # Vehicle suppliers endpoints
        ("GET", "https://api.uber.com/v1/vehicle-suppliers/orgs"),
        ("GET", "https://api.uber.com/v1/vehicle-suppliers/organizations"),
        
        # Try POST for analytics directly (might not need orgs)
        ("POST", "https://api.uber.com/v1/vehicle-suppliers/analytics-data/query"),
        
        # Fleet endpoints
        ("GET", "https://api.uber.com/v1/fleet/vehicles"),
        ("GET", "https://api.uber.com/v1/fleet/drivers"),
        
        # Try without v1
        ("GET", "https://api.uber.com/vehicle-suppliers/orgs"),
        
        # Business endpoints
        ("GET", "https://api.uber.com/v1/business/organizations"),
    ]
    
    for method, url in endpoints:
        print(f"\n{method} {url}")
        try:
            if method == "GET":
                resp = requests.get(url, headers=headers, timeout=10)
            else:
                # For POST, send minimal valid payload
                payload = {
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-07"
                }
                resp = requests.post(url, json=payload, headers=headers, timeout=10)
            
            print(f"  Status: {resp.status_code}")
            if resp.status_code == 200:
                print(f"  ✅ SUCCESS!")
                print(f"  Response keys: {list(resp.json().keys()) if resp.json() else 'empty'}")
                print(f"  Sample: {str(resp.json())[:300]}")
            elif resp.status_code == 401:
                print(f"  ❌ Unauthorized - scope issue")
            elif resp.status_code == 403:
                print(f"  🚫 Forbidden - need different permissions")
            elif resp.status_code == 404:
                print(f"  📭 Not found - endpoint doesn't exist")
            else:
                print(f"  Response: {resp.text[:200]}")
                
        except Exception as e:
            print(f"  ⚠️ Error: {e}")
            
except Exception as e:
    print(f"Fatal error: {e}")

