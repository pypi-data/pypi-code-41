from pathlib import Path
import time
import numpy as np 
from functools import wraps
import re
from matplotlib import pyplot as plt
import sys
def result_wrapper(func,last_info=[0,1]):
    @wraps(func)
    def wrapper(*args, **kwargs):
        t = func(*args, **kwargs)
        if t is None:
            return np.array([])
        t = [i.split() for i in t]
        if t and not t[-1][2].isdigit():
            if t[0][2].isdigit():
                kt = t[-1][2]
                last_digit = 0
                for i,v in enumerate(t):
                    if v[2] == kt:
                        last_digit = i - 1
                        break 
                delta = int(t[last_digit][2]) - int(t[last_digit-1][2])
            else:
                last_digit,delta = last_info
            for i in t[last_digit+1:]:
                last_digit += delta
                i[2] = last_digit

            last_info[0] = last_digit
            last_info[1] = delta

        try:
            t = np.array(t,dtype='float32')
        except:
            print(t)
        if not t.any():
            return t
        self = args[0]
        if self.blk is None:
            #取self.blk 为blk序列中的众数
            m = t[:,1]
            m = m[1:] - m[:-1]
            m = t[:,1][np.where(m==0)]
            self.blk = m[0]

        t = t[np.where(np.abs(t[:,1] - self.blk)<0.01)]
        return t
    return wrapper
class Residual:
    def __init__(self,filename):
        self.filename = Path(filename)
        self.pos=-1
        self.titles = None
        self.re_res = None
        self.latest_mtime = 0
        self.re_res = self.get_re_res()
        self.blk = None
        self.iter_last = 0
    def get_re_res(self):
        fp = open(self.filename,'r')
        for i in fp:
            if i.find('total res.')!=-1:
                self.titles = re.split(' {2,}',i)
                n = len(self.titles) - 3
                return re.compile('\s+\d+\s+\d+\s+(\d+|\*{{6}})\s+([-\.\d]+E[\+-]\d+\s+){{{n}}}'.format(n = n))
        return None

    @result_wrapper
    def get(self):
        mtime = self.filename.lstat().st_mtime
        if mtime <= self.latest_mtime:
            return []
        self.latest_mtime = mtime
        fp = open(self.filename,'r')
        if self.re_res is None:
            t = self.get_re_res()
            if t is not None:
                self.re_res = t
            else:
                return None
        fp.seek(self.pos+1,0)
        res_list = [i for i in fp if self.re_res.match(i)]
        self.pos = fp.tell()
        return res_list
    def get_history(self):
        fp = open(self.filename,'r')
        is_title = False
        title_re = re.compile(' *iteration *residual *CL *CD *CY *CMY.*')
        data_re  = re.compile('( +\d+)( +[\.\dEe\+\-]+)( +[\.\dEe\+\-]+)( +[\.\dEe\+\-]+)( +[\.\dEe\+\-]+)( +[\.\dEe\+\-]+)')
        result = []
        for line in fp:
            if title_re.match(line):
                is_title = True 
                continue
            if is_title==True:
                t = data_re.findall(line)
                if t:
                    result.append(t)
                else:
                    break
        if not is_title:
            return np.array([])
        result = np.array(result,dtype = 'float32').reshape((len(result),-1))
     

        result = np.hstack((result[:,-2:],result,(result[:,-2:])))
        result[:,4] = result[:,3]
        return result

def run(filename,interval):
    plt.ion()
    plt.figure(filename)
    res = Residual(filename)
    k = res.get_history()
    is_first = True
    min_shape = None
    try:
        while True:
            k2 = res.get()
            if is_first:
                if k.any():
                    min_shape = min(k.shape[1],k2.shape[1])
                    k = np.vstack((k[:,:min_shape],k2[:,:min_shape]))
                else:
                    k = k2
                    min_shape = k2.shape[1]
            
            else:
                if not k2.any():
                    plt.pause(2*interval)
                    continue
                else:
                    k = np.vstack((k[-1:,:min_shape],k2[:,:min_shape]))
            x = k[:,2]
            y1 = k[:,3]
            y2 = k[:,4]
            plt.semilogy(x,y1,'k-',label='$residual$')
            plt.semilogy(x,y2,'b-',label = '$total res.$')
            l = k[-1]
            titles = res.titles
            for i in range(5,k.shape[1]):
                if not titles:break
                if titles[i] == 'time':break
                if abs(l[i]) > 1e-18:
                    y = np.abs(k[:,i])
                    plt.semilogy(x,y,label='${}$'.format(titles[i]))
            plt.xlabel('$iterations$')
            plt.ylabel('$res$')
            if is_first:
                plt.legend()
            plt.pause(interval)
            is_first = False
    except:
        pass
def run_sub(filename,interval):
    plt.figure(filename)
    fp = open(filename)
    fp.readline()
    xy = np.array([i.split()[:2] for i in fp],dtype='float32')
    plt.plot(xy[:,0],xy[:,1])
    plt.show()
def find_parm(p):
    for i,v in enumerate(sys.argv):
        if v.strip() == p:
            if p[:2]=='--':return True
            return sys.argv[i+1]
    return None
if __name__ == '__main__':
    fname = None
    interval = find_parm('-t')
    if interval:
        interval = float(interval)
    else:
        interval = 10
    fname = find_parm('-i')
    if not fname:
        fname = [i.name for i in Path('./').glob('*.out') if i.name != 'precfl3d.out']
        if len(fname)>=2:
            print('Warning: too many out files',fname)
        if fname:
            fname = fname[0]
    fsub = find_parm('--s') 
    if fsub:
        fsub = 'cfl3d.subit_res'
        run_sub(fsub,interval)
    else:
        run(fname,interval)


    
