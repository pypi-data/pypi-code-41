# -*- coding: utf-8 -*-
__version__ = '0.8.1'
__version_info__ = tuple([int(num) if num.isdigit() else num for num in __version__.replace('-', '.', 1).split('.')])

default_app_config = "simpl_users.apps.SimplUsersConfig"
