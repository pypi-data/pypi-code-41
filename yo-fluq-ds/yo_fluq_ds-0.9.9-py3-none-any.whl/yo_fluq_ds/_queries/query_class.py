from typing import *
from .._common import *
from .query_helpers import *
from .queryable import Queryable
from yo_fluq import QueryClass as QueryClassBase
import pandas as pd



def _df_iter(dataframe):
    for row in dataframe.iterrows():
        yield Obj(**row[1].to_dict())



class QueryClass(QueryClassBase):
    def en(self, en: Iterable) -> Queryable:
        return super(QueryClass, self).en(en)

    def dict(self, dictionary: Dict) -> Queryable:
        return super(QueryClass, self).dict(dictionary)
    
    def args(self, *args)  -> Queryable:
        return super(QueryClass, self).args(*args)

    file = FileQuery()

    combinatorics = CombinatoricsQuery()

    def folder(self, location: Union[Path, str], pattern: str = '*') -> Queryable[Path]:
        return Queryable(folder(location, pattern))

    def loop(self, begin: Any, delta: Any, end: Any = None, endtype=LoopEndType.NotEqual) -> Queryable:
        return super(QueryClass, self).loop(begin, delta, end, endtype)


    def df(self, dataframe: pd.DataFrame):
        return Queryable(_df_iter(dataframe), dataframe.shape[0])

    def series(self, series: pd.Series) -> Queryable[KeyValuePair]:
        return Queryable(
            map(lambda z: KeyValuePair(z[0],z[1]), zip(series.index,series)),
            series.shape[0]
        )