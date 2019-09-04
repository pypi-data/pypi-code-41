from ftw.upgrade import UpgradeStep


class RegisterIFrameCheckJS(UpgradeStep):
    """Register i frame check js.
    """

    def __call__(self):
        self.install_upgrade_profile()
