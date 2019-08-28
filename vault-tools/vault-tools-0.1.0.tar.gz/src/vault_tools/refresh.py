#!/usr/bin/env python3.6m
"""
Renews vault token
"""
import time

import hvac


class VaultTokenRefresher(object):
    def __init__(
        self, vault_addr: str, token: str, sleep_time: int = 3600, forever: bool = False
    ):
        self.client = hvac.Client(url=vault_addr, token=token)
        self.sleep_time = sleep_time
        self.forever = forever

        self.renewal = None

    def info(self):
        lookup = self.client.lookup_token()

        accessor = lookup["data"]["accessor"]
        expire_time = lookup["data"]["expire_time"]

        return 'token accessor={}, expire_time={}, sleep_time={}'.format(accessor, expire_time, self.sleep_time)

    def renew(self):
        return self.client.renew_token()

    def run(self):
        while True:
            self.renew()

            print(self.info())

            if not self.forever:
                break

            time.sleep(self.sleep_time)
