"""Feed Manager for GeoNet NZ Volcanic Alert Level feed."""
from aio_geojson_client.feed_manager import FeedManagerBase
from aiohttp import ClientSession

from .feed import GeonetnzVolcanoFeed


class GeonetnzVolcanoFeedManager(FeedManagerBase):
    """Feed Manager for GeoNet NZ Volcanic Alert Level feed."""

    def __init__(self, websession: ClientSession, generate_callback,
                 update_callback, remove_callback,
                 home_coordinates, filter_radius=None, status_callback=None):
        """Initialize the GeoNet NZ Volcanic Alert Level Feed Manager."""
        feed = GeonetnzVolcanoFeed(
            websession,
            home_coordinates,
            filter_radius=filter_radius)
        super().__init__(feed, generate_callback, update_callback,
                         remove_callback, status_callback)
