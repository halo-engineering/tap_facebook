"""
Main tap module for Facebook engagement metrics.

This is the entry point for the Singer tap.
"""

import json
import sys
import singer
from typing import Dict, List
import argparse

from tap_facebook.auth import FacebookOAuthAuthenticator
from tap_facebook.client import FacebookClient
from tap_facebook.streams import PostsStream, PostInsightsStream, PageInsightsStream

LOGGER = singer.get_logger()

# All available streams
AVAILABLE_STREAMS = {
    'posts': PostsStream,
    'post_insights': PostInsightsStream,
    'page_insights': PageInsightsStream,
}


def load_json_file(path: str) -> Dict:
    """Load JSON from file path."""
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        LOGGER.error(f"Error loading JSON file {path}: {str(e)}")
        raise


def discover(client: FacebookClient, config: Dict) -> Dict:
    """
    Run discovery mode to generate catalog of available streams.

    Args:
        client: Facebook API client
        config: Tap configuration

    Returns:
        Catalog dictionary
    """
    LOGGER.info("Running discovery mode...")

    streams = []

    for stream_name, stream_class in AVAILABLE_STREAMS.items():
        stream = stream_class(client, config)
        streams.append(stream.get_metadata())

    catalog = {
        "streams": streams
    }

    return catalog


def sync(client: FacebookClient, config: Dict, catalog: Dict, state: Dict) -> None:
    """
    Run sync mode to extract data from selected streams.

    Args:
        client: Facebook API client
        config: Tap configuration
        catalog: Stream catalog with selections
        state: Current state for incremental syncing
    """
    LOGGER.info("Running sync mode...")

    # Get selected streams from catalog
    selected_streams = [
        stream for stream in catalog.get('streams', [])
        if stream.get('metadata', {}).get('selected', True)
    ]

    if not selected_streams:
        LOGGER.warning("No streams selected for sync")
        return

    LOGGER.info(f"Syncing {len(selected_streams)} streams")

    for stream_entry in selected_streams:
        stream_name = stream_entry.get('tap_stream_id')

        if stream_name not in AVAILABLE_STREAMS:
            LOGGER.warning(f"Unknown stream: {stream_name}")
            continue

        LOGGER.info(f"Syncing stream: {stream_name}")

        # Instantiate stream
        stream_class = AVAILABLE_STREAMS[stream_name]
        stream = stream_class(client, config)

        # Write schema
        stream.write_schema()

        # Sync records
        try:
            for record in stream.get_records(state):
                stream.write_record(record)

        except Exception as e:
            LOGGER.error(f"Error syncing stream {stream_name}: {str(e)}")
            raise

    LOGGER.info("Sync complete")


def main():
    """Main entry point for the tap."""
    parser = argparse.ArgumentParser(description='Singer tap for Facebook engagement metrics')

    parser.add_argument(
        '--config',
        required=True,
        help='Path to config.json file'
    )

    parser.add_argument(
        '--catalog',
        help='Path to catalog.json file (required for sync mode)'
    )

    parser.add_argument(
        '--state',
        help='Path to state.json file (for incremental syncing)'
    )

    parser.add_argument(
        '--discover',
        action='store_true',
        help='Run in discovery mode'
    )

    args = parser.parse_args()

    # Load config
    config = load_json_file(args.config)

    # Validate required config fields
    required_fields = ['client_id', 'client_secret', 'page_id']
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required config field: {field}")

    # Initialize authenticator and client
    authenticator = FacebookOAuthAuthenticator(config)
    client = FacebookClient(authenticator)

    # Run in discovery or sync mode
    if args.discover:
        catalog = discover(client, config)
        print(json.dumps(catalog, indent=2))

    else:
        if not args.catalog:
            raise ValueError("--catalog is required for sync mode")

        catalog = load_json_file(args.catalog)
        state = load_json_file(args.state) if args.state else {}

        sync(client, config, catalog, state)


if __name__ == '__main__':
    main()
