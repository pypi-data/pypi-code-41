from dli.client.components import SirenComponent
from dli.client.utils import ensure_count_is_valid


class Search(SirenComponent):
    """
    Catalogue search functions.
    """

    class urls:
        search_root = '/__api/search/'
        search_packages = '/__api/search/packages/'
        search_datasets = '/__api/search/datasets/'
        search_collections = '/__api/search/collections/'

    def _search_my_entities(self, entity, search_func, term, count):
        ensure_count_is_valid(count)

        # replicating UI behavior, for empty term we want an empty search
        if term is None or term == "":
            return []

        result = search_func(query=term, page_size=count)
        return result.get_entities(rel=entity)

    def search(self, term, count=100):
        """
        Search across all catalogue entities given a particular set of keywords.

        :param str term: The search term.
        :param int count: Optional. The amount of results to be returned.

        :returns: A list of Catalogue entities
        :rtype: list[collections.namedtuple]

        - **Sample**

        .. code-block:: python

                automotive_catalogue_entities = client.search(
                    term="Automotive",
                    count=100
                )

        """
        ensure_count_is_valid(count)
        return self.client.session.get(
            self.urls.search_root, params={'query': term, 'page_size': count}
        ).to_many_siren('')

    def search_packages(self, term, count=100):
        """
        Search across packages in the catalogue given a particular set of keywords.

        :param str term: The search term.
        :param int count: Optional. The amount of results to be returned. Defaults to 100.

        :returns: A list of packages
        :rtype: list[collections.namedtuple]

        - **Sample**

        .. code-block:: python

                automotive_packages = client.search_packages(
                    term="Automotive",
                    count=100
                )

        """
        ensure_count_is_valid(count)
        return self.client.session.get(
            self.urls.search_packages, params={'query': term, 'page_size': count}
        ).to_many_siren('package')


    def search_collections(self, term, count=100):
        """
        Search across collections in the catalogue given a particular set of keywords.

        :param str term: The search term.
        :param int count: Optional. The amount of results to be returned. Defaults to 100.

        :returns: A list of collections
        :rtype: list[collections.namedtuple]

        - **Sample**

        .. code-block:: python

                automotive_collections = client.search_collections(
                    term="Automotive",
                    count=100
                )

        """
        ensure_count_is_valid(count)
        return self.client.session.get(
            self.urls.search_collections, params={'query': term, 'page_size': count}
        ).to_many_siren('collection')

    def search_datasets(self, term, count=100):
        """
        Search across datasets in the catalogue given a particular set of keywords.

        :param str term: The search term.
        :param int count: Optional. The amount of results to be returned. Defaults to 100.

        :returns: A list of datasets
        :rtype: list[dataset.namedtuple]

        - **Sample**

        .. code-block:: python

                results = client.search_datasets(
                    term="CDS",
                    count=100
                )

        """
        ensure_count_is_valid(count)
        return self.client.session.get(
            self.urls.search_datasets, params={'query': term, 'page_size': count}
        ).to_many_siren('dataset')
