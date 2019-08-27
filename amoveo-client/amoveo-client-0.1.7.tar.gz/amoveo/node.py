import requests


class AmoveoNode:
    def __init__(self, host):
        self.host = host

    def last_block(self):
        """
        Get current blockchain height.
        curl Example:
        curl http://amoveo.node/ -d '["height"]'
        > ["ok",79580]
        :return: (int) height
        """
        payload = ["height"]
        r = requests.get(self.host, json=payload)
        r.raise_for_status()
        data = r.json()
        return data[1]

    def block(self, block_num):
        """
        curl Example:
        curl http://amoveo.node/ -d '["block", 3, 79584]'
        > ["ok",[-6,[-6,["signed",["spend","BC80oG/EAXojuLCjIjQmIQgTv9wHscgCccEy4q7R2Vwak2iPbrTb1htgVOU+NjChxxmOeNiUJMxURPqUEWZ2lzc=",26836,61657,"BNS4+X1t80W0F8iqOcM9Wp/ltLgMpmLbS56MpQ6DR4kKx8AY03ATzcDB29G8xSyZdQlCwZYId5SKGoZ5/fEzoKY=",32080843,0],"MEYCIQCzkY2TbLXH71O3S6INXHzuoiNaolTSbfkt+Udv226ilQIhALOwRPoOxjLQA1VfUnIWB8gLksd+nzLjutLjhUb5CxO4",[-6]]],[-6,"W0wX4/kGvPBv7QoR1Uz6Mwp09RrravaDUXLhL7alUnU="]]]
        :param block_num:
        :return: (list) [-6,[-6,["signed",["spend","BC80oG/EAXojuLCjIjQmIQgTv9wHscgCccEy4q7R2Vwak2iPbrTb1htgVOU+NjChxxmOeNiUJMxURPqUEWZ2lzc=",26836,61657,"BNS4+X1t80W0F8iqOcM9Wp/ltLgMpmLbS56MpQ6DR4kKx8AY03ATzcDB29G8xSyZdQlCwZYId5SKGoZ5/fEzoKY=",32080843,0],"MEYCIQCzkY2TbLXH71O3S6INXHzuoiNaolTSbfkt+Udv226ilQIhALOwRPoOxjLQA1VfUnIWB8gLksd+nzLjutLjhUb5CxO4",[-6]]],[-6,"W0wX4/kGvPBv7QoR1Uz6Mwp09RrravaDUXLhL7alUnU="]]
        """
        # payload = ["block", block_num] # for external api
        payload = ["block", 3, block_num]
        r = requests.get(self.host, json=payload)
        r.raise_for_status()
        data = r.json()
        return data[1]

    def account(self, address: str):
        """
        curl Example:
        curl http://amoveo.node/ \
        -d '["account", "BIkj6yP84pYqRP8LDjKnO6Ae4cQSP5NiX6x5jRpWUcYWyR87uM6pf90ZhAH/J0g3Fm35O+Kf6a0mAqzsuvTPmyU="]'
        > ["ok",0]  # account not funded yet.
        :param address: veo address
        :return: 0 - if account not funded
                list ["acc",74679577,25, address,0,"unknown hash"] - if account funded
        """
        payload = ["account", address]
        r = requests.get(self.host, json=payload)
        r.raise_for_status()
        data = r.json()
        return data[1]

    def pending_tx(self):
        """
        Pending transactions. Response contains current pending transactions.
        Unfortunately, they have no hashes included in response but one can map them using theirs signatures.
        curl Example: curl http://amoveo.external/ -d '["txs"]'
        curl Example: curl http://amoveo.node/ -d '["mempool"]'
        :return: list of txs.
        """
        # payload = ["txs"]  # for external api
        payload = ["mempool"]
        r = requests.get(self.host, json=payload)
        r.raise_for_status()
        data = r.json()
        return data[1]

    def prepare_tx(self, typ, amount, fee, _from, _to):
        """
        Prepare transaction for sending.
        curl Example: curl http://amoveo.node/ -d '[typ, amount, fee, _from, _to]'
        :param typ:
        :param amount:
        :param fee:
        :param _from:
        :param _to:
        :return: (str) tx
        """
        payload = [typ, amount, fee, _from, _to]
        r = requests.get(self.host, json=payload)
        r.raise_for_status()
        data = r.json()
        return data[1]

    def send_tx(self, tx, sign):
        """
        curl Example: curl http://amoveo.node/ -X POST -d '["txs", [-6, ["signed", tx, sign, [-6]]]]'
        :param tx:
        :param sign:
        :return: (str) tx_id
        """
        payload = ["txs", [-6, ["signed", tx, sign, [-6]]]]
        r = requests.post(self.host, json=payload)
        r.raise_for_status()
        data = r.json()
        return data[1]
