import pytest

from girder.plugin import loadedPlugins


@pytest.mark.plugin('geo_heatmap')
def test_import(server):
    assert 'geo_heatmap' in loadedPlugins()
