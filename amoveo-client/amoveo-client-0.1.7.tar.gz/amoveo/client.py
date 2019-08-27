from .node import AmoveoNode
from .explorer import AmoveoExplorer
from .sign import sign, generate_wallet


class AmoveoClient:
    def __init__(self, conf):
        """
        Implement all methods from node, explorer, sign
        :param conf: dict {'EXPLORER': ..., 'NODE': ...}
        """
        explorer = AmoveoExplorer(conf.get("EXPLORER"))
        self.get_tx = explorer.get_tx
        self.account_txs = explorer.account_txs

        node = AmoveoNode(conf.get("NODE"))
        self.last_block = node.last_block
        self.block = node.block
        self.account = node.account
        self.pending_tx = node.pending_tx
        self.prepare_tx = node.prepare_tx
        self.send_tx = node.send_tx

    sign = staticmethod(sign)
    generate_wallet = staticmethod(generate_wallet)

    def balance(self, address: str, in_satoshi=False):
        """
        Get balance in veo or satoshi.
        :param address:
        :return:
        """
        res = self.account(address)
        if res == 0:
            return 0
        else:
            try:
                amount = res[1]
                if in_satoshi:
                    return amount
                else:
                    return amount / 1e8
            except:
                raise Exception

    def tx_confirmations(self, tx_hash):
        tx = self.get_tx(tx_hash)
        confirmations = self.last_block() - tx["blocknumber"]
        return confirmations

    def get_txs(self, block_data):
        """
        Get txs from block_data.
        :param block_data:
            [
              "ok",
              [
                -6,
                [
                  -6,
                  [
                    "signed",
                    [
                      "spend",
                      "BBrLVfwGFhMTmnZ6RZrBTwPXYHnsvi9Y8hL0EkWaoWM9qWxTiS8AWPdVWd7Cz6p4hv9moSC6m1ekbxi2DVYhwvo=",
                      1221,
                      61657,
                      "BKHzjIT1+N58gkU12i7kgtn/BlFOshonqoBId13Ap1r6Rhie/7CLb/ldDHa0iKk+3++umO86mbIcXee+GnveuCo=",
                      63398162,
                      0
                    ],
                    "MEQCIDcvqA4lDOfVt48P90s5A2QT9zdVD3Bl15UuN/N/dvptAiAUlxIT7ES6dUtVoeyM6D1D+46xESKFLxfSKmNvDRZXnQ==",
                    [
                      -6
                    ]
                  ]
                ],
                [
                  -6,
                  "cQuiBwY20dqcQPmrkHYMyrQwo/x3ho7cFuB1lVjMGQQ="
                ]
              ]
            ]

        :return:
            txs: list
             [ [
                "signed",
                [
                  "spend",
                  "BBrLVfwGFhMTmnZ6RZrBTwPXYHnsvi9Y8hL0EkWaoWM9qWxTiS8AWPdVWd7Cz6p4hv9moSC6m1ekbxi2DVYhwvo=",
                  1221,
                  61657,
                  "BKHzjIT1+N58gkU12i7kgtn/BlFOshonqoBId13Ap1r6Rhie/7CLb/ldDHa0iKk+3++umO86mbIcXee+GnveuCo=",
                  63398162,
                  0
                ],
                "MEQCIDcvqA4lDOfVt48P90s5A2QT9zdVD3Bl15UuN/N/dvptAiAUlxIT7ES6dUtVoeyM6D1D+46xESKFLxfSKmNvDRZXnQ==",
                [
                  -6
                ]
              ], ...
             ]
             hashes: list (str)
        """
        try:
            txs, hashes = block_data[1][1:], block_data[2][1:]
        except IndexError:
            txs, hashes = [], []

        return self.parse_txs(txs, hashes)

    def parse_txs(self, raw_txs, hashes=None):
        """
        Convert to list of tx dict values.
        :param raw_txs
            [
                [
                    "signed",
                    [
                        "spend",
                        "BGJJ08FDDFCQ8w3G3AbrL/qjEQJXWZsLqIqrmyoH3Vhy709+UlkJLgA2KarZTfXQg5E46jd918Nl9AkexDUKNzI=",
                        5965,
                        61657,
                        "BEodyMSNL3mDGZwhb1a34YLLapqMWJmBXvcIA9BwN+UA3eHFSPeHj1jDxElAlGBGQehVlxuQH696yVbNfQubRfs=",
                        44343288,
                        0
                    ],
                    "MEYCIQDwxypFRNzvPU8WTPM9nxQ5x0dgM1xJTCXrKl6+4S3zcQIhALKP7ohD12HUzpN6kY/v5SXK0dPkLKSK4FN+cl8wWHyw",
                    [
                        -6
                    ]
                ],
            ...]
        :param hashes: list(str)
        =>
        :return: list (dict)
            [
                {
                    'hash':
                    'sign': tx_sign,
                    'from':
                    'to':
                    'amount':
                }
            ]
        """
        txs = []
        for ind, tx_raw in enumerate(raw_txs):
            tx_sign = tx_raw[2]
            tx = tx_raw[1]

            if tx[0] in ["spend", "create_acc_tx"]:
                txs.append({
                    'hash': hashes[ind] if hashes else None,
                    'sign': tx_sign,
                    'from': tx[1],
                    'to': tx[4],
                    'amount': tx[5]
                })
        return txs

