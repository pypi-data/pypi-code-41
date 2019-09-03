class DataFrameError(Exception):
    def __init__(self, text):
        super().__init__(text)


class StepError(Exception):
    def __init__(self, text):
        super().__init__(text)


class ColumnNotFound(Exception):
    def __init__(self, text):
        super().__init__(text)


class ProcessorError(Exception):
    def __init__(self, text):
        super().__init__(text)


class ConversionError(Exception):
    def __init__(self, text):
        super().__init__(text)
