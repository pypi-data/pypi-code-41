import json
import os

NUMPY_AVAILABLE = 0
try:
    import numpy as np

    NUMPY_AVAILABLE = 1
except:
    pass


class JsonMultiEncoder(json.JSONEncoder):
    def default(self, obj):
        if NUMPY_AVAILABLE:
            if isinstance(obj, np.ndarray):
                return obj.tolist()

            if isinstance(obj, np.number):
                if obj.itemsize > 6:
                    return str(obj.item())
                return obj.item()

        if isinstance(obj, set):
            return list(obj)

        try:
            return json.JSONEncoder.default(self, obj)
        except TypeError:
            return str(obj)


class AbstractJsonDict:
    def __init__(self, data=None, autosave=False, encoder=JsonMultiEncoder):
        if encoder is None:
            encoder = JsonMultiEncoder
        self._encoder = None
        self.encoder = encoder
        self._autosave = autosave
        self._data = {}
        self._file = None
        if data is not None:
            self.data = data
        if autosave:
            self.autosave = autosave

    def _set_data(self, data):
        self._data = data

    def _get_data(self):
        return self._data

    def set_data(self, data):
        self._set_data(data)

    def get_data(self):
        return self._get_data()

    data = property(get_data, set_data)

    def _set_file(self, file):
        self._file = file

    def _get_file(self):
        return self._file

    def set_file(self, file):
        self._set_file(file)

    def get_file(self):
        return self._get_file()

    file = property(get_file, set_file)

    def _set_encoder(self, encoder):
        self._encoder = encoder

    def _get_encoder(self):
        return self._encoder

    def set_encoder(self, encoder):
        self._set_encoder(encoder)

    def get_encoder(self):
        return self._get_encoder()

    encoder = property(get_encoder, set_encoder)

    def _set_autosave(self, autosave):
        self._autosave = autosave

    def _get_autosave(self):
        return self._autosave

    def set_autosave(self, autosave):
        self._set_autosave(autosave)

    def get_autosave(self):
        return self._get_autosave()

    autosave = property(get_autosave, set_autosave)

    def read(self, file):
        with open(file) as f:
            self.data = json.loads(f.read())

    def get(self, *args, default=None, autosave=True):
        d = self.data
        args = [str(arg) for arg in args]
        for arg in args[:-1]:
            arg = str(arg)
            if arg not in d:
                d[arg] = {}
            d = d[arg]

        if args[-1] not in d:
            self.put(*args, value=default, autosave=autosave)

        return d[args[-1]]

    def put(self, *args, value, autosave=True):
        d = self.data
        for arg in args[:-1]:
            arg = str(arg)
            if arg not in d:
                d[arg] = {}
            d = d[arg]

        new = False
        if args[-1] not in d:
            new = True
            d[args[-1]] = None
        elif d[args[-1]] != value:
            new = True
        preval = d[args[-1]]
        d[args[-1]] = value

        if new or (preval != value):
            if self.autosave and autosave:
                self.save()

        return value, new

    def save(self):
        assert self.file is not None, "no file specified"
        if self.file is not None:
            with open(self.file, "w+") as outfile:
                self.stringify_keys()
                outfile.write(self.to_json(indent=4, sort_keys=True))

    def __getitem__(self, key):
        return self.data.get(key)

    def stringify_keys(self, diction=None):
        if diction is None:
            diction = self.data
        for k in list(diction.keys()):
            if isinstance(diction[k], dict):
                self.stringify_keys(diction=diction[k])
            diction[str(k)] = diction.pop(k)

    def to_json(self, indent=None, sort_keys=False):
        return json.dumps(
            self.data, cls=self.encoder, indent=indent, sort_keys=sort_keys
        )

    def get_base_dict(self):
        return self.get_parent(highest=True)

    def get_parent(self, highest=False):
        if not highest:
            return self.parent
        return self.parent.get_parent(highest=highest)

    def getsubdict(self, preamble=None):
        if preamble is None:
            preamble = []
        return JsonSubDict(parent=self, preamble=preamble)

    def __str__(self):
        return self.to_json()


class JsonDict(AbstractJsonDict):
    def __init__(
        self, file=None, data=None, createfile=True, autosave=True, *args, **kwargs
    ):
        if data is not None:
            if isinstance(data, str):
                data = json.loads(data)
            elif isinstance(data, JsonDict):
                data = data.data
        super().__init__(data=data, autosave=autosave, *args, **kwargs)

        if file is not None:
            self.read(file, createfile=createfile)

    def read(self, file, createfile=False):
        try:
            super().read(file)
            self.file = os.path.abspath(file)
        except Exception as e:
            if createfile:
                os.makedirs(os.path.dirname(file), exist_ok=True)
                self.save(file=file)
                self.read(file, createfile=False)
            else:
                raise e

    def _set_data(self, data, file=None):
        if file is not None:
            self.file = os.path.abspath(file)
        super()._set_data(data)

    def save(self, file=None):
        if file is not None:
            self.file = os.path.abspath(file)
        super().save()

    def get_parent(self, highest=True):
        return self


class JsonSubDict(AbstractJsonDict):
    def _set_data(self, data):
        assert isinstance(data, dict), "data is not a dictionary"
        self.parent.put(*self.preamble, value=data)

    def _get_data(self):
        return self.parent.get(*self.preamble, default={})

    def _get_file(self):
        return self.parent.get_file()

    def _get_autosave(self):
        return self.parent.get_autosave()

    def _get_encoder(self):
        return self.parent.get_encoder()

    def save(self):
        self.parent.save()

    def __init__(self, parent, preamble):
        super().__init__()
        if isinstance(preamble, tuple):
            preamble = list(preamble)
        if not isinstance(preamble, list):
            preamble = [preamble]
        self.preamble = preamble
        self.parent = parent
        self.parent.get(*self.preamble, default={})

    def get(self, *args, default=None, autosave=True):
        return self.parent.get(
            *(self.preamble + list(args)), default=default, autosave=autosave
        )

    def put(self, *args, value):
        self.parent.put(*(self.preamble + list(args)), value=value)


if __name__ == "__main__":
    d1 = JsonDict('{"test":[1,2.5,{}]}')
    print(d1)
    a = d1.get("test", default=[])
    a[2]["foo"] = "bar"
    d1.put("test", value=a)
    print(d1)
    d2 = d1.getsubdict("sub1")
    d2.put("sub_", value="folder")
    print(d1)
    print(d2.data)
    d3 = d2.getsubdict(["sub", "dic"])
    print(d2)
    print(d1)
    print(d3.get_base_dict())
    print(d3.get_parent())
    print(d3.get_parent(highest=True))
    print(d3)
