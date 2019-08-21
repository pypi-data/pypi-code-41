"""GeoNet NZ Volcanic Alert Level feed entry."""
import logging
from typing import Optional

from aio_geojson_client.feed_entry import FeedEntry

from .consts import ATTR_ACTIVITY, ATTR_HAZARDS, ATTR_LEVEL, ATTR_VOLCANO_ID, \
    ATTR_VOLCANO_TITLE, ATTRIBUTION

_LOGGER = logging.getLogger(__name__)


class GeonetnzVolcanoFeedEntry(FeedEntry):
    """GeoNet NZ Volcanic Alert Level feed entry."""

    def __init__(self, home_coordinates, feature):
        """Initialise this service."""
        super().__init__(home_coordinates, feature)

    @property
    def attribution(self) -> str:
        """Return the attribution of this entry."""
        return ATTRIBUTION

    @property
    def external_id(self) -> Optional[str]:
        """Return the external id of this entry."""
        return self._search_in_properties(ATTR_VOLCANO_ID)

    @property
    def title(self) -> Optional[str]:
        """Return the title of this entry."""
        return self._search_in_properties(ATTR_VOLCANO_TITLE)

    @property
    def alert_level(self) -> Optional[int]:
        """Return the volcanic alert level of this entry."""
        return self._search_in_properties(ATTR_LEVEL)

    @property
    def hazards(self) -> Optional[str]:
        """Return the hazards of this entry."""
        return self._search_in_properties(ATTR_HAZARDS)

    @property
    def activity(self) -> Optional[str]:
        """Return the quality of this entry."""
        return self._search_in_properties(ATTR_ACTIVITY)
