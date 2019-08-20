from people.apps.people.humanresources_list import HumanResourcesList
from .descriptions.degrees_app import DegreesAdminApp
from .descriptions.scientific_areas_app import ScientificAreasAdminApp
from .groups.groups_list import GroupsListApp
from .descriptions.grouptype_app import GroupTypesAdminApp
from .descriptions.positions_app import PositionsAdminApp


from .people.people_list import PeopleListWidget
from .groups.mygroups_list import MyGroupsApp

from .search import SearchWidget

try:
    from .profile import UserProfileFormWidget
except:
    pass

from .dashboard import HRDashboard