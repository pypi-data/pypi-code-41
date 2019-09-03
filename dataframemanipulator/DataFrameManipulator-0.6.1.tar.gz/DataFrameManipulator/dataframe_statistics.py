from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype
from pandas.api.types import is_object_dtype


class DataFrameStatistics:
    def __init__(self, table):
        self.table = table

    def run(self, columnName):
        stat = dict()
        val_count = dict()
        missing_value_count = self.table[columnName].isnull().sum()
        indices = list(missing_value_count.index)
        missing_values = {}
        for index in indices:
            missing_values[index] = missing_value_count[index]
        try:
            statistics = self.table[columnName].describe()
            value_counts = self.table[columnName].value_counts(dropna=False)
            if not statistics.empty:
                if is_numeric_dtype(self.table[columnName]):
                    stat = {'count': statistics[0], 'mean': statistics[1], 'std': statistics[2], 'min': statistics[3],
                            '1stQtile': statistics[4], '2ndQtile': statistics[5], '3rdQtile': statistics[6],
                            'max': statistics[7]}
                elif is_string_dtype(self.table[columnName]) or is_object_dtype(self.table[columnName]):
                    stat = {'count': statistics[0], 'unique': statistics[1], 'top': statistics[2],
                            'frequence': statistics[3]}
                    if not value_counts.empty:
                        for i, name in enumerate(value_counts.index):
                            val_count.update({str(name): list(value_counts)[i]})

            return {'statistics': stat, 'value_counts': val_count, 'missing_counts': missing_values}
        except:
            return {'statistics': stat, 'value_counts': val_count, 'missing_counts': missing_values}
