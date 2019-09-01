import os


class FileSystem:
    @staticmethod
    def save(filename, code):
        with open(filename, "w") as f:
            f.write(code)

    @staticmethod
    def open(filename):
        with open(filename, "r") as f:
            return f.read()

    @classmethod
    def list_files(cls, directory):
        dic = {}
        for i in os.listdir(directory):
            if os.path.isdir(i):
                dic[i] = cls.list_files(i)
            else:
                dic[i] = None

        return dic

