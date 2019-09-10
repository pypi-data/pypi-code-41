# coding:utf-8
import random

a = ''.join(random.sample(['z','y','x','w','v','u','t','s','r','q','p','o','n','m','l','k',
                             'j','i','h','g','f','e','d','c','b','a'], 5))
b = ''.join(random.sample(['1','2','3','4','5','6','7','8','9','0'],5))

def getstring():
    m = ''.join(random.sample(['z','y','x','w','v','u','t','s','r','q','p','o','n','m','l','k',
                             'j','i','h','g','f','e','d','c','b','a'], 5))
    n = ''.join(random.sample(['1','2','3','4','5','6','7','8','9','0'],5))
    return m + n
