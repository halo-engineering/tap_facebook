"""Stream classes for Facebook tap."""

from tap_facebook.streams.posts import PostsStream
from tap_facebook.streams.post_insights import PostInsightsStream
from tap_facebook.streams.page_insights import PageInsightsStream

__all__ = ['PostsStream', 'PostInsightsStream', 'PageInsightsStream']
