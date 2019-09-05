class ES54Exception(Exception):
    def __init__(self, *args, **kwargs):
        self.ext_data = None

        if 'ext_data' in kwargs:
            self.ext_data = kwargs.pop('ext_data')
        super().__init__(*args, **kwargs)

    def get_ext_data(self):
        return self.ext_data
