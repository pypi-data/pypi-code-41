from tests.core.common import *
import numpy


class AggregationMethodsTests(LinqTestBase):


    def test_count(self):
        self.assertEqual(3,Query.args(1,2,3).count())

    def test_count_float(self):
        t = Query.args(1,2,3).aggregate_with(agg.Count(True))
        self.assertIsInstance(t,float)
        self.assertEqual(3.0,t)

    def test_sum(self):
        self.assertEqual(6,Query.args(1,2,3).sum())

    def test_sum_on_empty(self):
        self.assertIsNone(Query.args().sum())

    def test_min(self):
        self.assertEqual(1,Query.args(1,2,3).min())

    def test_min_on_empty(self):
        self.assertIsNone(Query.args().min())

    def test_max(self):
        self.assertEqual(3,Query.args(1,2,3).max())

    def test_max_on_empty(self):
        self.assertIsNone(Query.args().max())

    def test_mean(self):
        self.assertEqual(2.0,Query.args(1,2,3).mean())

    def test_mean_on_empty(self):
        self.assertIsNone(Query.args().mean())

    def test_std(self):
        for i in range(10):
            r = numpy.random.RandomState(i).rand(10)
            expected = numpy.std(r)
            actual = Query.en(r).aggregate_with(agg.Std())
            self.assertAlmostEqual(expected,actual,5)




    def test_all_1(self):
        self.assertEqual(True, Query.args(1, 2, 3).all(lambda z: z > 0))

    def test_all_2(self):
        self.assertEqual(False, Query.args(1, 2, 3).all(lambda z: z > 1))

    def test_all_3(self):
        self.assertEqual(True, Query.args(dict()).all())

    def test_all_4(self):
        self.assertEqual(True, Query.args().all())


    def test_any_1(self):
        self.assertEqual(True, Query.args(1, 2, 3).any(lambda z: z > 1))

    def test_any_2(self):
        self.assertEqual(False, Query.args(1, 2, 3).any(lambda z: z < 1))

    def test_any_3(self):
        self.assertEqual(True, Query.args(dict()).any())

    def test_any_4(self):
        self.assertEqual(False, Query.args().any())




    def test_aggregate_with(self):
        self.assertDictEqual({'sum':6,'count':3,'mean':2.0},Query.args(1,2,3).aggregate_with(agg.Sum(),agg.Count(),agg.Mean()))


    def test_aggregator(self):
        self.assertDictEqual(
            {
                'a': {
                    'min': 1,
                    'max': 3
                },
                'b': 20.0,
                'sum' : {
                    'min': 11,
                    'mean': 22.0
                }
            },
            Query.args(1,2,3).select(lambda z: Obj(a=z, b=10*z)).aggregate_with(
                agg.Aggregator()
                .to_field('a').apply(agg.Min(),agg.Max())
                .to_field('b').apply(agg.Mean())
                .to_field('sum',lambda z: z['a']+z['b']).apply(agg.Min(),agg.Mean())
            ))

    def test_aggregator_and_to(self):
        self.assertDictEqual({
                'a': {'min':1,'max':3},
                'b': {'min':10, 'max':30}
            },
            Query.args(1,2,3).aggregate_with(agg.Aggregator()
                                             .to_field('a',lambda z: z)
                                             .to_field('b',lambda z: 10*z)
                                             .apply(agg.Min(),agg.Max())))


    def test_bucket_aggregator(self):
        tst = []
        for a in range(3):
            for b in range(3):
                for i in range(a+b):
                    tst.append(dict(a=a,b=b))
        ag = agg.BucketAggregator(
            agg.Count(),
            lambda z: z['a'],
            lambda z: z['b']
        )

        result = ag.process(tst)
        expected = {0: {1: 1, 2: 2}, 1: {0: 1, 1: 2, 2: 3}, 2: {0: 2, 1: 3, 2: 4}}
        self.assertDictEqual(expected,result)



