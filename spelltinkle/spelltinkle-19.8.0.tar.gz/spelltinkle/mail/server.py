import imaplib
import os
import pickle
import socket
import sqlite3
import stat
import sys
from pathlib import Path
from typing import List

# from imapclient import IMAPClient

from ..config import conf


class Server:
    def __init__(self, name: str):
        self.config = conf.mail[name]
        self.dir = conf.home / 'mail' / name
        self._server = None
        self._db = None

    def fork(self):
        pid = os.fork()
        if pid == 0:
            pid = os.fork()
            if pid == 0:
                # redirect standard file descriptors
                """
                sys.stderr.flush()
                si = open(os.devnull, 'r')
                so = open(os.devnull, 'w')
                se = open(os.devnull, 'w')
                os.dup2(si.fileno(), sys.stdin.fileno())
                os.dup2(so.fileno(), sys.stdout.fileno())
                os.dup2(se.fileno(), sys.stderr.fileno())
                """
                self.run()
            else:
                os._exit(0)

    @property
    def db(self):
        if self._db:
            return self._db
        dbfile = self.dir / 'db.sqlite3'
        exists = dbfile.is_file()
        self._db = sqlite3.connect(
            # f'file:{dbfile}?nolock=1',
            str(dbfile),
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        if not exists:
            with self._db as db:
                db.execute(
                    'CREATE TABLE mails ('
                    'uid INTEGER PRIMARY KEY,'
                    'folder TEXT,'
                    'time timestamp,'
                    'subject TEXT,'
                    'from TEXT,'
                    'to TEXT);')
            with self._db as db:
                db.execute('CREATE INDEX mails_index ON mails(folder);')
            with self._db as db:
                db.execute(
                    'CREATE TABLE folders ('
                    'name TEXT PRIMARY KEY,'
                    'folder TEXT);')
        return self._db

    def read_password(self):
        pw = self.dir / 'pw'
        assert pw.stat().st_mode & (stat.S_IRGRP | stat.S_IROTH) == 0
        return pw.read_text().strip()

    @property
    def server(self):
        if self._server is None:
            host = self.config['host']
            if host == 'test':
                from .test import TestIMAP4
                self.server = TestIMAP4()
            else:
                self._server = imaplib.IMAP4_SSL(host)
            self._server.login(self.config['user'], self.read_password())
        return self._server

    # find_special_folder

    def run(self):
        addr = self.dir / 'socket'
        print('SSSSS', addr)
        with socket.socket(socket.AF_UNIX) as s:
            s.bind(str(addr))
            s.listen()
            while True:
                conn, _ = s.accept()
                with conn:
                    command, _, args = conn.recv(1024).decode().partition(' ')
                    if command == 'stop':
                        break
                    if command == 'folder':
                        reply = self.folder(args)
                    elif command == 'folder2':
                        reply = self.folder2(args)
                    elif command == 'env':
                        folder, *uids = args.split()
                        reply = self.envelope(folder,
                                              [int(uid) for uid in uids])
                    conn.sendall(pickle.dumps(reply, pickle.HIGHEST_PROTOCOL))
        addr.unlink()

    def folder(self, name):
        with self.db as db:
            uids = [uid for uid in
                    db.execute('SELECT uid FROM mails WHERE folder=?',
                               [name])]
            folders = [fname for fname in
                       db.execute('SELECT name FROM folders WHERE folder=?',
                                  [name])]
        return (uids, folders)

    def folder2(self, name):
        self.server.select_folder(name)
        messages = self.server.search(['NOT', 'DELETED'])
        print(messages)
        print(self.server.list_folders())

    def envelope(self, name, uids):
        self.server.select()  # name)
        missing: List[int] = []
        with self.db as db:
            for uid in uids:
                result = list(db.execute('SELECT * FROM mails WHERE uid=?',
                                         [uid]))
                if result:
                    print(result)
                else:
                    missing.append(uid)
        if missing:
            print(','.join(str(uid) for uid in missing))
            data = self.server.uid('FETCH',
                                   ','.join(str(uid) for uid in missing),
                                   # '(INTERNALDATE ENVELOPE BODY[HEADER])',
                                   'RFC822.HEADER')
            status, response = data
            import email
            m = email.message_from_bytes(response[0][1])
            # data = self.server.fetch(missing, ['ENVELOPE'])
            # from pprint import pprint
            for k, v in m.items():
                print(f'{k}: ({type(v)})\n{v}\n')


if __name__ == '__main__':
    name = sys.argv[1]
    if len(sys.argv) == 2:
        s = Server(name)
        # .run()
        s.envelope('INBOX', [17495])
    else:
        addr = Path.home() / '.spelltinkle' / 'mail' / name / 'socket'
        with socket.socket(socket.AF_UNIX) as sock:
            sock.connect(str(addr))
            sock.send(' '.join(sys.argv[2:]).encode())
            if sys.argv[2] != 'stop':
                print(pickle.loads(b''.join(iter(lambda: sock.recv(8096),
                                                 b''))))
