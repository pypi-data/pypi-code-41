from pathlib import Path


class Configuration:
    initialized = False
    home = Path.home() / '.spelltinkle'

    def read(self):
        if self.initialized:
            return
        filename = self.home / 'config.py'
        if filename.is_file():
            dct = {}
            exec(filename.read_text(), dct)
            if 'user_files' in dct:
                self.user_files = {
                    shortcut: Path(name).expanduser()
                    for shortcut, name in dct['user_files'].items()}
            if 'calender_file' in dct:
                self.calender_file = Path(dct['calender_file']).expanduser()
            self.mail = dct.get('mail', {})

        self.initialized = True


conf = Configuration()
