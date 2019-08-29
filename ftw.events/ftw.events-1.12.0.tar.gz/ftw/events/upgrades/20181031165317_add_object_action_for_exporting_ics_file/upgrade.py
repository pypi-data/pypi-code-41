from ftw.upgrade import UpgradeStep


class AddObjectActionForExportingICSFile(UpgradeStep):
    """Add object action for exporting ICS file.
    """

    def __call__(self):
        self.install_upgrade_profile()
