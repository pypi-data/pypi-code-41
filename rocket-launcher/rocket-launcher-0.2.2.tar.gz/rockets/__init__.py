import os,sys
path=__file__.split('/')
del path[-1]
path='/'.join(path)
for i in os.listdir(path):
    if i.split('.')[-1]=='py' and i!='__init__.py':
        f=open(path+'/'+i,'r')
        exec(f.read())
