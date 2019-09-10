import obst
import numpy as np
import pickle
import shutil

TEST_PATH = "test_obst"

try:
    shutil.rmtree(TEST_PATH)
except:
    print("Error while deleting dir ", TEST_PATH)

test = obst.open_obst(TEST_PATH)


scan = range(4)
avg = range(2)
other = range(2)

#TODO build in that meta can be only string keys

print("Create Files...")
import random
random.seed(13453314)
# sw = 1

for s in scan:
    sub = test.sub("Scan_" + str(s))
    for a in avg:
        for o in other:
            data = np.random.rand(10)
            obj = obst.object(name='' + str(a) + str(s) + str(o), unique_id=True)
            obj.meta["scan"] = s
            obj.meta["avg"] = a
            obj.meta["other"] = {'test' : o}
            obj.meta["stuff"] = random.randint(0,1)
            obj.data = pickle.dumps(data)
            sub.insert(obj)


### Now traverse data diffently

print("Create Index....")


def filter_one(meta):
    if 'stuff' in meta:
        if meta['stuff'] == 1:
            return True

    return False

def filter_zero(meta):
    if 'stuff' in meta:
        if meta['stuff'] == 0:
            print("zero")
            return True

    return False

#index = test.index(["avg", "scan", "other.test"], filter=filter_one)
indices = test.indices([["avg", "scan", "other.test", "stuff"], ["avg", "scan" , "other.test", "stuff"]], idx_filter = [filter_one,None])


index = indices[0]

print("Traverse Index...")

for avg, avg_data in index.order("avg", "scan", "other.test"):
    for scan, scan_data in avg_data:
        for other, other_data in scan_data:
            objs = other_data
            for obj in objs:
                obj = obj()
                print(avg, scan, obj.meta)
            print('----')




print("=========================")
index = indices[1]
for scan, scan_data in index.order("scan", "avg"):
    for avg, avg_data in scan_data:
            objs = avg_data
            for obj in objs:
                obj = obj()
                print(avg, scan, obj.meta)

                if obj.meta["stuff"] == 1:
                    obj.remove()
                    print("Remove")
            print('----')

print("Search =======================")

#update because element got removed
index.update()
         
res = index.search("scan > 2")
for o in res:
    obj = o()
    print(obj.meta)


test1 = obst.open_obst(TEST_PATH)
sub = test.sub("Scan_1")

obj = obst.object(name='asdasda' + str(1) + str(3) + str(4))
data = np.random.rand(10)
obj.meta["scan"] = 1
obj.meta["avg"] = 3
obj.meta["other"] = {'test' : 4}
obj.data = pickle.dumps(data)
sub.insert(obj)

