"""Base stream class for Facebook tap."""

import singer
from typing import Dict, Iterator, Optional, List
from abc import ABC, abstractmethod
from tap_facebook.client import FacebookClient

LOGGER = singer.get_logger()


class FacebookStream(ABC):
    """Base class for Facebook data streams."""

    # Stream metadata (override in subclasses)
    name: str = None
    replication_method: str = "INCREMENTAL"
    replication_key: str = "updated_time"
    key_properties: List[str] = ["id"]
    schema: Dict = {}

    def __init__(self, client: FacebookClient, config: Dict):
        """
        Initialize the stream.

        Args:
            client: Facebook API client
            config: Tap configuration
        """
        self.client = client
        self.config = config

    @abstractmethod
    def get_records(self, state: Optional[Dict] = None) -> Iterator[Dict]:
        """
        Retrieve records from the stream.

        Args:
            state: Current state for incremental syncing

        Yields:
            Record dictionaries
        """
        pass

    def get_schema(self) -> Dict:
        """
        Get the JSON schema for this stream.

        Returns:
            JSON schema dictionary
        """
        return {
            "type": "object",
            "properties": self.schema
        }

    def get_metadata(self) -> Dict:
        """
        Get stream metadata for catalog.

        Returns:
            Metadata dictionary
        """
        return {
            "tap_stream_id": self.name,
            "stream": self.name,
            "key_properties": self.key_properties,
            "replication_key": self.replication_key,
            "replication_method": self.replication_method,
            "schema": self.get_schema()
        }

    def write_schema(self):
        """Write schema message to stdout."""
        singer.write_schema(
            stream_name=self.name,
            schema=self.get_schema(),
            key_properties=self.key_properties
        )

    def write_record(self, record: Dict):
        """
        Write a record to stdout.

        Args:
            record: Record dictionary
        """
        singer.write_record(stream_name=self.name, record=record)

    def write_state(self, state: Dict):
        """
        Write state to stdout.

        Args:
            state: State dictionary
        """
        singer.write_state(state)
