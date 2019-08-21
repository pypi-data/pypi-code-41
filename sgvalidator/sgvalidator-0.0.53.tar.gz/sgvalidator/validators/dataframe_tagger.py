class DataframeTagger:
    TAG_COLUMN_NAME = "REASON"

    @staticmethod
    def tagRows(df, func):
        if df.empty:
            return df

        copied = df.copy()
        reasonSeries = copied.apply(func, axis=1)
        copied[DataframeTagger.TAG_COLUMN_NAME] = reasonSeries
        mask = reasonSeries.astype("bool")
        return copied[mask]
