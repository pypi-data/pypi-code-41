import os
import datetime
import json


class Note(object):
    notes = list()
    save_location = "notes"

    def __init__(self, cite, body=None, link=None):
        self.created_time = datetime.datetime.now()
        self.updated_time = datetime.datetime.now()
        self.cite = cite
        self.body = body
        self.link = link
        Note.notes.append(self)
        self.save()

    def __repr__(self):
        ctx = {
            "cite": self.cite,
            "body": self.body,
            "link": self.link,
            "created_time": self.created_time.strftime(
                "%d %b %Y %H:%M:%S"
            ),
            "updated_time": self.updated_time.strftime(
                "%d %b %Y %H:%M:%S"
            ),
        }
        return json.dumps(ctx, indent=3)

    def __str__(self):
        return self.__repr__()

    def save(self):
        if not os.path.exists(Note.save_location):
            os.mkdir(Note.save_location)
        file_name = self.created_time.strftime(
            "%Y_%m_%d_%H_%M_%S.txt"
        )
        file_path = os.path.join(
            os.path.curdir, Note.save_location, file_name
        )
        if os.path.exists(file_path):
            self.updated_time = datetime.datetime.now()

        with open(file_path, "w") as f:
            f.write(str(self))


if __name__ == "__main__":
    import subprocess

    subprocess.call(
        [
            "ipython3",
            "-i",
            "-c",
            "from ipynote.notes import Note",
        ]
    )
