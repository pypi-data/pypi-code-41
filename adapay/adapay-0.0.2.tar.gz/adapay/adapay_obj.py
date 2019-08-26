class AdapayObject(dict):

    def __init__(self):
        super(AdapayObject, self).__init__()

    def __setattr__(self, k, v):
        if k[0] == '_' or k in self.__dict__:
            return super(AdapayObject, self).__setattr__(k, v)

        self[k] = v

    def __getattr__(self, k):
        if k[0] == '_':
            raise AttributeError(k)

        try:
            return self[k]
        except KeyError as err:
            raise AttributeError(*err.args)

    def __delattr__(self, k):
        if k[0] == '_' or k in self.__dict__:
            return super(AdapayObject, self).__delattr__(k)
        else:
            del self[k]

    def __setitem__(self, k, v):
        if v == "":
            raise ValueError(
                "You cannot set %s to an empty string. "
                "We interpret empty strings as None in requests."
                "You may set %s.%s = None to delete the property" % (
                    k, str(self), k))

        super(AdapayObject, self).__setitem__(k, v)

    def __getitem__(self, k):
        try:
            return super(AdapayObject, self).__getitem__(k)
        except KeyError as err:
            raise err

    def __delitem__(self, k):
        super(AdapayObject, self).__delitem__(k)

        if hasattr(self, '_attrs'):
            self._attrs.remove(k)

    def __setstate__(self, state):
        self.update(state)

    def __reduce__(self):
        reduce_value = (
            type(self),  # callable
            (  # args
                self.get('id', None),
                self.api_key
            ),
            dict(self),  # state
        )
        return reduce_value

    @classmethod
    def construct_from(cls, info_obj):
        instance = cls()

        instance.refresh_from(info_obj)
        return instance

    def refresh_from(self, values):
        from adapay.utils.param_handler import parse_to_adapay_object

        for k, v in iter(values.items()):
            super(AdapayObject, self).__setitem__(k, parse_to_adapay_object(v))
