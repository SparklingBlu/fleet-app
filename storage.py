# storage.py — GitHub Gist-based data persistence
# Enables shareable links that always show the latest published data

import streamlit as st
import json
import requests
from typing import Optional, Dict, Any


# ── CACHE BUSTING HELPER ──────────────────────────────────────────────────────
def _get_cache_buster() -> str:
    """Generate a simple cache buster to force fresh reads"""
    import time
    return str(int(time.time() / 60))  # Changes every minute


# ── STORAGE CHECK ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def is_storage_configured() -> bool:
    """
    Check if GitHub Gist storage is configured.
    Cached for 60 seconds to avoid checking secrets repeatedly.
    
    Returns:
        bool: True if both GITHUB_TOKEN and GIST_ID are configured
    """
    token = st.secrets.get("GITHUB_TOKEN")
    gist_id = st.secrets.get("GIST_ID")
    return bool(token and gist_id and token != "your_token_here" and gist_id != "your_gist_id_here")


# ── SAVE DATA ─────────────────────────────────────────────────────────────────
def save_fleet_data(data: Dict[str, Any]) -> bool:
    """
    Save fleet data to GitHub Gist.
    This is called from the Admin view when publishing data.
    
    Args:
        data: Dictionary containing fleet data, week info, metadata
        
    Returns:
        bool: True if save was successful
    """
    token = st.secrets.get("GITHUB_TOKEN")
    gist_id = st.secrets.get("GIST_ID")
    
    if not token or not gist_id:
        st.error("GitHub Gist not configured. Please add GITHUB_TOKEN and GIST_ID to Secrets.")
        return False
    
    url = f"https://api.github.com/gists/{gist_id}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    
    payload = {
        "files": {
            "fleet_data.json": {
                "content": json.dumps(data, indent=2, default=str)
            }
        }
    }
    
    try:
        response = requests.patch(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        # Clear the load cache so next read gets fresh data
        load_fleet_data.clear()
        return True
        
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to save data to Gist: {str(e)}")
        return False


# ── LOAD DATA ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=120, show_spinner=False)
def load_fleet_data() -> Optional[Dict[str, Any]]:
    """
    Load fleet data from GitHub Gist.
    Used by Driver, Fleet, and Team views.
    Cached for 2 minutes to balance freshness with performance.
    
    Returns:
        Optional dict containing fleet data, or None if not available
    """
    token = st.secrets.get("GITHUB_TOKEN")
    gist_id = st.secrets.get("GIST_ID")
    
    if not token or not gist_id:
        return None
    
    url = f"https://api.github.com/gists/{gist_id}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    
    # Add cache-busting parameter for fresh reads
    params = {"t": _get_cache_buster()}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        gist_data = response.json()
        files = gist_data.get("files", {})
        fleet_file = files.get("fleet_data.json", {})
        content = fleet_file.get("content", "{}")
        
        if isinstance(content, str):
            return json.loads(content)
        return content
        
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        st.warning(f"Could not load fleet data: {str(e)}")
        return None