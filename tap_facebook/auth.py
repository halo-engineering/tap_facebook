"""
OAuth 2.0 authentication handler for Facebook Graph API.
"""

import time
import requests
from typing import Dict, Optional
import singer

LOGGER = singer.get_logger()


class FacebookOAuthAuthenticator:
    """Handles OAuth 2.0 authentication and token refresh for Facebook Graph API."""

    TOKEN_URL = "https://graph.facebook.com/v18.0/oauth/access_token"
    TOKEN_EXCHANGE_URL = "https://graph.facebook.com/v18.0/oauth/access_token"

    def __init__(self, config: Dict):
        """
        Initialize the authenticator.

        Args:
            config: Configuration dictionary containing OAuth credentials
        """
        self.client_id = config.get('client_id')
        self.client_secret = config.get('client_secret')
        self.refresh_token = config.get('refresh_token')
        self._access_token = config.get('access_token')
        self._token_expiry = config.get('token_expiry', 0)

    def get_access_token(self) -> str:
        """
        Get a valid access token, refreshing if necessary.

        Returns:
            Valid access token string
        """
        current_time = time.time()

        # If token is expired or about to expire (within 5 minutes), refresh it
        if not self._access_token or current_time >= (self._token_expiry - 300):
            LOGGER.info("Access token expired or missing, refreshing...")
            self._refresh_access_token()

        return self._access_token

    def _refresh_access_token(self) -> None:
        """Refresh the access token using the refresh token."""
        if not self.client_id or not self.client_secret:
            raise ValueError("client_id and client_secret are required for token refresh")

        # Facebook doesn't use traditional refresh tokens for long-lived tokens
        # Instead, we exchange the short-lived token for a long-lived one
        if self.refresh_token:
            params = {
                'grant_type': 'fb_exchange_token',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'fb_exchange_token': self.refresh_token
            }
        else:
            raise ValueError("refresh_token is required for authentication")

        try:
            response = requests.get(self.TOKEN_EXCHANGE_URL, params=params)
            response.raise_for_status()
            data = response.json()

            self._access_token = data.get('access_token')
            expires_in = data.get('expires_in', 5184000)  # Default to 60 days

            self._token_expiry = time.time() + expires_in

            LOGGER.info(f"Access token refreshed successfully. Expires in {expires_in} seconds.")

        except requests.exceptions.RequestException as e:
            LOGGER.error(f"Failed to refresh access token: {str(e)}")
            raise

    def get_long_lived_token(self, short_lived_token: str) -> Dict:
        """
        Exchange a short-lived user access token for a long-lived token.

        Args:
            short_lived_token: Short-lived access token from OAuth flow

        Returns:
            Dictionary containing access_token and expires_in
        """
        params = {
            'grant_type': 'fb_exchange_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'fb_exchange_token': short_lived_token
        }

        response = requests.get(self.TOKEN_EXCHANGE_URL, params=params)
        response.raise_for_status()

        return response.json()

    def validate_token(self) -> Dict:
        """
        Validate the current access token and get debug info.

        Returns:
            Dictionary containing token validation information
        """
        access_token = self.get_access_token()
        url = "https://graph.facebook.com/debug_token"
        params = {
            'input_token': access_token,
            'access_token': f"{self.client_id}|{self.client_secret}"
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        return response.json()
