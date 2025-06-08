# twitch_api.py
import os
import requests
from dotenv import load_dotenv

class TwitchAPI:
    def __init__(self):
        load_dotenv()
        self.client_id = os.getenv("TWITCH_CLIENT_ID")
        self.client_secret = os.getenv("TWITCH_CLIENT_SECRET")
        self.access_token = None
        self.base_url = "https://api.twitch.tv/helix"
    
    def _get_access_token(self):
        """Get app access token from Twitch"""
        auth_url = 'https://id.twitch.tv/oauth2/token'
        auth_params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        response = requests.post(auth_url, params=auth_params)
        response.raise_for_status()
        self.access_token = response.json()['access_token']
    
    def _get_headers(self):
        """Get headers for API requests"""
        if not self.access_token:
            self._get_access_token()
        
        return {
            'Client-ID': self.client_id,
            'Authorization': f'Bearer {self.access_token}'
        }
    
    def get_data(self, endpoint, params=None):
        """Generic method to get data from Twitch API"""
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, headers=self._get_headers(), params=params)
        response.raise_for_status()
        return response.json()
    
    def get_user(self, username):
        """Get user info by username"""
        data = self.get_data('users', params={'login': username})
        return data['data'][0] if data['data'] else None
    
    def get_top_games(self, limit=5):
        """Get top games"""
        data = self.get_data('games/top', params={'first': limit})
        return data['data']