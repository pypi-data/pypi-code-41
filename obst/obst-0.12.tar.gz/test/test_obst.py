import unittest
import obst
import shutil
import numpy as np
import pickle

TEST_PATH = "test_obst"

class TestObst(unittest.TestCase):

    def setUp(self):
        try:
            shutil.rmtree(TEST_PATH)
        except:
            print("Error while deleting dir ", TEST_PATH)

        self.test = obst.open_obst(TEST_PATH)
        
        scan = range(4)
        avg = range(2)
        other = range(2)

        sw = True
        for s in scan:
            sub = self.test.sub("Scan_" + str(s))
            for a in avg:
                for o in other:
                    data = np.random.rand(10)
                    obj = obst.object(name='' + str(a) + str(s) + str(o))
                    obj.meta["scan"] = s
                    obj.meta["avg"] = a
                    obj.meta["other"] = {'test' : o}
                    obj.meta["stuff"] = sw
                    sw = not sw
                    obj.data = pickle.dumps(data)
                    sub.insert(obj)

    def test_filter(self):

        def filter_true(meta):
            if 'stuff' in meta:
                if meta['stuff']:
                    return True
            return False

        def filter_false(meta):
            if 'stuff' in meta:
                if not meta['stuff']:
                    return True
            return False

        #index = test.index(["avg", "scan", "other.test"], filter=filter_one)
        indices = self.test.indices([["avg", "scan", "other.test", "stuff"], ["avg", "scan" , "other.test", "stuff"]], idx_filter = [filter_true,filter_false])

        self.assertTrue(True)
 
if __name__ == '__main__':
    unittest.main()