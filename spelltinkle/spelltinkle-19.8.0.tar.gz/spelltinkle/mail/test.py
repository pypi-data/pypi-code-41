from typing import Tuple, List

emails = {
    1: """
From: jj@smoerhul.dk

Bla bla.
""",
    2: """"""}


class TestIMAP4:
    def login(self, user: str, pw: str):
        pass

    def uid(self, cmd: str, *args: str) -> Tuple[str, List[Tuple[str, str]]]:
        if cmd == 'FETCH':
            uids = [int(x) for x in args[0].split(',')]
            return ('OK', [('hmm', emails[uid]) for uid in uids])
        assert 0
