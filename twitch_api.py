# twitch_api.py
import os
import requests
from dotenv import load_dotenv
from functools import wraps
import time
from decorators import retry_on_failure  # Import the decorator

class TwitchAPI:
    def __init__(self):
        load_dotenv()
        self._client_id = os.getenv("TWITCH_CLIENT_ID")
        self._client_secret = os.getenv("TWITCH_CLIENT_SECRET")
        self._access_token = None
        self._base_url = "https://api.twitch.tv/helix"
        self._validate_credentials()
    
    def _validate_credentials(self):
        """Validate that required credentials are present"""
        if not self._client_id or not self._client_secret:
            raise ValueError("TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET must be set in .env file")
    
    @property
    def client_id(self):
        """Get client ID"""
        return self._client_id
    
    @client_id.setter
    def client_id(self, value):
        """Set client ID"""
        if not value:
            raise ValueError("Client ID cannot be empty")
        self._client_id = value
        self._access_token = None  # Reset token when credentials change
    
    @property
    def client_secret(self):
        """Get client secret (masked for security)"""
        return "*" * len(self._client_secret) if self._client_secret else None
    
    @client_secret.setter
    def client_secret(self, value):
        """Set client secret"""
        if not value:
            raise ValueError("Client secret cannot be empty")
        self._client_secret = value
        self._access_token = None  # Reset token when credentials change
    
    @property
    def base_url(self):
        """Get base URL"""
        return self._base_url
    
    @property
    def is_authenticated(self):
        """Check if API is authenticated"""
        return self._access_token is not None
    
    @retry_on_failure(max_retries=3, delay=1)
    def _get_access_token(self):
        """Get app access token from Twitch"""
        auth_url = 'https://id.twitch.tv/oauth2/token'
        auth_params = {
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'grant_type': 'client_credentials'
        }
        response = requests.post(auth_url, params=auth_params)
        response.raise_for_status()
        self._access_token = response.json()['access_token']
        return self._access_token
    
    def _get_headers(self):
        """Get headers for API requests"""
        if not self._access_token:
            self._get_access_token()
        
        return {
            'Client-ID': self._client_id,
            'Authorization': f'Bearer {self._access_token}'
        }
    
    @retry_on_failure(max_retries=3, delay=1)
    def get_data(self, endpoint, params=None):
        """Generic method to get data from Twitch API"""
        if not endpoint:
            raise ValueError("Endpoint cannot be empty")
        
        url = f"{self._base_url}/{endpoint}"
        response = requests.get(url, headers=self._get_headers(), params=params)
        response.raise_for_status()
        return response.json()
    
    def get_user(self, username):
        """Get user info by username"""
        if not username:
            raise ValueError("Username cannot be empty")
        
        data = self.get_data('users', params={'login': username})
        return data['data'][0] if data['data'] else None
    
    def get_top_games(self, limit=5):
        """Get top games"""
        if limit <= 0 or limit > 100:
            raise ValueError("Limit must be between 1 and 100")
        
        data = self.get_data('games/top', params={'first': limit})
        return data['data']
    
    def get_streams(self, username=None, game_id=None, limit=20):
        """Get live streams"""
        if limit <= 0 or limit > 100:
            raise ValueError("Limit must be between 1 and 100")
        
        params = {'first': limit}
        if username:
            user = self.get_user(username)
            if user:
                params['user_id'] = user['id']
        if game_id:
            params['game_id'] = game_id
        
        data = self.get_data('streams', params=params)
        return data['data']
    
    def refresh_token(self):
        """Force refresh the access token"""
        self._access_token = None
        return self._get_access_token()
    
    def __str__(self):
        """String representation of the API instance"""
        return f"TwitchAPI(authenticated={self.is_authenticated})"
    
    def __repr__(self):
        """Developer representation of the API instance"""
        return f"TwitchAPI(client_id='{self.client_id[:8]}...', authenticated={self.is_authenticated})"