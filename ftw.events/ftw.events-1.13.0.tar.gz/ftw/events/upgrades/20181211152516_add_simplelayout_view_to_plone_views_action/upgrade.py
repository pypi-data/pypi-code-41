from ftw.upgrade import UpgradeStep


class AddSimplelayoutViewToPloneViewsAction(UpgradeStep):
    """Add simplelayout view to plone views action.
    """

    def __call__(self):
        self.install_upgrade_profile()
