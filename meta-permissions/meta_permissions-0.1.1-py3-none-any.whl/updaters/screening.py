from django.contrib.auth.models import Group
from edc_permissions.utils import (
    add_permissions_to_group_by_app_label,
    make_view_only_model,
    remove_historical_group_permissions,
)

from ..group_names import SCREENING


def update_screening_group_permissions():

    group_name = SCREENING
    group = Group.objects.get(name=group_name)

    add_permissions_to_group_by_app_label(group, "meta_screening")
    make_view_only_model(group, "meta_screening.subjectscreening")
    remove_historical_group_permissions(group)
    return group_name
