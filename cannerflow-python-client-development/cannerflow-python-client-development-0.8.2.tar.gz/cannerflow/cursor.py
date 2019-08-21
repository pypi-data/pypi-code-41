import cannerflow.exceptions
__all__ = ["Cursor"]

class Cursor(object):
    def __init__(self, stats, columns, data):
        self._default_size = 1
        self._stats = stats
        self._columns = columns
        self._data = data
        self._iterator = iter(data)

    @property
    def description(self):
        if self._columns is None:
            return None

        # [ (name, type_code, display_size, internal_size, precision, scale, null_ok) ]
        return [
            (col["name"], col["type"], None, None, None, None, None)
            for col in self._columns
        ]

    @property
    def rowcount(self):
        return len(self._data)

    @property
    def stats(self):
        return self._stats

    def get_one(self):
        try:
            return next(self._iterator)
        except StopIteration:
            return None
        except cannerflow.exceptions.HttpError as err:
            raise cannerflow.exceptions.OperationalError(str(err))

    def get_many(self, size=None):
        if size is None:
            size = self._default_size

        result = []
        for _ in range(size):
            row = self.get_one()
            if row is None:
                break
            result.append(row)

        return result

    def get_all(self):
        return self._data

    def get_rest(self):
        result = []
        row = self.get_one()
        while(row is not None):
            result.append(row)
            row = self.get_one()
        return result