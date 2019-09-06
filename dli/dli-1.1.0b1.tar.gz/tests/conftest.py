import pytest


def pytest_collection_modifyitems(config, items):
    skip_integration = config.getoption("--skip-integration")
    mark_skip_integration = pytest.mark.skip(reason="skipping integration test")
    for item in items:
        if skip_integration and "integration" in item.keywords:
            item.add_marker(mark_skip_integration)

def pytest_addoption(parser):
    parser.addoption(
        "--skip-integration", action="store_true", default=False,
        help="Skip integration tests."
    )
