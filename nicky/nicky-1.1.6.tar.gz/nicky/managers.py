import os

from nicky.utils import SOURCE_PATH, SUPPORT_LANG_LIST


class PathManager:
    @classmethod
    def lang_path(cls, lang='ko'):
        if lang not in SUPPORT_LANG_LIST:
            raise ValueError('unsupported language.')
        return os.path.join(SOURCE_PATH, lang)

    @classmethod
    def suffix_path(cls, lang='ko'):
        return os.path.join(cls.lang_path(lang), 'suffix.txt')

    @classmethod
    def prefix_path(cls, lang='ko'):
        return os.path.join(cls.lang_path(lang), 'prefix.txt')


class LoadManager:
    def __init__(self, lang='ko'):
        self.lang = lang

    def get_prefix_file(self, mode='r'):
        return open(PathManager.prefix_path(self.lang), mode)

    def get_suffix_file(self, mode='r'):
        return open(PathManager.suffix_path(self.lang), mode)

    def get_suffix_list(self):
        return [i for i in self.get_suffix_file().read().split('\n') if i]

    def get_prefix_list(self):
        return [i for i in self.get_prefix_file().read().split('\n') if i]


class SourceManager:
    def __init__(self, lang='ko'):
        self.lang = lang
        self.loader = LoadManager(lang)

    def write(self, values, item_list, f):
        for v in values:
            if not v:
                continue
            elif v in item_list:
                print('{} is already exists'.format(v))
            else:
                item_list.append(v)

        item_list.sort()
        f.write('\n'.join(item_list))
        f.close()

    def copy(self, path):
        pass

    def suf_ordering(self,):
        li = self.loader.get_suffix_list()
        f = self.loader.get_suffix_file('w')
        self.write([], li, f)

    def pre_sorting(self):
        li = self.loader.get_prefix_list()
        f = self.loader.get_prefix_file('w')
        self.write([], li, f)

    def suf_add(self, values):
        li = self.loader.get_suffix_list()
        f = self.loader.get_suffix_file('w')
        self.write(values, li, f)

    def pre_add(self, values):
        li = self.loader.get_prefix_list()
        f = self.loader.get_prefix_file('w')
        self.write(values, li, f)
