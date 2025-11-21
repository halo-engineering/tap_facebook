"""
Facebook Graph API client with pagination and error handling.
"""

import requests
import singer
from typing import Dict, Iterator, Optional, List
from tap_facebook.auth import FacebookOAuthAuthenticator

LOGGER = singer.get_logger()


class FacebookClient:
    """Client for interacting with Facebook Graph API."""

    BASE_URL = "https://graph.facebook.com/v18.0"
    DEFAULT_PAGE_SIZE = 100

    def __init__(self, authenticator: FacebookOAuthAuthenticator):
        """
        Initialize the Facebook API client.

        Args:
            authenticator: OAuth authenticator instance
        """
        self.authenticator = authenticator

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        return {
            'Authorization': f'Bearer {self.authenticator.get_access_token()}',
            'Content-Type': 'application/json'
        }

    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_body: Optional[Dict] = None
    ) -> Dict:
        """
        Make an authenticated request to the Facebook Graph API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            params: Query parameters
            json_body: JSON body for POST requests

        Returns:
            Response JSON dictionary

        Raises:
            requests.exceptions.HTTPError: On HTTP errors
        """
        url = f"{self.BASE_URL}/{endpoint}"
        params = params or {}

        # Add access token to params (alternative to header)
        params['access_token'] = self.authenticator.get_access_token()

        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                json=json_body,
                timeout=30
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            LOGGER.error(f"HTTP error for {endpoint}: {e}")
            if e.response is not None:
                LOGGER.error(f"Response: {e.response.text}")
            raise

        except requests.exceptions.RequestException as e:
            LOGGER.error(f"Request failed for {endpoint}: {e}")
            raise

    def paginate(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        data_key: str = 'data'
    ) -> Iterator[Dict]:
        """
        Paginate through API results using cursor-based pagination.

        Args:
            endpoint: API endpoint to paginate
            params: Query parameters
            data_key: Key in response containing the data array

        Yields:
            Individual records from paginated results
        """
        params = params or {}
        params.setdefault('limit', self.DEFAULT_PAGE_SIZE)

        next_url = None
        page_count = 0

        while True:
            page_count += 1

            if next_url:
                # Use the full next URL provided by Facebook
                response = requests.get(
                    next_url,
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()
            else:
                # First request
                data = self.request('GET', endpoint, params=params)

            # Yield records from current page
            records = data.get(data_key, [])
            LOGGER.info(f"Page {page_count}: Retrieved {len(records)} records from {endpoint}")

            for record in records:
                yield record

            # Check for next page
            paging = data.get('paging', {})
            next_url = paging.get('next')

            if not next_url:
                LOGGER.info(f"Pagination complete for {endpoint}. Total pages: {page_count}")
                break

    def get_page_info(self, page_id: str) -> Dict:
        """
        Get information about a Facebook Page.

        Args:
            page_id: Facebook Page ID

        Returns:
            Page information dictionary
        """
        params = {
            'fields': 'id,name,username,fan_count,category,about'
        }
        return self.request('GET', page_id, params=params)

    def get_page_posts(
        self,
        page_id: str,
        fields: Optional[List[str]] = None,
        since: Optional[str] = None,
        until: Optional[str] = None
    ) -> Iterator[Dict]:
        """
        Get posts from a Facebook Page with engagement metrics.

        Args:
            page_id: Facebook Page ID
            fields: List of fields to retrieve
            since: Start date (Unix timestamp or strtotime)
            until: End date (Unix timestamp or strtotime)

        Yields:
            Post records with engagement data
        """
        if fields is None:
            fields = [
                'id',
                'message',
                'created_time',
                'updated_time',
                'permalink_url',
                'type',
                'status_type',
                'shares',
                'reactions.summary(total_count).limit(0)',
                'comments.summary(total_count).limit(0)',
                'likes.summary(total_count).limit(0)'
            ]

        params = {
            'fields': ','.join(fields)
        }

        if since:
            params['since'] = since
        if until:
            params['until'] = until

        endpoint = f"{page_id}/posts"
        yield from self.paginate(endpoint, params=params)

    def get_post_insights(self, post_id: str, metrics: Optional[List[str]] = None) -> List[Dict]:
        """
        Get insights/analytics for a specific post.

        Args:
            post_id: Facebook Post ID
            metrics: List of metric names to retrieve

        Returns:
            List of insight data points
        """
        if metrics is None:
            metrics = [
                'post_impressions',
                'post_impressions_unique',
                'post_engaged_users',
                'post_clicks',
                'post_reactions_by_type_total'
            ]

        params = {
            'metric': ','.join(metrics)
        }

        endpoint = f"{post_id}/insights"
        data = self.request('GET', endpoint, params=params)
        return data.get('data', [])

    def get_page_insights(
        self,
        page_id: str,
        metrics: Optional[List[str]] = None,
        period: str = 'day',
        since: Optional[str] = None,
        until: Optional[str] = None
    ) -> List[Dict]:
        """
        Get page-level insights/analytics.

        Args:
            page_id: Facebook Page ID
            metrics: List of metric names
            period: Time period (day, week, days_28)
            since: Start date
            until: End date

        Returns:
            List of insight data points
        """
        if metrics is None:
            metrics = [
                'page_impressions',
                'page_impressions_unique',
                'page_engaged_users',
                'page_post_engagements',
                'page_fans',
                'page_fan_adds',
                'page_fan_removes'
            ]

        params = {
            'metric': ','.join(metrics),
            'period': period
        }

        if since:
            params['since'] = since
        if until:
            params['until'] = until

        endpoint = f"{page_id}/insights"
        data = self.request('GET', endpoint, params=params)
        return data.get('data', [])
