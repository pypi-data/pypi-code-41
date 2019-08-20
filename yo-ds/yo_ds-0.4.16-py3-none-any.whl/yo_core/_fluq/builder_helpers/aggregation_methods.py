from typing import *
import math
import copy

class BaseAggregation:
    def reset(self):
        raise NotImplementedError()
    def account(self, element):
        raise NotImplementedError()
    def report(self):
        raise NotImplementedError()
    def get_name(self):
        raise NotImplementedError()
    def process(self, en):
        self.reset()
        for e in en:
            self.account(e)
        return self.report()

class Sum(BaseAggregation):
    def __init__(self):
        self.sum=0
        self.has_elements = False

    def reset(self):
        self.sum=0
        self.has_elements = False

    def account(self, element):
        self.sum+=element
        self.has_elements = True

    def report(self):
        if not self.has_elements:
            return None
        return self.sum

    def get_name(self):
        return 'sum'


class Count(BaseAggregation):
    def __init__(self,as_float : bool =False):
        self.cnt = 0
        self.as_float = as_float
    def reset(self):
        self.cnt = 0

    def account(self, element):
        self.cnt+=1

    def report(self):
        if self.as_float:
            return float(self.cnt)
        else:
            return self.cnt

    def get_name(self):
        return 'count'


class Mean(BaseAggregation):
    def __init__(self):
        self.sum = 0
        self.cnt = 0

    def reset(self):
        self.sum=0
        self.cnt=0

    def account(self, element):
        self.sum+=element
        self.cnt += 1

    def report(self):
        if self.cnt==0:
            return None
        return self.sum/float(self.cnt)

    def get_name(self):
        return 'mean'

class Min(BaseAggregation):
    def __init__(self):
        self.min = None
        self.has_element = False

    def reset(self):
        self.min = None
        self.has_element = False

    def account(self, element):
        self.has_element = True
        if self.min is None or self.min>element:
            self.min = element

    def report(self):
        if not self.has_element:
            return None
        return self.min

    def get_name(self):
        return 'min'


class Max(BaseAggregation):
    def __init__(self):
        self.max = None
        self.has_element = False

    def reset(self):
        self.max = None
        self.has_element = False

    def account(self, element):
        self.has_element = True
        if self.max is None or self.max<element:
            self.max = element

    def report(self):
        if not self.has_element:
            return None
        return self.max

    def get_name(self):
        return 'max'

class Any(BaseAggregation):
    def __init__(self):
        self.any = None

    def reset(self):
        self.any = False

    def account(self, element):
        if element:
            self.any = True

    def report(self):
        return self.any

    def get_name(self):
        return 'any'


class All(BaseAggregation):
    def __init__(self):
        self.all = None

    def reset(self):
        self.all = True

    def account(self, element):
        if not element:
            self.all = False

    def report(self):
        return self.all

    def get_name(self):
        return 'all'


class Std(BaseAggregation):
    def __init__(self):
        self.mean = None
        self.count = None
        self.M2 = None

    def reset(self):
        self.mean = 0
        self.count = 0
        self.M2 = 0

    def account(self, element):
        self.count += 1
        delta = element - self.mean
        self.mean += delta / self.count
        delta2 = element - self.mean
        self.M2 += delta * delta2

    def report(self):
        if self.count<2:
            return None
        return math.sqrt(self.M2/(self.count))

    def get_name(self):
        return 'std'



class ListAggregator(BaseAggregation):
    def __init__(self, *aggs: BaseAggregation):
        self.aggs = aggs
        if len(self.aggs) == 0:
            raise ValueError('No aggregators are provided')

    def reset(self):
        for a in self.aggs:
            a.reset()

    def account(self, element):
        for a in self.aggs:
            a.account(element)

    def report(self):
        if len(self.aggs)==1:
            return self.aggs[0].report()
        return {z.get_name(): z.report() for z in self.aggs}

    def get_name(self):
        return 'ListAggregator'

class _FieldListAggregatorComponent:
    def __init__(self, name: str, selector:Optional[Callable], agg: ListAggregator):
        self.name=name
        if selector is not None:
            self.selector = selector
        else:
            self.selector = lambda z: z[name]
        self.agg = agg


class _FieldListAggregatorPromise:
    def __init__(self, aggregator: 'Aggregator', name: str, selector: Optional[Callable]):
        self.fields_list = [(name,selector)]
        self._aggregator = aggregator

    def to_field(self, name, selector: Optional[Callable] = None):
        self.fields_list.append((name,selector))
        return self

    def apply(self, *aggs: BaseAggregation):
        for pair in self.fields_list:
            self._aggregator._components.append(_FieldListAggregatorComponent(pair[0],pair[1],copy.deepcopy(ListAggregator(*aggs))))
        return self._aggregator



class Aggregator(BaseAggregation):
    def __init__(self):
        self._components = [] # type: List[_FieldListAggregatorComponent]

    def to_field(self, name: str, selector: Optional[Callable]=None):
        return _FieldListAggregatorPromise(self,name,selector)

    def reset(self):
        for c in self._components:
            c.agg.reset()


    def account(self, element):
        for c in self._components:
            c.agg.account(c.selector(element))

    def report(self):
        return {c.name:c.agg.report() for c in self._components}

    def get_name(self):
        return 'Aggregator'

class BucketAggregator(BaseAggregation):
    def __init__(self, aggregator: BaseAggregation, *buckets: Callable):
        self.aggregator = aggregator
        self.buckets = buckets
        self.result = None # type: Dict

    def reset(self):
        self.result = {}

    def account(self, element):
        current = self.result
        for index, bucket in enumerate(self.buckets):
            key = bucket(element)
            if key not in current:
                if index == len(self.buckets)-1:
                    current[key] = copy.deepcopy(self.aggregator)
                    current[key].reset()
                else:
                    current[key] = {}
            current = current[key]
        if not isinstance(current,BaseAggregation):
            raise ValueError('Internal error: aggregator should be in the end of the bucket, but was {0}'.format(current))
        current.account(element)

    def _recoursive_report(self, current, depth):
        if depth==len(self.buckets):
            return current.report()
        return {key:self._recoursive_report(value,depth+1) for key, value in current.items()}

    def report(self):
        return self._recoursive_report(self.result,0)


def aggregate_with(en, selector:Optional[Callable] = None, *args: BaseAggregation):
    list_agg = ListAggregator(*args)
    list_agg.reset()
    for e in en:
        if selector is None:
            p = e
        else:
            p = selector(e)
        list_agg.account(p)
    return list_agg.report()

