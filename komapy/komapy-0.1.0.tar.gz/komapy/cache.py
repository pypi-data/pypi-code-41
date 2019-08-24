from collections import OrderedDict


class ResolverCache(object):
    """
    An object representing resolver cache.

    It takes a single argument, i.e config, which is a dictionary of data
    resolver settings. Here it is an example:

    config = {
        'name': 'edm',
        'benchmark': 'BAB0',
        'reflector': 'RB2',
        'start_at': '2019-04-01',
        'end_at': '2019-08-01',
        'ci': True,
    }

    Key 'csv', 'url', and 'name' is reserved as data resolver sources. Other
    keys left as optional parameters.
    """

    def __init__(self, config):
        self.config = config

    def __eq__(self, other):
        if isinstance(other, ResolverCache):
            return self.config == other.config
        return False

    def __hash__(self):
        return hash(frozenset(self.config.items()))

    @classmethod
    def get_resolver_cache_config(self, series):
        """
        Get resolver cache config from KomaPy series instance. It's simply
        takes data resolver key and optional query or csv parameters.
        """
        config = {}

        sources = OrderedDict([
            ('csv', 'csv_params'),
            ('url', 'query_params'),
            ('name', 'query_params'),
        ])

        for name in sources:
            source = getattr(series, name, None)
            if source:
                config[name] = source
                options = getattr(series, sources[name], {})
                if options:
                    config.update(options)
                break

        return config
