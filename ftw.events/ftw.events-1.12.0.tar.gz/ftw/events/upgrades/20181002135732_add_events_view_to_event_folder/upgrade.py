from ftw.upgrade import UpgradeStep


class AddEventsViewToEventFolder(UpgradeStep):
    """Add events view to event folder.
    """

    def __call__(self):
        self.install_upgrade_profile()
