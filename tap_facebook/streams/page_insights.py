"""Page insights stream for page-level analytics."""

import singer
from typing import Dict, Iterator, Optional
from datetime import datetime, timedelta
from tap_facebook.streams.base import FacebookStream

LOGGER = singer.get_logger()


class PageInsightsStream(FacebookStream):
    """Stream for Facebook page-level insights and analytics."""

    name = "page_insights"
    replication_method = "INCREMENTAL"
    replication_key = "date"
    key_properties = ["page_id", "metric_name", "date"]

    schema = {
        "page_id": {
            "type": ["null", "string"],
            "description": "Facebook Page ID"
        },
        "date": {
            "type": ["null", "string"],
            "format": "date",
            "description": "Date of the metric"
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
            "description": "Time period for the metric (day, week, days_28)"
        }
    }

    # Page-level metrics available from Facebook
    DAILY_METRICS = [
        'page_impressions',              # Total page impressions
        'page_impressions_unique',       # Unique page impressions
        'page_impressions_paid',         # Paid page impressions
        'page_impressions_organic',      # Organic page impressions
        'page_engaged_users',            # Users who engaged with page
        'page_post_engagements',         # Total post engagements
        'page_consumptions',             # Page consumptions
        'page_consumptions_unique',      # Unique page consumptions
        'page_fans',                     # Total page fans (lifetime)
        'page_fan_adds',                 # New page fans
        'page_fan_removes',              # Page fan removals
        'page_views_total',              # Total page views
        'page_views_logged_in_unique',   # Unique logged-in page views
        'page_video_views',              # Video views on page
        'page_posts_impressions',        # Impressions from page posts
        'page_posts_impressions_unique', # Unique impressions from posts
    ]

    def get_records(self, state: Optional[Dict] = None) -> Iterator[Dict]:
        """
        Retrieve page insight records.

        Args:
            state: Current state for incremental syncing

        Yields:
            Page insight record dictionaries
        """
        page_id = self.config.get('page_id')
        if not page_id:
            raise ValueError("page_id is required in configuration")

        # Get bookmark from state for incremental sync
        state = state or {}
        last_date = state.get(self.name, {}).get(self.replication_key)
        start_date = last_date or self.config.get('start_date')

        LOGGER.info(f"Syncing page insights for page {page_id} since {start_date}")

        # Calculate date range (Facebook allows max 93 days)
        since = self._parse_date(start_date)
        until = datetime.utcnow().date()

        # Split into chunks if needed (93-day limit)
        date_chunks = self._split_date_range(since, until, max_days=90)

        max_date = start_date

        for chunk_since, chunk_until in date_chunks:
            LOGGER.info(f"Fetching insights from {chunk_since} to {chunk_until}")

            try:
                insights = self.client.get_page_insights(
                    page_id=page_id,
                    metrics=self.DAILY_METRICS,
                    period='day',
                    since=chunk_since.isoformat(),
                    until=chunk_until.isoformat()
                )

                for insight in insights:
                    records = self._transform_insight(insight, page_id)
                    for record in records:
                        # Track the latest date for state
                        if record.get('date') and record['date'] > max_date:
                            max_date = record['date']

                        yield record

            except Exception as e:
                LOGGER.error(f"Error fetching page insights: {str(e)}")
                raise

        # Update state with latest bookmark
        if max_date:
            state[self.name] = {self.replication_key: max_date}
            self.write_state(state)

    def _transform_insight(self, insight: Dict, page_id: str) -> Iterator[Dict]:
        """
        Transform raw insight data to schema format.

        Args:
            insight: Raw insight data from API
            page_id: Facebook Page ID

        Yields:
            Transformed insight record dictionaries
        """
        metric_name = insight.get('name')
        period = insight.get('period')
        title = insight.get('title')
        description = insight.get('description')

        # Insights have time-series values
        values = insight.get('values', [])

        for value_obj in values:
            end_time = value_obj.get('end_time')
            value = value_obj.get('value')

            # Parse date from end_time
            date = self._parse_datetime(end_time).date().isoformat() if end_time else None

            if isinstance(value, (int, float)):
                yield {
                    'page_id': page_id,
                    'date': date,
                    'metric_name': metric_name,
                    'metric_value': int(value),
                    'metric_title': title,
                    'metric_description': description,
                    'period': period
                }

    def _parse_date(self, date_str: str) -> datetime.date:
        """Parse date string to date object."""
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
        except Exception:
            return datetime.strptime(date_str[:10], '%Y-%m-%d').date()

    def _parse_datetime(self, datetime_str: str) -> datetime:
        """Parse datetime string to datetime object."""
        return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))

    def _split_date_range(self, start: datetime.date, end: datetime.date, max_days: int = 90) -> Iterator:
        """
        Split a date range into chunks.

        Args:
            start: Start date
            end: End date
            max_days: Maximum days per chunk

        Yields:
            Tuples of (chunk_start, chunk_end)
        """
        current = start

        while current <= end:
            chunk_end = min(current + timedelta(days=max_days), end)
            yield (current, chunk_end)
            current = chunk_end + timedelta(days=1)
