# 2019/2/18 by DKZ

import json

def parseConf():
    with open('/etc/pccold.conf','r') as f:
        lines=f.readlines()
    j='{'
    for line in lines:
        l=line.replace('\n','').split('#')[0].strip()
        if l!='':
            k=l.split('=')[0].strip()
            v=l.split('=')[1].strip()
            j=j+'"'+k+'":'+v+','
    j=j[:-1]+'}'
    return json.loads(j)

conf=parseConf()