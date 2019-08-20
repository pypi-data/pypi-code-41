# from .dashboard import DashboardWidget
from people.apps.profile import UserProfileFormWidget
from people.apps.search import SearchWidget
from .external_links import WikiLink
from .external_links import RequisitionsLink
from .external_links import QlikViewLink
from .external_links import NexBittLink
from .external_links import iLabLink
from .external_links import FundingOpportunitiesLink

__all__ = (
    # 'DashboardWidget',
    UserProfileFormWidget,
    SearchWidget,
    WikiLink,
    RequisitionsLink,
    QlikViewLink,
    NexBittLink,
    iLabLink,
    FundingOpportunitiesLink,
)
