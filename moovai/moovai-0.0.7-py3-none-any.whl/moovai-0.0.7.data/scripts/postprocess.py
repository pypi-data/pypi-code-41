class Postprocess:
    def __init__(self, scaler):
        self.scaler = scaler

    def inverse_transform(self, data):
        result = self.scaler.inverse_transform(data).flatten()[0]
        return result

