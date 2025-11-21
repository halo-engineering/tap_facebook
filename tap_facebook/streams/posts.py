"""Posts stream for Facebook engagement data."""

import singer
from typing import Dict, Iterator, Optional
from datetime import datetime
from tap_facebook.streams.base import FacebookStream

LOGGER = singer.get_logger()


class PostsStream(FacebookStream):
    """Stream for Facebook Page posts with engagement metrics."""

    name = "posts"
    replication_method = "INCREMENTAL"
    replication_key = "updated_time"
    key_properties = ["id"]

    schema = {
        "id": {
            "type": ["null", "string"],
            "description": "Unique post ID"
        },
        "message": {
            "type": ["null", "string"],
            "description": "Post message content"
        },
        "created_time": {
            "type": ["null", "string"],
            "format": "date-time",
            "description": "Time the post was created"
        },
        "updated_time": {
            "type": ["null", "string"],
            "format": "date-time",
            "description": "Time the post was last updated"
        },
        "permalink_url": {
            "type": ["null", "string"],
            "format": "uri",
            "description": "Permanent URL to the post"
        },
        "type": {
            "type": ["null", "string"],
            "description": "Post type (link, status, photo, video, offer)"
        },
        "status_type": {
            "type": ["null", "string"],
            "description": "Status type of the post"
        },
        "likes_count": {
            "type": ["null", "integer"],
            "description": "Total number of likes"
        },
        "comments_count": {
            "type": ["null", "integer"],
            "description": "Total number of comments"
        },
        "shares_count": {
            "type": ["null", "integer"],
            "description": "Total number of shares"
        },
        "reactions_count": {
            "type": ["null", "integer"],
            "description": "Total number of reactions (all types)"
        },
        "page_id": {
            "type": ["null", "string"],
            "description": "Facebook Page ID that owns this post"
        }
    }

    def get_records(self, state: Optional[Dict] = None) -> Iterator[Dict]:
        """
        Retrieve post records with engagement metrics.

        Args:
            state: Current state for incremental syncing

        Yields:
            Post record dictionaries
        """
        page_id = self.config.get('page_id')
        if not page_id:
            raise ValueError("page_id is required in configuration")

        # Get bookmark from state for incremental sync
        state = state or {}
        last_updated = state.get(self.name, {}).get(self.replication_key)
        start_date = last_updated or self.config.get('start_date')

        LOGGER.info(f"Syncing posts for page {page_id} since {start_date}")

        # Define fields to retrieve
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

        # Fetch posts from Facebook API
        posts = self.client.get_page_posts(
            page_id=page_id,
            fields=fields,
            since=start_date
        )

        max_updated_time = start_date

        for post in posts:
            # Transform post data
            record = self._transform_post(post, page_id)

            # Track the latest updated_time for state
            if record.get('updated_time') and record['updated_time'] > max_updated_time:
                max_updated_time = record['updated_time']

            yield record

        # Update state with latest bookmark
        if max_updated_time:
            state[self.name] = {self.replication_key: max_updated_time}
            self.write_state(state)

    def _transform_post(self, post: Dict, page_id: str) -> Dict:
        """
        Transform raw Facebook post data to schema format.

        Args:
            post: Raw post data from API
            page_id: Facebook Page ID

        Returns:
            Transformed record dictionary
        """
        # Extract engagement counts safely
        likes_count = post.get('likes', {}).get('summary', {}).get('total_count', 0)
        comments_count = post.get('comments', {}).get('summary', {}).get('total_count', 0)
        shares_count = post.get('shares', {}).get('count', 0)
        reactions_count = post.get('reactions', {}).get('summary', {}).get('total_count', 0)

        return {
            'id': post.get('id'),
            'message': post.get('message'),
            'created_time': post.get('created_time'),
            'updated_time': post.get('updated_time'),
            'permalink_url': post.get('permalink_url'),
            'type': post.get('type'),
            'status_type': post.get('status_type'),
            'likes_count': likes_count,
            'comments_count': comments_count,
            'shares_count': shares_count,
            'reactions_count': reactions_count,
            'page_id': page_id
        }
