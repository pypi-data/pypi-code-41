class ApiNode():
    """Api dot access facility"""

    def __setitem__(self, k, v):
        setattr(self, k, v)

    def __getitem__(self, y):
        return getattr(self, y)
