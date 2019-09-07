class DefaultParamDict(dict):
    """ Dictionary with default values. """

    def __init__(self, defaults, *args, **kwargs):
        self.update(defaults)
        super().__init__(*args, **kwargs)