import pandas as pd
from .validators.country_validation_helpers.country_detector import CountryDetector
from .color_printer import ColorPrinter


class DataPreprocessor:
    DETECTED_CC = "DETECTED_CC"

    @staticmethod
    def preprocess(data):
        df = pd.DataFrame(data).reset_index().rename({"index": "rowNumber"}, axis=1)
        if df.empty or len(df.columns) < 13:  # hardcoded number of required columns (eventually should not hc)
            ColorPrinter.printRedBanner("Error reading data. Make sure the dataset is not empty and that it has all "
                                        "the required columns. Also, ensure that you're using comma as the delimiter.")
            exit(0)

        df[DataPreprocessor.DETECTED_CC] = df.apply(CountryDetector.detect, axis="columns")
        return df
