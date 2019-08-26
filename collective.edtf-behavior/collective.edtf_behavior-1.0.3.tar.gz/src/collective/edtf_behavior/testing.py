# -*- coding: utf-8 -*-
from __future__ import absolute_import
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import collective.edtf_behavior


class CollectiveEdtfBehaviorLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import Products.DateRangeInRangeIndex
        self.loadZCML(package=Products.DateRangeInRangeIndex)
        z2.installProduct(app, 'Products.DateRangeInRangeIndex')

        self.loadZCML(package=collective.edtf_behavior)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.edtf_behavior:default')


COLLECTIVE_EDTF_BEHAVIOR_FIXTURE = CollectiveEdtfBehaviorLayer()


COLLECTIVE_EDTF_BEHAVIOR_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_EDTF_BEHAVIOR_FIXTURE,),
    name='CollectiveEdtfBehaviorLayer:IntegrationTesting',
)


COLLECTIVE_EDTF_BEHAVIOR_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_EDTF_BEHAVIOR_FIXTURE,),
    name='CollectiveEdtfBehaviorLayer:FunctionalTesting',
)


COLLECTIVE_EDTF_BEHAVIOR_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_EDTF_BEHAVIOR_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='CollectiveEdtfBehaviorLayer:AcceptanceTesting',
)
