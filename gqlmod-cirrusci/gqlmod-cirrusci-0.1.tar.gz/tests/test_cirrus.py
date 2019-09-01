import gqlmod


def test_get_schema():
    assert gqlmod.providers.query_for_schema('cirrus-ci')
