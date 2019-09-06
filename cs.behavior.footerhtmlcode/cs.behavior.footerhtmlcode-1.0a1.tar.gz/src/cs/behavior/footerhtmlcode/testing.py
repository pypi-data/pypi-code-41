# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import cs.behavior.footerhtmlcode


class CsBehaviorFooterhtmlcodeLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.app.multilingual

        self.loadZCML(package=plone.app.multilingual)
        self.loadZCML(package=cs.behavior.footerhtmlcode)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "cs.behavior.footerhtmlcode:default")


CS_BEHAVIOR_FOOTERHTMLCODE_FIXTURE = CsBehaviorFooterhtmlcodeLayer()


CS_BEHAVIOR_FOOTERHTMLCODE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(CS_BEHAVIOR_FOOTERHTMLCODE_FIXTURE,),
    name="CsBehaviorFooterhtmlcodeLayer:IntegrationTesting",
)


CS_BEHAVIOR_FOOTERHTMLCODE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(CS_BEHAVIOR_FOOTERHTMLCODE_FIXTURE,),
    name="CsBehaviorFooterhtmlcodeLayer:FunctionalTesting",
)


CS_BEHAVIOR_FOOTERHTMLCODE_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        CS_BEHAVIOR_FOOTERHTMLCODE_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="CsBehaviorFooterhtmlcodeLayer:AcceptanceTesting",
)
