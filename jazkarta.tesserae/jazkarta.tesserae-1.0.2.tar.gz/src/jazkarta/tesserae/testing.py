# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import jazkarta.tesserae


class JazkartaTesseraeLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=jazkarta.tesserae)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'jazkarta.tesserae:default')


JAZKARTA_TESSERAE_FIXTURE = JazkartaTesseraeLayer()


JAZKARTA_TESSERAE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(JAZKARTA_TESSERAE_FIXTURE,),
    name='JazkartaTesseraeLayer:IntegrationTesting'
)


JAZKARTA_TESSERAE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(JAZKARTA_TESSERAE_FIXTURE,),
    name='JazkartaTesseraeLayer:FunctionalTesting'
)


JAZKARTA_TESSERAE_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        JAZKARTA_TESSERAE_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='JazkartaTesseraeLayer:AcceptanceTesting'
)
