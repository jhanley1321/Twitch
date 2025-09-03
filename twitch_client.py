# pip install requests python-dotenv
import os
import time
import json
import requests
from typing import Optional

class TwitchCon:
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        self.client_id = client_id or os.getenv("TWITCH_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("TWITCH_CLIENT_SECRET")
        if not self.client_id or not self.client_secret:
            raise ValueError("Set TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET or pass them in.")

        self._token: Optional[str] = None
        self._expires_at: float = 0.0
        self.user_id: Optional[str] = None 
        # Auto-connect on initialization
        try:
            self.connect()
        except Exception as e:
            # Surface a clear error so callers know initialization failed due to auth/network.
            raise RuntimeError(f"TwitchCon initialization failed during connect(): {e}") from e

    def connect(self) -> bool:
        """Get an app access token. Returns True if successful."""
        url = "https://id.twitch.tv/oauth2/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }
        resp = requests.post(url, data=data, timeout=10)
        resp.raise_for_status()
        j = resp.json()
        self._token = j["access_token"]
        self._expires_at = time.time() + j.get("expires_in", 3600)
        return True

    def is_connected(self) -> bool:
        """Token exists and not expired."""
        return bool(self._token) and time.time() < self._expires_at - 30



    def disconnect(self) -> None:
        """Clear the token (no remote revoke)."""
        self._token = None
        self._expires_at = 0.0



 

 


    def get_user(self, login: str) -> dict:
        """Return Twitch user object for the given login (or empty dict if not found)."""
        if not login:
            raise ValueError("login is required")
        # ensure we have a valid token
        if not self.is_connected():
            self.connect()

        url = "https://api.twitch.tv/helix/users"
        headers = {"Client-ID": self.client_id, "Authorization": f"Bearer {self._token}"}
        resp = requests.get(url, headers=headers, params={"login": login}, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("data", [])
        self.user_id = data[0]["id"] if data else None
        self.user_name = data[0]["display_name"] if data else None
        result = data[0] if data else {}
        print(result)
        return result





    def get_user_id(self, login: str) -> dict:
        """
        Return all available fields Twitch currently provides for the given user login.
        Also pretty-prints the JSON to the console.
        """
        user = self.get_user(login)
        if not isinstance(user, dict) or not user:
            print(f"No Twitch user found for login '{login}'.")
            return {}

        print(json.dumps(user, indent=2, sort_keys=True))
      
        return user['id']



    def get_vod_ids(self, login: str, only_archive: bool = True) -> list:
        """
        Return a list of VOD IDs for the given streamer login.
        Simple synchronous implementation. Returns [] if streamer not found.
        """
        if not login:
            raise ValueError("login is required")

        # ensure token available
        if not self.is_connected():
            self.connect()

        # resolve user id using existing get_user()
        user = self.get_user(login)
        if not user:
            return []

        user_id = user.get("id")
        url = "https://api.twitch.tv/helix/videos"
        headers = {"Client-ID": self.client_id, "Authorization": f"Bearer {self._token}"}
        params = {"user_id": user_id, "first": 100}
        if only_archive:
            params["type"] = "archive"

        vod_ids = []
        while True:
            resp = requests.get(url, headers=headers, params=params, timeout=15)
            resp.raise_for_status()
            j = resp.json()
            vod_ids.extend([v.get("id") for v in j.get("data", []) if v.get("id")])
            cursor = j.get("pagination", {}).get("cursor")
            if not cursor:
                break
            params["after"] = cursor
        
        return vod_ids


