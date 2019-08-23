import requests


class DomainService:

    @staticmethod
    def get_domain(account_id, service_name, env='prod'):
        """
        Documentation:
        https://developers.liveperson.com/agent-domain-domain-api.html

        :param account_id: str <Required>
        :param service_name: str <Required>
        :return: str (Returns API base domain based on account id and service name)
        """

        env_list = ['prod', 'qa'] # TODO: Find a central place to import this list from
        if env not in env_list:
            raise ValueError(f"{env} is not a valid environment. Choose from {env_list}")

        # Generate request
        if env == 'qa':
            r = requests.get(
                url=f'http://hc1n.dev.lprnd.net/api/account/{account_id}/service/{service_name}/baseURI.json?version=1.0'
            )
        else:
            r = requests.get(
                url=f'http://api.liveperson.net/api/account/{account_id}/service/{service_name}/baseURI.json?version=1.0'
            )

        # Check request status
        if r.ok:
            try:
                return r.json()['baseURI']
            except KeyError:
                print(f'[Domain Error]: {r.json()}')
        else:
            try:
                print(f'[Domain Error]: {r.json()}')
            except ValueError:
                pass

            r.raise_for_status()
