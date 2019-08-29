from ftw.events.utils import IS_PLONE_5
from ftw.upgrade import UpgradeStep


class AddEventsArchivePortlet(UpgradeStep):
    """Add events archive portlet.
    """

    def __call__(self):
        if IS_PLONE_5:
            self.install_upgrade_profile(['plone.app.registry', 'portlets'])
        else:
            self.install_upgrade_profile(['jsregistry', 'portlets'])
