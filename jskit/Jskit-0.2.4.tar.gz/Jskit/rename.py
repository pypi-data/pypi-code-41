import os, sys


path = '/home/gift/Desktop/新建文件夹'
namelist = os.listdir(path)

for item in namelist:
	if 'GB-T' in item:
		oldname = item
		newname = item.replace('GB-T', 'GB')
		os.rename(os.sep.join([path, oldname]), os.sep.join([path, newname]))

