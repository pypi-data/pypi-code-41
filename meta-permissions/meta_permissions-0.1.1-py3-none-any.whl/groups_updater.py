from edc_permissions.groups_updater import GroupsUpdater as Base
from edc_permissions.constants import LAB, AUDITOR

from .group_names import RANDO, AE_REVIEW


class GroupsUpdater(Base):

    extra_group_names = [RANDO, AE_REVIEW]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ensure_users_not_in_group(RANDO, users_by_groups=[AUDITOR, LAB])
