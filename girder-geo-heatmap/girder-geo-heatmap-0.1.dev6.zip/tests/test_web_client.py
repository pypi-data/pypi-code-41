import os
import pytest
from pytest_girder.web_client import runWebClientTest


@pytest.mark.skip(reason='geojs packaging needs to be updated to work in the test environment')
@pytest.mark.plugin('geo_heatmap')
@pytest.mark.parametrize('spec', (
    'geoHeatmapSpec.js',
))
def testWebClient(boundServer, fsAssetstore, db, spec):  # noqa
    spec = os.path.join(os.path.dirname(__file__), 'web_client_specs', spec)
    runWebClientTest(boundServer, spec, 15000)
