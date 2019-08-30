import functools
import copy

def inplace_wrapper(func):
    @functools.wraps(func)
    def wrapper(obj,**kwargs):
        inplace = dflt_kwargs('inplace',False,**kwargs)
        if(inplace):
            return(func(obj,**kwargs))
        else:
            nobj = copy.deepcopy(obj)
            return(func(nobj,**kwargs))
    return(wrapper)


def keep_ptr_wrapper(func):
    @functools.wraps(func)
    def wrapper(obj,**kwargs):
        keep_ptr = dflt_kwargs('keep_ptr',False,**kwargs)
        nobj = copy.deepcopy(obj)
        nobj = func(nobj,**kwargs)
        if(keep_ptr):
            obj.clear()
            if(isinstance(obj,list)):
                obj.extend(nobj)
            elif(isinstance(obj,dict)):
                obj.update(nobj)
            else:
                pass
            return(obj)
        else:
            return(nobj)
    return(wrapper)





def dflt_kwargs(k,dflt,**kwargs):
    if(k in kwargs):
        v = kwargs[k]
    else:
        v = dflt
    return(v)


def self_kwargs(self,kl,dfltl,**kwargs):
    for i in range(len(kl)):
        k = kl[i]
        if(k in kwargs):
            self.__setattr__(k,kwargs[k])
        else:
            self.__setattr__(k,dfltl[i])
    return(self)


def de_args(kl,dfltl,*args):
    d = {}
    args_len = len(args)
    kl_len = len(kl)
    for i in range(args_len):
        k = kl[i]
        d[k] = args[i]
    for i in range(args_len,kl_len):
        k = kl[i]
        d[k] = dfltl[i]
    return(d)


def pipeline(funcs):
    def _pipeline(funcs,arg):
        func = funcs[0]
        arg = func(arg)
        for i in range(1,len(funcs)):
            func = funcs[i]
            arg = func(arg)
        return(arg)
    p = functools.partial(_pipeline,funcs)
    return(p)

