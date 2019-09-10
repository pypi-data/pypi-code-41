from dli.client.components import SirenComponent
from dli.client.utils import ensure_count_is_valid
from dli.client.components.urls import me_urls


class Me(SirenComponent):
    """Functions related to the current logged in user."""

    def _get_my_entities(self, entity, my_entities_func, count):
        ensure_count_is_valid(count)

        result = my_entities_func(page_size=count)
        return result.get_entities(rel=entity)

    def get_my_packages(self, count=100):
        """
        Returns a list of packages where session user account is: a Manager, Tech Data Ops or Access Manager.

        :param int count: The number of items to retrieve, defaults to 100.

        :returns: List of my packages.
        :rtype: list[collections.namedtuple]

        - **Sample**

        .. code-block:: python

                my_packages = client.get_my_packages()

        """
        ensure_count_is_valid(count)

        response = self.session.get(
            me_urls.my_packages, params={'page_size': count}
        )

        return response.to_many_siren('package')

    def get_my_consumed_packages(self, count=100):
        """
        Returns a list of all the packages user session account has access to.

        :param int count: The number of items to retrieve, defaults to 100.

        :returns: List of my consumed packages.
        :rtype: list[collections.namedtuple]

        - **Sample**

        .. code-block:: python

                my_consumed_packages = client.get_my_consumed_packages()

        """
        ensure_count_is_valid(count)

        response = self.session.get(
            me_urls.consumed_packages, params={'page_size': count}
        )

        return response.to_many_siren('access_request')


    def get_my_collections(self, count=100):
        """
        Returns a list of collections where session user account is the manager.

        :param int count: The number of items to retrieve, defaults to 100.

        :returns: List of my collections.
        :rtype: list[collections.namedtuple]

        - **Sample**

        .. code-block:: python

                my_collections = client.get_my_collections()

        """
        ensure_count_is_valid(count)

        response = self.session.get(
            me_urls.my_collections, params={'page_size': count}
        )

        return response.to_many_siren('collection')


    def get_my_accounts(self):
        """
        Returns a list of all the accounts associated with user session.

        :returns: list of all associated accounts.
        :rtype: list[collections.namedtuple]

        - **Sample**

        .. code-block:: python

                my_accounts = client.get_my_accounts()

        """
        response = self.session.get(me_urls.my_accounts)
        return response.to_many_siren('')
