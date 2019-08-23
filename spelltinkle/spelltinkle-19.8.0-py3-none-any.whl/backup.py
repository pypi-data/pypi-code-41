from spelltinkle.session import Session


class Backup:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.folder = session.folder / 'backup'
        if not self.folder.is_dir():
            self.folder.mkdir()
        self.n = 0
        self.start()

    def start(self) -> None:
        self.session.loop.call_later(120, self.start)

        if self.n > 0:
            self.do_backup()
            if self.n % 5 == 0:
                self.remove_old_files()

        self.n += 1

    def do_backup(self) -> None:
        for doc in self.session.docs:
            if doc.path and doc.backup_needed:
                doc._write(self.folder / doc.path.name)
                doc.backup_needed = False

    def remove_old_files(self) -> None:
        files = [(f.stat().st_ctime, f) for f in self.folder.glob('*')]
        for t, f in sorted(files)[:-100]:
            f.unlink()
