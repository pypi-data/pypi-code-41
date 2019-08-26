# -*- coding: utf-8 -*-
from __future__ import absolute_import
from plone.app.upgrade.utils import loadMigrationProfile


def reload_gs_profile(context):
    loadMigrationProfile(
        context,
        'profile-collective.edtf_behavior:default',
    )
