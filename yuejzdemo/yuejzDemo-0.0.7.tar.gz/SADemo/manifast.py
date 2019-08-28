# from bitarray import bitarray
import pickle as pickle
path = "/Users/yuejz/Desktop/com.csii.zybk.ui_423/AndroidManifest.xml";

fh = open(path, 'rb')
a = fh.read()

print(a)

f = open(r'/Users/yuejz/Desktop/com.csii.zybk.ui_423/AndroidManifest.xml', 'rb')

d = pickle.load(f)

f.close()

print(d)
