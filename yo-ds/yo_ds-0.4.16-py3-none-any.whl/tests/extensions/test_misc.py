from yo_extensions.misc import *
from tests.extensions.common import *
from IPython.display import HTML

class MiscTests(TestCase):
    def test_json(self):
        os.makedirs(path('misc_files'),exist_ok=True)
        jsonpath = path('misc_files','test.json')
        obj = dict(a=1,b='2')
        IO.write_json(obj,jsonpath)
        self.assertDictEqual(
            dict(a=1,b='2'),
            IO.read_json(jsonpath))

    def test_json_1(self):
        jsonpath = path('misc_files', 'test1.json')
        obj = dict(a=1, b='2')
        IO.write_json(obj,jsonpath)
        rs = IO.read_json(jsonpath,as_obj=True)
        self.assertDictEqual(
            dict(a=1, b='2'),
            rs)
        self.assertIsInstance(rs,Obj)


    def test_pickle(self):
        jsonpath = path('misc_files', 'test.pkl')
        obj = dict(a=1, b='2')
        IO.write_pickle(obj, jsonpath)
        self.assertDictEqual(
            dict(a=1, b='2'),
            IO.read_pickle(jsonpath))

    def test_printable(self):
        self.assertIsInstance(notebook_printable_version(True),HTML)
        self.assertIsNone(notebook_printable_version(False))

    def test_find_root_fails(self):
        self.assertRaises(ValueError,lambda: IO.find_root_folder('aigjixfjbvijfdawemnarldsncolkcznvoisalmenfwsefdfsdvlskdapejr'))


    def test_diffset_no(self):
        r = diffset([1,2],[2,3])
        self.assertFalse(r.Match)
        self.assertFalse(r.LeftIsSubset)
        self.assertFalse(r.RightIsSubset)
        self.assertEqual(1,r.Intersection)

    def test_diffset_left(self):
        r = diffset([1,2],[1,2,3])
        self.assertFalse(r.Match)
        self.assertTrue(r.LeftIsSubset)
        self.assertFalse(r.RightIsSubset)
        self.assertEqual(2,r.Intersection)


    def test_diffset_right(self):
        r = diffset([1,2, 3],[2,3])
        self.assertFalse(r.Match)
        self.assertFalse(r.LeftIsSubset)
        self.assertTrue(r.RightIsSubset)
        self.assertEqual(2,r.Intersection)


    def test_diffset_match(self):
        r = diffset([1,2, 3],[1, 2,3])
        self.assertTrue(r.Match)
        self.assertTrue(r.LeftIsSubset)
        self.assertTrue(r.RightIsSubset)
        self.assertEqual(3,r.Intersection)
