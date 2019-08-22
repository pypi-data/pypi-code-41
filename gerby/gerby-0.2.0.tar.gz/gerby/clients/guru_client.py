import os

import requests as r
from cached_property import cached_property

import gerby.constants as c
from gerby.secrets import GURU_PASS, GURU_USER

POLICY_BOARD = "29611c28-41cc-4b25-86fe-30cc7e9d0630"


class HoloCard:

    gf_mirror_collection_id = "fc4e13bf-fa63-4a74-b957-738c9cc85387"

    def __init__(self, title, content, board_id=POLICY_BOARD):
        self.card_data = {
            "preferredPhrase": title,
            "content": content,
            "verificationInterval": 90,
            "shareStatus": "TEAM",
            "boards": [{"id": board_id}],
            "collection": {"id": self.gf_mirror_collection_id},
            "verifiers": [],
        }

    def __repr__(self):
        return f"<HoloCard '{self.card_data['preferredPhrase']}' >"

    @cached_property
    def data(self):
        return self.card_data


class GuruClient:
    __base_url = "https://api.getguru.com/api/v1/"

    def __init__(self):
        self.__user = GURU_USER
        self.__pass = GURU_PASS

    def __build_url(self, path):
        return self.__base_url + path

    def get(self, path):
        full_url = self.__build_url(path)
        return r.get(full_url, auth=(self.__user, self.__pass))

    def post(self, path, data):
        full_url = self.__build_url(path)
        return r.post(full_url, json=data, auth=(self.__user, self.__pass))

    def delete(self, path):
        full_url = self.__build_url(path)
        return r.delete(full_url, auth=(self.__user, self.__pass))

    def query(self, query_string):
        query = urlencode({"q": query_string})
        path = f"search/query?{query}"
        return self.get(path)

    def collections(self):
        path = f"collections"
        return self.get(path)

    def boards(self):
        path = f"boards"
        return self.get(path)

    def board(self, board_id):
        path = f"boards/{board_id}"
        return self.get(path)

    def create_card(self, card_data):
        path = f"cards/extended"
        return self.post(path, card_data)

    def create_group(self, group_name):
        path = f"groups"
        return self.post(path, {"name": group_name})

    def groups(self):
        path = f"groups"
        return self.get(path)

    def members(self):
        path = f"members"
        return self.get(path)

    def delete_card(self, card_id):
        path = f"cards/{card_id}"
        return self.delete(path)

    def clean_board(self, board_id, dry_run=True):
        """
        WARNING: THIS IS A DESTRUCTIVE ACTION, REQUIRES YOU TO OVERRIDE DRY_RUN
        PARAMETER TO ACTUALLY RUN DELETE METHOD.
        """
        board = self.board(board_id).json()
        cards = board["items"]
        print(
            f"cleaning board: {board['title']}, {len(cards)} items to delete [DRY_RUN: ${dry_run}]"
        )
        for (index, title) in [
            (card["id"], card.get("preferredPhrase", "empty-attribute"))
            for card in cards
        ]:
            print(f"deleting: {index}-{title}")
            if not dry_run:
                self.delete_card(index)
