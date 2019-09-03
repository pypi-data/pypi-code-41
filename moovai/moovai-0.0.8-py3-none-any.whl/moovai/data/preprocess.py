

class Preprocess:
    def __init__(self, scaler):
        self.scaler = scaler

    def transform(self, df):
        result = self.scaler.transform(df)
        return result

