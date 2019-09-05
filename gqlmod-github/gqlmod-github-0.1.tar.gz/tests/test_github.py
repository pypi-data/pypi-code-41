import gqlmod


def test_get_schema():
    assert gqlmod.providers.query_for_schema('github')


def test_import():
    gqlmod.enable_gql_import()
    import tests.queries  # noqa
    # TODO: Actually check previews got detected
