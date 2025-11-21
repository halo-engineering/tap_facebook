"""Post insights stream for detailed engagement analytics."""

import singer
from typing import Dict, Iterator, Optional
from tap_facebook.streams.base import FacebookStream

LOGGER = singer.get_logger()


class PostInsightsStream(FacebookStream):
    """Stream for Facebook post-level insights and analytics."""

    name = "post_insights"
    replication_method = "FULL_TABLE"  # Insights are typically refreshed fully
    replication_key = None
    key_properties = ["post_id", "metric_name"]

    schema = {
        "post_id": {
            "type": ["null", "string"],
            "description": "Facebook Post ID"
        },
        "metric_name": {
            "type": ["null", "string"],
            "description": "Name of the metric"
        },
        "metric_value": {
            "type": ["null", "integer"],
            "description": "Value of the metric"
        },
        "metric_title": {
            "type": ["null", "string"],
            "description": "Human-readable metric title"
        },
        "metric_description": {
            "type": ["null", "string"],
            "description": "Description of what the metric measures"
        },
        "period": {
            "type": ["null", "string"],
            "description": "Time period for the metric (lifetime, day, etc.)"
        }
    }

    # Post insights metrics available from Facebook
    AVAILABLE_METRICS = [
        'post_impressions',              # Total impressions
        'post_impressions_unique',       # Unique impressions
        'post_impressions_paid',         # Paid impressions
        'post_impressions_organic',      # Organic impressions
        'post_engaged_users',            # Users who engaged
        'post_clicks',                   # Total clicks
        'post_clicks_unique',            # Unique clicks
        'post_reactions_by_type_total'   # Reactions broken down by type
    ]

    def get_records(self, state: Optional[Dict] = None) -> Iterator[Dict]:
        """
        Retrieve post insight records.

        Args:
            state: Current state (unused for full table replication)

        Yields:
            Post insight record dictionaries
        """
        page_id = self.config.get('page_id')
        if not page_id:
            raise ValueError("page_id is required in configuration")

        # First, get all posts to fetch insights for
        LOGGER.info(f"Fetching posts to retrieve insights for page {page_id}")

        posts = list(self.client.get_page_posts(
            page_id=page_id,
            fields=['id'],
            since=self.config.get('start_date')
        ))

        LOGGER.info(f"Fetching insights for {len(posts)} posts")

        for post in posts:
            post_id = post['id']

            try:
                insights = self.client.get_post_insights(
                    post_id=post_id,
                    metrics=self.AVAILABLE_METRICS
                )

                for insight in insights:
                    records = self._transform_insight(insight, post_id)
                    for record in records:
                        yield record

            except Exception as e:
                # Some posts may not have insights available
                LOGGER.warning(f"Could not fetch insights for post {post_id}: {str(e)}")
                continue

    def _transform_insight(self, insight: Dict, post_id: str) -> Iterator[Dict]:
        """
        Transform raw insight data to schema format.

        Args:
            insight: Raw insight data from API
            post_id: Facebook Post ID

        Yields:
            Transformed insight record dictionaries
        """
        metric_name = insight.get('name')
        period = insight.get('period')
        title = insight.get('title')
        description = insight.get('description')

        # Insights can have multiple values (e.g., breakdown by type)
        values = insight.get('values', [])

        for value_obj in values:
            value = value_obj.get('value')

            # Handle different value types
            if isinstance(value, dict):
                # For metrics like reactions_by_type_total
                for key, count in value.items():
                    yield {
                        'post_id': post_id,
                        'metric_name': f"{metric_name}_{key}",
                        'metric_value': count,
                        'metric_title': f"{title} - {key}",
                        'metric_description': description,
                        'period': period
                    }
            elif isinstance(value, (int, float)):
                yield {
                    'post_id': post_id,
                    'metric_name': metric_name,
                    'metric_value': int(value),
                    'metric_title': title,
                    'metric_description': description,
                    'period': period
                }
