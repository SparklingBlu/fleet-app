# uber_client.py — Uber Fleet API Integration
# Phase 1: Supplier Performance Data API
# OAuth2 Client Credentials flow with caching

import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any


class UberAPIError(Exception):
    """Custom exception for Uber API errors"""
    pass


# ── CONSTANTS ─────────────────────────────────────────────────────────────────
BASE_URL     = "https://api.uber.com"
AUTH_URL     = "https://auth.uber.com/oauth/v2/token"
SCOPE = "vehicle_suppliers.organizations.read solutions.suppliers.metrics.read"
TOKEN_TTL    = 3300  # 55 minutes (token expires at 60 min)
DATA_TTL     = 900   # 15 minutes cache for analytics data
ORG_TTL      = 86400 # 24 hours cache for org IDs
MAX_RETRIES  = 3
RETRY_DELAY  = 2     # seconds between retries


# ── CACHED TOKEN GENERATION ──────────────────────────────────────────────────
@st.cache_resource(ttl=TOKEN_TTL)
def _get_uber_token() -> str:
    """
    Generate OAuth2 access token using Client Credentials.
    Cached for 55 minutes to avoid unnecessary auth calls.
    """
    client_id     = st.secrets.get("UBER_CLIENT_ID")
    client_secret = st.secrets.get("UBER_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        raise UberAPIError(
            "Missing Uber credentials. Please configure UBER_CLIENT_ID "
            "and UBER_CLIENT_SECRET in Streamlit Secrets."
        )
    
    auth_payload = {
        "client_id":     client_id,
        "client_secret": client_secret,
        "grant_type":    "client_credentials",
        "scope":         SCOPE,
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                AUTH_URL,
                data=auth_payload,
                headers=headers,
                timeout=15
            )
            response.raise_for_status()
            
            token_data = response.json()
            access_token = token_data.get("access_token")
            
            if not access_token:
                raise UberAPIError("No access token in response")
            
            return access_token
            
        except requests.exceptions.RequestException as e:
            if attempt == MAX_RETRIES - 1:
                raise UberAPIError(
                    f"Authentication failed after {MAX_RETRIES} attempts: {str(e)}"
                )
            time.sleep(RETRY_DELAY * (attempt + 1))
    
    raise UberAPIError("Unexpected authentication error")


# ── CACHED ORGANIZATION IDS ──────────────────────────────────────────────────
@st.cache_data(ttl=ORG_TTL)
def _get_organization_uuids(access_token: str) -> List[str]:
    """
    Retrieve encrypted organization UUIDs from Get Organizations API.
    Cached for 24 hours since org structure rarely changes.
    
    Returns:
        List of encrypted org UUIDs
    """
    # First check if manually provided in secrets
    manual_org = st.secrets.get("UBER_ORG_UUID")
    if manual_org and manual_org not in ["PLACEHOLDER", "your-org-uuid-here", ""]:
        return [manual_org]
    
    url = f"{BASE_URL}/v1/vehicle-suppliers/orgs"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type":  "application/json",
        "Accept":        "application/json",
    }
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 401:
                raise UberAPIError(
                    "Cannot access organizations API. Your app may not have "
                    "the required permissions. Please add UBER_ORG_UUID to "
                    "Streamlit Secrets manually."
                )
            
            response.raise_for_status()
            
            data = response.json()
            
            # Parse organization UUIDs from response
            orgs = data.get("organizations", [])
            org_uuids = []
            
            for org in orgs:
                org_uuid = org.get("orgUuid") or org.get("organizationUuid") or org.get("id")
                if org_uuid:
                    org_uuids.append(org_uuid)
            
            if not org_uuids:
                raise UberAPIError(
                    "No organizations found. Please add UBER_ORG_UUID to secrets. "
                    "You can find this in your Uber Developer Dashboard."
                )
            
            return org_uuids
            
        except requests.exceptions.RequestException as e:
            if attempt == MAX_RETRIES - 1:
                raise UberAPIError(
                    f"Failed to fetch organizations after {MAX_RETRIES} attempts. "
                    f"Add UBER_ORG_UUID to Streamlit Secrets. Error: {str(e)}"
                )
            time.sleep(RETRY_DELAY * (attempt + 1))
    
    raise UberAPIError("Unexpected error fetching organizations")


# ── ANALYTICS DATA FETCH (CORRECTED WITH DOCUMENTATION) ──────────────────────
@st.cache_data(ttl=DATA_TTL)
def _fetch_analytics_data(
    access_token: str,
    org_uuid: str,
    start_date: str,
    end_date: str
) -> Dict[str, Any]:
    """
    Fetch driver analytics data from Supplier Performance Data API.
    
    Uses the exact payload format from Uber's documentation:
    - timeRanges with UNIX milliseconds timestamps
    - dimensions with vs:driver
    - metrics with vs: prefix
    - orgId as object with orgUuid
    """
    url = f"{BASE_URL}/v1/vehicle-suppliers/analytics-data/query"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type":  "application/json",
        "Accept":        "application/json",
    }
    
    # Convert dates to UNIX milliseconds timestamps
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
    
    starts_at_ms = int(start_dt.timestamp() * 1000)
    ends_at_ms = int(end_dt.timestamp() * 1000)
    
    payload = {
        "reportRequests": [
            {
                "timeRanges": [
                    {
                        "startsAt": starts_at_ms,
                        "endsAt": ends_at_ms
                    }
                ],
                "dimensions": [
                    {
                        "name": "vs:driver"
                    }
                ],
                "metrics": [
                    {
                        "expression": "vs:HoursOnline"
                    },
                    {
                        "expression": "vs:HoursOnTrip"
                    },
                    {
                        "expression": "vs:TotalTrips"
                    }
                ],
                "pagination_options": {
                    "pageSize": 100
                }
            }
        ],
        "orgId": {
            "orgUuid": org_uuid
        }
    }
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            if attempt == MAX_RETRIES - 1:
                error_detail = ""
                try:
                    error_detail = response.text if 'response' in locals() else "No response"
                except:
                    pass
                    
                raise UberAPIError(
                    f"Failed to fetch analytics data after {MAX_RETRIES} attempts. "
                    f"Detail: {error_detail}"
                )
            time.sleep(RETRY_DELAY * (attempt + 1))
    
    raise UberAPIError("Unexpected error fetching analytics data")


# ── RESPONSE PARSING ─────────────────────────────────────────────────────────
def _parse_driver_data(api_response: Dict[str, Any]) -> pd.DataFrame:
    """
    Parse the complex Uber API response into a simple DataFrame.
    
    Response structure:
    {
        "body": {
            "reports": [{
                "columnHeader": {
                    "dimensionHeaderEntries": [...],
                    "metricHeaderEntries": [...]
                },
                "data": {
                    "timeRangeData": [{
                        "rows": [{
                            "dimensionValues": ["FirstName", "LastName", "Phone", "Email"],
                            "metricValues": ["hours_online", "hours_trip", "trips"]
                        }]
                    }]
                }
            }]
        }
    }
    """
    all_drivers = []
    
    # Navigate the response structure
    body = api_response.get("body", api_response)
    reports = body.get("reports", [])
    
    for report in reports:
        # Get column headers to understand field order
        column_header = report.get("columnHeader", {})
        dimension_headers = column_header.get("dimensionHeaderEntries", [])
        metric_headers = column_header.get("metricHeaderEntries", [])
        
        # Get dimension field names and indices
        first_name_idx = None
        last_name_idx = None
        
        for i, header in enumerate(dimension_headers):
            name = header.get("name", "")
            if name == "FirstName":
                first_name_idx = i
            elif name == "LastName":
                last_name_idx = i
        
        # Get metric field names and indices
        hours_online_idx = None
        hours_trip_idx = None
        total_trips_idx = None
        
        for i, header in enumerate(metric_headers):
            name = header.get("name", "")
            if name == "HoursOnline":
                hours_online_idx = i
            elif name == "HoursOnTrip":
                hours_trip_idx = i
            elif name == "TotalTrips":
                total_trips_idx = i
        
        # Extract data rows
        data = report.get("data", {})
        time_range_data = data.get("timeRangeData", [])
        
        for time_range in time_range_data:
            rows = time_range.get("rows", [])
            
            for row in rows:
                dimension_values = row.get("dimensionValues", [])
                metric_values = row.get("metricValues", [])
                
                # Build driver name from first and last name
                first_name = dimension_values[first_name_idx] if first_name_idx is not None and first_name_idx < len(dimension_values) else ""
                last_name = dimension_values[last_name_idx] if last_name_idx is not None and last_name_idx < len(dimension_values) else ""
                driver_name = f"{first_name} {last_name}".strip()
                
                if not driver_name:
                    driver_name = row.get("dimensionId", "Unknown Driver")
                
                # Extract metrics
                hours_online = _safe_float(metric_values[hours_online_idx]) if hours_online_idx is not None and hours_online_idx < len(metric_values) else 0.0
                hours_on_trip = _safe_float(metric_values[hours_trip_idx]) if hours_trip_idx is not None and hours_trip_idx < len(metric_values) else 0.0
                total_trips = _safe_int(metric_values[total_trips_idx]) if total_trips_idx is not None and total_trips_idx < len(metric_values) else 0
                
                all_drivers.append({
                    "Driver": driver_name,
                    "Hours Online": hours_online,
                    "Hours on Trip": hours_on_trip,
                    "Total Trips": total_trips,
                })
    
    if not all_drivers:
        raise UberAPIError(
            "No driver data found in API response. The date range may have no activity."
        )
    
    df = pd.DataFrame(all_drivers)
    
    # Remove duplicates by driver name
    df = df.drop_duplicates(subset=["Driver"], keep="first")
    
    # Round numeric columns
    df["Hours Online"] = df["Hours Online"].round(1)
    df["Hours on Trip"] = df["Hours on Trip"].round(1)
    
    return df


# ── UTILITY FUNCTIONS ────────────────────────────────────────────────────────
def _safe_float(value: Any) -> float:
    """Safely convert value to float, returning 0.0 on failure"""
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _safe_int(value: Any) -> int:
    """Safely convert value to int, returning 0 on failure"""
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


# ── PUBLIC API ────────────────────────────────────────────────────────────────
def fetch_live_driver_data(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> pd.DataFrame:
    """
    Main public function to fetch live driver data from Uber API.
    
    1. Authenticate with OAuth2
    2. Discover organization UUIDs
    3. Fetch analytics data for each org
    4. Parse and return standardized DataFrame
    
    Args:
        start_date: Start date in ISO format (YYYY-MM-DD). Defaults to 7 days ago.
        end_date: End date in ISO format (YYYY-MM-DD). Defaults to today.
        
    Returns:
        pd.DataFrame with driver metrics
    """
    # Default date range: last 7 days
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if not start_date:
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    # Step 1: Get access token
    token = _get_uber_token()
    
    # Step 2: Get organization UUIDs
    org_uuids = _get_organization_uuids(token)
    
    # Step 3: Fetch data for each organization
    all_dfs = []
    for org_uuid in org_uuids:
        response = _fetch_analytics_data(token, org_uuid, start_date, end_date)
        
        # Store raw response for debugging
        st.session_state["uber_raw_response"] = response
        
        df = _parse_driver_data(response)
        all_dfs.append(df)
    
    # Step 4: Combine all orgs
    if len(all_dfs) > 1:
        final_df = pd.concat(all_dfs, ignore_index=True)
        final_df = final_df.drop_duplicates(subset=["Driver"], keep="first")
    else:
        final_df = all_dfs[0]
    
    return final_df


# ── DEVELOPMENT FALLBACK ─────────────────────────────────────────────────────
def fetch_sample_driver_data() -> pd.DataFrame:
    """
    Returns sample driver data for testing when API is unavailable.
    REMOVE OR COMMENT OUT IN PRODUCTION.
    """
    import random
    
    sample_drivers = [
        "John Msosa", "Peter Banda", "Grace Phiri", "David Chirwa",
        "Mary Tembo", "James Banda", "Elizabeth Mwale", "Michael Daka",
        "Sarah Jere", "Robert Ngoma", "Patricia Lungu", "William Mumba",
        "Catherine Phiri", "Joseph Zulu", "Margaret Soko"
    ]
    
    data = []
    for name in sample_drivers:
        hours_online = round(random.uniform(5, 60), 1)
        hours_trip = round(hours_online * random.uniform(0.3, 0.8), 1)
        trips = int(hours_trip * random.uniform(1.5, 4))
        
        data.append({
            "Driver": name,
            "Hours Online": hours_online,
            "Hours on Trip": hours_trip,
            "Total Trips": trips,
        })
    
    return pd.DataFrame(data)