from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from .stateless import (
    StatelessCrosser,
)

if TYPE_CHECKING:
    from typing import (
        Optional,
    )
    from jinete.models import (
        PlannedTrip,
    )

logger = logging.getLogger(__name__)


class BestStateCrosser(StatelessCrosser):

    def update_ranking(self):
        ranking = list()
        for route, trip in self:
            planned_trip = route.feasible_trip(trip)
            if planned_trip is None:
                continue
            ranking.append(planned_trip)
        ranking.sort(key=lambda pt: pt.scoring)

    def get_planned_trip(self) -> Optional[PlannedTrip]:
        best_planned_trip = None
        for planned_trip in self.iterator:
            if best_planned_trip is None or planned_trip.scoring < best_planned_trip.scoring:
                best_planned_trip = planned_trip
        return best_planned_trip
