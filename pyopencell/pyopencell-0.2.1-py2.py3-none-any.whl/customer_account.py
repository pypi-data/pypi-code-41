from errors import ArgumentMissingError, HTTPError


class Customer():

    def find_customer(self,
                      customer_id=None):
        """ Find a Customer

        Args:
            customer_id (int): Customer ID to find

        Return:
            **response**: Return the response object
        """
        if not customer_id:
            raise ArgumentMissingError("customer_id")

        self.url = "{0}{1}/account/customerAccount/list?customerCode={2}".format(
            self.baseurl,
            self.api_route,
            str(customer_id))
        self.http_method = 'GET'

        response = self._send_request()

        return response

    def create_subscription(
            self,
            subscription=None):
        """ Create a Subscription

        Args:
            subscription (dict): Dict with the Customer Account Hierarchy fields

        Return:
            **response**: Return the response object
        """
        if not subscription:
            raise ArgumentMissingError("subscription")

        self.url = "{0}{1}/billing/subscription".format(
            self.baseurl,
            self.api_route)
        self.http_method = 'POST'

        response = self._send_request(subscription)

        return response

    def create_or_update_account_hierarchy(
            self,
            customer_hierarchy=None):
        """ Create or Update Customer Account Hierarchy

        Args:
            customer_hierarchy (dict): Dict with the Customer Account Hierarchy fields

        Return:
            **response**: Return the response object
        """
        if not customer_hierarchy:
            raise ArgumentMissingError("account_hierarchy")

        self.url = "{0}{1}/account/accountHierarchy/createOrUpdateCRMAccountHierarchy".format(
            self.baseurl,
            self.api_route)
        self.http_method = 'POST'

        response = self._send_request(customer_hierarchy)

        return response

