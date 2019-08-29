import os

from vmtlib.vmt_object import VmtObject

# TODO args with spaces in ""


class VmtFile:
    def __init__(self, path=None):
        self._content = ""

        self.path = path
        self.shader = None

    def __str__(self):
        return self.shader.stringify()

    @property
    def initialized(self):
        return self.shader is not None

    @property
    def filename(self):
        return os.path.basename(self.path) if self.path is not None else None

    @property
    def directory(self):
        return os.path.dirname(os.path.abspath(self.path)) if self.path is not None else None

    @property
    def dict(self):
        return {self.shader.name: self.shader.dict}

    def from_dict(self, dict):
        if len(dict) == 1:
            key = list(dict.keys())[0]
            self.shader = VmtObject(name=key, dict=dict[key])
        else:
            raise ValueError("The dict can only contain one key for the shader name!")

    def read(self):
        with open(self.path, "r") as file:
            self._content = file.read()

            shader_obj = VmtObject.detect_objects(self._content)
            self.shader = VmtObject(shader_obj["name"], shader_obj["span"], self._content)

    def write(self, target):
        if not os.path.exists(os.path.dirname(os.path.abspath(target))):
            raise FileNotFoundError

        with open(target, "w") as file:
            file.write(str(self))

