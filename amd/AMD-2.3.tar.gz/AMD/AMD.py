#                                             Delta Version 2.2

##############################################################################################################################################
##############################################################################################################################################
'                                                     IMPORT SECTION:                                                                        '
##############################################################################################################################################
##############################################################################################################################################

def __cmd__(command):
    try:
        import os
        os.system(command)
    except Exception as e:
        print("Something went wrong in accessing the command line. This feature was well tested on All OS.\n This part belongs to importing of modules if they are not installed in your computer yet.\nTry installing matplotlib and pyserial manually via pip.\nAutomatic installation fail due to unaccessable command line !\n")
        print(e)
        raise Exception('Required modules installation failure and failed access to command line !')

def __installationCheck__():
    try:
        import serial
        Module_1=True
    except Exception:
        Module_1=False
        print("pyserial module not found.\nDon't worry, we'll install it in your pc automatically.\nJust make sure you have good internet connection !!")
    try:
        import matplotlib
        Module_2=True
    except Exception:
        Module_2=False
        print("matplotlib module not found.\nDon't worry, we'll install it in your pc automatically.\nJust make sure you have good internet connection !!")

    return(1 if (Module_1 and Module_2)==True else 0)

def __installModules__():
    try:
        __cmd__("pip install pyserial")
        __cmd__("pip install matplotlib")
    except Exception as e:
        print(e)

def __modulesInitialization__():
    n=1
    while(__installationCheck__()!=1):
        __installModules__()
        if(n>3):
            print("This module consists auto-pip package installation yet unable to download 'matplotlib' and 'pyserial'")
            print("Try switching on your internet connection or download those two modules via pip manually")
            raise ModuleNotFoundError
            break
        n+=1
    return

__modulesInitialization__()
import time
from itertools import zip_longest as zip_longest
import serial
from serial import *
import matplotlib.pyplot as plt
from matplotlib import style

##############################################################################################################################################
##############################################################################################################################################
'                                                      Data Science FUNCTIONS :                                                              '
##############################################################################################################################################
##############################################################################################################################################

# Used to hybridize a given set of list
def hybridize(li1,li2=None):
    '''
    Documentation: https://pypi.org/project/AMD/
    Returns a Hybrid.
    If only one argument is passed, It corresponds to y values(amplitude) and x values(index) are automatically generated !
    If two arguments are passed, The 1st argument corresponds to index and the 2nd corresponds to amplitude.
    Both the arguements take a 1 dimensional list.
    '''
    if li2==None:
        li2=li1.copy()
        li1=[i for i in range(len(li2))]
    if(len(li1)!=len(li2)):
        print("Expecting same number of elements in both lists !")
        raise Exception('Both lists must have equal number of elements to be hybridized')
    return(li1,li2)

# Functionality of compress() enhanced to hybrids
def __cpress(index,li=[]):
    try:
        #inittialization
        if li==[] :
            li=index.copy()
            index= [j for j in range(len(li))]


        retli=[li[0]]
        ind=[0]
        i=1
        for i in range(len(li)):
            lastEle = retli[-1]
            currentEle = li[i]
            if (currentEle!=lastEle):
                retli.append(currentEle)
                ind.append(index[i])
        return(ind,retli)
    except Exception as e:
        print(str(e)+"\n ERROR ID - __cpress")
        raise Exception('Unknown Error Occured')

# You know what I do
def __elements(g_string):
    try:
        gstring=str(g_string)
        ng=len(gstring)-1
        lg=list()
        ig=0
        while(ig<=ng):
            lg.append(gstring[ig])
            ig+=1
        return(lg)
    except Exception as e:
        print(str(e)+'\n ERROR ID - elements')
        raise Exception('Unknown Error Occured')

# Checks if all the elements in the given list are unique
def __isunique(Data):
    try:
        nData=len(Data)
        nSet =len(list(set(Data)))
        if(nData==nSet):
            return(True)
        else:
            return(False)
    except Exception as e:
        print(str(e)+'\nERROR ID - isunique')
        raise Exception('Unknown Error Occured')

# draws a line parallel to y axis
def horizontal(y,lbl='horizontal',start=0,end=10,stl='dark_background',color='yellow'):
    '''
    Documentation: https://pypi.org/project/AMD/
    Draws a line parallel to X-axis
    Returns Nothing. Plots nothing. Just a placeholder for plotting functions. Should always be used before plotting functions like Graph, compGraph or visualizeSmoothie.

    Parameter_Name    Default_Value    DataType_Needed_To_Be_Passed
         y                -                 integer/float
         lbl           horizontal              string
         start            0                 integer/float
         end              10                integer/float
         stl           dark_background     (string) one of the styles in this link: https://matplotlib.org/3.1.0/gallery/style_sheets/style_sheets_reference.html
         color           yellow                string

    '''
    try:
        style.use(stl)
        plt.plot([start,end],[y,y],label=lbl,linewidth=2,color=color)
    except Exception as e:
        print(str(e)+'\nERROR ID - yline')
        raise Exception('Unknown Error Occured')

# draws a line parallel to x axis.
def vertical(x,lbl='vertical',start=0,end=10,stl='dark_background',color='yellow'):
    '''
    Documentation: https://pypi.org/project/AMD/
    Draws a line parallel to Y-axis.
    Returns Nothing. Plots nothing. Just a placeholder for plotting functions. Should always be used before plotting functions like Graph, compGraph or visualizeSmoothie.

    Parameter_Name    Default_Value    DataType_Needed_To_Be_Passed
         y                -                 integer/float
         lbl           horizontal              string
         start            0                 integer/float
         end              10                integer/float
         stl           dark_background     (string) one of the styles in this link: https://matplotlib.org/3.1.0/gallery/style_sheets/style_sheets_reference.html
         color           yellow                string

    '''
    try:
        style.use(stl)
        plt.plot([x,x],[start,end],label=lbl,linewidth=2,color=color)
    except Exception as e:
        print(str(e)+'\nERROR ID - xline')
        raise Exception('Unknown Error Occured')

# Creates a marker:
def marker(x,y,limit=1,lbl="marker",color='yellow',stl='dark_background'):
    '''
    Documentation: https://pypi.org/project/AMD/
    Used to create a 'plus' shaped plot(small marker) at a given point.
    Returns Nothing. Plots nothing. Just a placeholder for plotting functions. Should always be used before plotting functions like Graph, compGraph or visualizeSmoothie.

    Parameter_Name    Default_Value    DataType_Needed_To_Be_Passed
         x                -                 integer/float
         y                -                 integer/float
       limit              1                 integer/float
        lbl            horizontal              string
        stl         dark_background     (string) one of the styles in this link: https://matplotlib.org/3.1.0/gallery/style_sheets/style_sheets_reference.html
        color           yellow                string


    '''
    style.use(stl)
    vertical(x,lbl=lbl,start=y-limit,end=y+limit,color=color)
    horizontal(y,lbl=lbl,start=x-limit,end=x+limit,color=color)

# Converts two lists into a dictionary
def __liDict(li1,li2):
    try:
        dictionary = dict(zip(li1,li2))
        return(dictionary)
    except Exception as e:
        print(str(e)+'ERROR ID - lidict')
        raise Exception('Unknown Error Occured')

# Assigns a value to a string
def __assignValue(str_list):
    try:
        key=list(set(str_list))
        n=len(list(set(str_list)))//2
        retLi=[]
        if(len(list(set(str_list)))%2==0):
            for i in range(-n+1,n+1):
                retLi.append(i)
            return(__liDict(key,retLi))
        else:
            for i in range(-n,n+1):
                retLi.append(i)
            return(__liDict(key,retLi))
    except Exception as e:
        print(str(e)+'ERROR ID - assignValue')

#finds the difference between two numbers
def __diff(x,y):
    try:
        return(abs(x-y))
    except Exception as e:
        print(str(e)+'ERROR ID - diff')
        raise Exception('Unknown Error Occured')

# Converts all the elements of the list to integers
def __numlist(Index,li):
    try:
        retIndex=[]
        retlist=[]
        for a in range(len(li)):
            retlist.append(float(li[a]))
            retIndex.append(Index[a])
        return(retIndex,retlist)
    except Exception as e:
        print(str(e)+'ERRO ID - numlist')

# Filters based on max deviation allowed
def __maxDev(Index,li,avg,max_deviation):
    try:
        retIn=[]
        retli=[]
        Index,li=__numlist(Index,li)
        for ele in range(len(li)):
            d=__diff(li[ele],avg)
            if(d<=max_deviation):
                retli.append(li[ele])
                retIn.append(Index[ele])
            else:
                pass
        return(retIn,retli)
    except Exception as e:
        print(str(e)+'ERROR ID - maxDev')

# Filters based on max deviation allowed
def __minDev(Index,li,avg,max_deviation):
    try:
        retIn=[]
        retli=[]
        Index,li=__numlist(Index,li)
        for ele in range(len(li)):
            d=__diff(li[ele],avg)
            if(d>max_deviation):
                retli.append(li[ele])
                retIn.append(Index[ele])
            else:
                pass
        return(retIn,retli)
    except Exception as e:
        print(str(e)+'ERROR ID - minDev')

#checks if a parameter is of numtype
def __isnum(var):
    try:
        float(var)
        return(True)
    except:
        return(False)
    pass

#Filters data according to type
def __type_filter(Index,Data,Type):
    try:
        ret_index=[]
        ret_data=[]
        if(Type=='all'):
            return(Index,Data)
        if(Type!='num'):
            for i in range(len(Data)):
                if(type(Data[i])==Type):
                    ret_data.append(Data[i])
                    ret_index.append(Index[i])
            return(ret_index,ret_data)
        else:
            for j in range(len(Data)):
                if(__isnum(Data[j])==True):
                    ret_data.append(float(Data[j]))
                    ret_index.append(Index[j])
            return(ret_index,ret_data)
    except Exception as e:
        print(str(e)+'ERROR ID - type_filter')

#filters a list based on a list of values or a single value
def __value_filter(Index,Data,Expected):
    try:
        if type(Expected) != type([]):
            expected=[]
            expected.append(Expected)
            Expected=expected
        pass
        ret_data=[]
        ret_index=[]
        for i in range(len(Data)):
            if(Data[i] in Expected):
                ret_data.append(Data[i])
                ret_index.append(Index[i])
        return(ret_index,ret_data)
    except Exception as e:
        print(str(e)+'ERROR ID - value_filter')

#Removes all the '' from a code
def __remnull__(li):
    try:
        retli=[]
        for i in range(len(li)):
            if (li[i]!=''):
                retli.append(li[i])
        return(retli)
    except Exception as e:
        print(str(e)+'ERROR ID - remnull')

# Used to set the data within limits
def __limits(Index,Data,s,e):
    try:
        retli=[]
        retIn=[]
        for i in range(len(Data)):
            if (Data[i]<=e) and (Data[i]>=s):
                retli.append(Data[i])
                retIn.append(Index[i])
        return(retIn,retli)
    except Exception as e:
        print(str(e)+'ERROR ID - limits')

# Checks if a HYB
def __isHyb(param):
    if (type(param)==type(()))  and (len(param)==2):
        _1,_2=param
        if(type(_1)==type([])) and (type(_2)==type([])) and (len(_1)==len(_2)):
            return(True)
        else:
            return(False)
    else:
        return(False)

# returns a list with the most dense amount of data
def densePop(hyb):
    '''
    Documentation: https://pypi.org/project/AMD/
    Takes only one arguement - a hybird.
    Returns a hybrid with the most densely populated amplitude-wise approximately linear strip os the data given(hybrid).
    '''
    if __isHyb(hyb)==True :
        index,li=hyb
        st = min(li)
        en = max(li)
        diff = abs(en-st)
        step_length=diff/5
        steps=[st,st+step_length,st+2*step_length,st+3*step_length,st+4*step_length,st+5*step_length]
        a=[]
        a_=[]
        b=[]
        b_=[]
        c=[]
        c_=[]
        d=[]
        d_=[]
        e=[]
        e_=[]
        for _ in range(len(li)):
            z = li[_]
            if z>=st and z<=st+step_length :
                a.append(z)
                a_.append(index[_])
            elif z>st+step_length and z<=st+step_length*2 :
                b.append(z)
                b_.append(index[_])
            elif z>st+step_length*2 and z<=st+step_length*3 :
                c.append(z)
                c_.append(index[_])
            elif z>st+step_length*3 and z<=st+step_length*4 :
                d.append(z)
                d_.append(index[_])
            elif z>st+step_length*4 and z<=st+step_length*5 :
                e.append(z)
                e_.append(index[_])
        allInd=[a_,b_,c_,d_,e_]
        allLi=[a,b,c,d,e]
        n = [len(a),len(b),len(c),len(d),len(e)]
        __Ind = n.index(max(n))
        bestRange=allLi[__Ind]
        bestRange_ind=allInd[__Ind]
        return(bestRange_ind,bestRange)
    else:
        return(densePop(hybridize(hyb)))

# retruns the region with the most scarce amount of data
def scarcePop(hyb):
    '''
    Documentation: https://pypi.org/project/AMD/
    Takes only one arguement - a hybird.
    Returns a hybrid with the least densely populated amplitude-wise approximately linear strip os the data given(hybrid).
    '''
    if __isHyb(hyb)==False :
        return(scarcePop(hybridize(hyb)))
    else:
        pass
    index,li=hyb
    st = min(li)
    en = max(li)
    diff = abs(en-st)
    step_length=diff/5
    steps=[st,st+step_length,st+2*step_length,st+3*step_length,st+4*step_length,st+5*step_length]
    a=[]
    a_=[]
    b=[]
    b_=[]
    c=[]
    c_=[]
    d=[]
    d_=[]
    e=[]
    e_=[]
    for _ in range(len(li)):
        z = li[_]
        if z>=st and z<=st+step_length :
            a.append(z)
            a_.append(index[_])
        elif z>st+step_length and z<=st+step_length*2 :
            b.append(z)
            b_.append(index[_])
        elif z>st+step_length*2 and z<=st+step_length*3 :
            c.append(z)
            c_.append(index[_])
        elif z>st+step_length*3 and z<=st+step_length*4 :
            d.append(z)
            d_.append(index[_])
        elif z>st+step_length*4 and z<=st+step_length*5 :
            e.append(z)
            e_.append(index[_])
    allInd=[a_,b_,c_,d_,e_]
    allLi=[a,b,c,d,e]
    n = [len(a),len(b),len(c),len(d),len(e)]
    __Ind = n.index(min(n))
    bestRange=allLi[__Ind]
    bestRange_ind=allInd[__Ind]
    return(bestRange_ind,bestRange)

# removes all impulses
def remImp(arg):
    '''
    Documentation: https://pypi.org/project/AMD/
    Takes only one arguement - a hybird.
    Removes impulses in a data and returns a hybrid
    '''
    if __isHyb(arg) == True:
        return(densePop(arg))
    else:
        return(remImp(hybridize(arg)))

# detects impulses
def detectImp(arg):
    '''
    Documentation: https://pypi.org/project/AMD/
    Takes only one arguement - a hybird.
    Detects all impulses in the given data and returns a hybrid.
    '''
    if __isHyb(arg)==False :
        return(detectImp(hybridize(arg)))
    else:
        pass
    Eindex,Evalue = remImp(arg)
    index,value = arg
    retind=[]
    retval=[]
    for i in range(len(index)):
        if index[i] not in Eindex:
            retind.append(index[i])
            retval.append(value[i])
    return(retind,retval)

# cleans impulses in data
def cleanImpulses(hyb,levels=None):
    '''
    Documentation: https://pypi.org/project/AMD/
    Removes impulses 'levels' number of times and returns a hybrid.
    If levels parameter is not passed, impulses are removed until only one point or a straight line remains.
    cleanImpulses(hyb,levels=None) is the function header.
    '''
    if __isHyb(hyb)==False :
        return(cleanImpulses(hybridize(hyb),levels))
    else:
        pass
    if levels==None:
        _,imp=detectImp(hyb)
        step=0
        while(len(imp)!=0):
            step+=1
            hyb=remImp(hyb)
            _,imp=detectImp(hyb)
        return(hyb)
    else:
        for someVar in range(levels):
            hyb=remImp(hyb)
        return(hyb)

# Filters data recieved from arduino
def filter(hybrid=None,index=[],data=[],expected=[],expectedType=None,maxDeviation=None,minDeviation=None,closeTo=None,farFrom=None,numeric=True,limit=[],frequentAverage=False,below=None,above=None):

    # Initialization
    if expectedType!=None:
        numeric=False
    if hybrid!=None:
        index,data=hybrid
    if index!=[] and data==[]:
        data=index.copy()
        index=[]
    data=list(data)
    if index==[]:
        index=[q for q in range(len(data))]
    elif index!=[] and (len(index)!=len(data)):
        print(f"index[] has {len(index)} elements while data[] has {len(data)} elements.\nMake sure both have equal number of elements !")
        raise AssertionError
    elif index!=[] and (len(index)==len(data)):
        pass

    if above!=None:
        ndata=[]
        nInd=[]
        for someVar in range(len(data)):
            if(data[someVar]>above):
                ndata.append(data[someVar])
                nInd.append(index[someVar])
        data=ndata
        index=nInd

    if below!=None:
        ndata=[]
        nInd=[]
        for someVar in range(len(data)):
            if(data[someVar]<below):
                ndata.append(data[someVar])
                nInd.append(index[someVar])
        data=ndata
        index=nInd


    if farFrom==None and closeTo!=None and maxDeviation !=None and minDeviation!= None:
        farFrom = closeTo
    if farFrom!=None and closeTo==None and maxDeviation !=None and minDeviation!= None:
        closeTo=farFrom

    # If data is numeric
    if(numeric==True):
        new_data=[]
        new_index=[]
        for i in range(len(data)):
            try:
                new_data.append(float(data[i]))
                new_index.append(float(index[i]))
            except:
                pass
        data=new_data.copy()
        index=new_index.copy()
        if (limit!=[]):
            index,data=__limits(index,data,limit[0],limit[1])
    pass


    if closeTo!=None and closeTo!='avg':
        average=closeTo
    elif __isunique(data)==False and frequentAverage==True:
        average=most_frequent(data)
        print(f'Average is most_frequent data = {average}')
    elif((numeric==True) and frequentAverage==False) or (closeTo=='avg' and frequentAverage==False) or (farFrom=='avg' and frequentAverage==False):
        try:
            average=sum(data)/len(data)
            print(f'Average is calculated as {average}')
        except Exception as e:
            if str(e) == 'ZeroDivisionError: division by zero':
                pass
                average='None'
            else:
                raise Exception(e)
    else:
        if (numeric==True) and expected==[] and expectedType==None and closeTo == None and farFrom == None:
            print("""
            Not enough information to filter !!
            Pass either limit , closeTo , expected , farFrom , minDeviation or maxDeviation""")
            raise BaseException
    print(average)
    # Average obtained
    if expected!=[] :
        index,data=__value_filter(index,data,expected)
    pass
    if expectedType!=None :
        index,data=__type_filter(index,data,expectedType)
    pass
    if maxDeviation!=None and (__isnum(closeTo)):
        index,data=maxDev(index,data,average,maxDeviation)
    elif maxDeviation!=None and (closeTo=='avg'):
        index,data= __maxDev(index,data,average,maxDeviation)
    pass
    if minDeviation!=None and (__isnum(farFrom)):
        index,data=__minDev(index,data,farFrom,minDeviation)
    elif minDeviation!=None and (farFrom=="avg"):
        index,data = __minDev(index,data,average,minDeviation)
    pass
    if maxDeviation==None and closeTo!=None :
        index,data=__maxDev(index,data,average,1)
    pass
    if minDeviation==None and farFrom!=None :
        index,data = __minDev(index,data,farFrom,1)
    return(index,data)

#Most frequent piece of data
def most_frequent(List):
    '''
    Documentation: https://pypi.org/project/AMD/
    Takes only one arguement - a list.
    Returns a single element - string / integer / float
    Returns an element which is the most least repeated.
    '''
    try:
        return (max(set(List), key = List.count))
    except Exception as e:
        print(str(e)+'ERROR ID - most_frequent')

#Least frequent piece of data
def least_frequent(List):
    '''
    Documentation: https://pypi.org/project/AMD/
    Takes only one arguement - a list.
    Returns a single element - string / integer / float
    Returns an element which is the most least repeated
    '''
    try:
        return (min(set(List), key = List.count))
    except Exception as e:
        print(str(e)+'ERROR ID - least_frequent')

#Compresses data
def compress(li):
    '''
    Documentation: https://pypi.org/project/AMD/
    Takes only one arguement.
    Returns a list if list is passed and returns a hybrid if hybrid is passed.
    compress replaces continuous equivalent elements by a single element.
    '''
    try:
        if (type(li)!=type([])):
            I,D=li
            return(__cpress(I,D))
        else:
            return([i for i,j in zip_longest(li,li[1:]) if i!=j])
    except Exception as e:
        print(str(e)+'ERROR ID - compress')

#Escapes from the escape Characters
def __escape(string):
    try:
        li=__elements(string)
        remli=['\b','\n','\r','\t']
        retli=[]
        for i in range(len(string)):
            if((string[i] in remli)==False):
                retli.append(string[i])
        return("".join(retli))
    except Exception as e:
        print(str(e)+'ERROR ID - escape')

def instAvg(hyb):
    '''
    Documentation: https://pypi.org/project/AMD/
    Takes only one arguement - a hybrid.
    Returns a hybrid.
    '''
    if __isHyb(hyb)==False :
        return(instAvg(hybridize(hyb)))
    else:
        pass
    X,Y=hyb
    retx,rety=[],[]
    for i in range(len(X)-1):
        x1,y1,x2,y2=X[i],Y[i],X[i+1],Y[i+1]
        xDiff = abs(x1-x2)
        retx.append(min([x1,x2])+xDiff)
        rety.append((y1+y2)/2)
    return(retx,rety)

def smoothie(hyb,levels=None):
    '''
    Documentation: https://pypi.org/project/AMD/
    executes instAvg() on the given data 'levels' number of times and returns a hybrid.
    If levels parameter is not passed, instAvg function is executed till only a point remains.
    smoothie(hyb,levels=None) is the function header.
    '''
    if __isHyb(hyb)==False :
        return(smoothie(hybridize(hyb),levels))
    else:
        pass
    if levels==None:
        x,y=hyb
        return(smoothie(hyb,len(y)-1))
    else:
        for i in range(levels):
            hyb=instAvg(hyb)
        return(hyb)

def reduce(hyb):
    '''
    Documentation: https://pypi.org/project/AMD/
    Takes a hybrid as arguement and returns a Hybrid.
    '''
    if __isHyb(hyb)==False :
        return(scarcePop(hybridize(hyb)))
    else:
        pass
    X,Y=hyb
    retx=X[2:]
    rety=Y[2:]
    x1,x2,y1,y2=X[0],X[1],Y[0],Y[1]
    xdiff=abs(x1-x2)
    x=min([x1,x2])+xdiff
    y=(y1+y2)/2
    retx.insert(0,x)
    rety.insert(0,y)
    return(retx,rety)

##############################################################################################################################################
##############################################################################################################################################
'                                                 Data Visualization FUNCTIONS:                                                              '
##############################################################################################################################################
##############################################################################################################################################

#Graphs the data
def Graph(hybrid=None,x=[],y=[],xlabel='dataPiece',ylabel='Amplitude',label='myData',color='red',title='Graph',markersize=7,stl='dark_background',d={},mark='x',equiAxis=False):
    '''
    Documentation: https://pypi.org/project/AMD/
    Plots a Graph
    Learn about equiAxis through this link:-https://github.com/SayadPervez/Arduino_Master_Delta/blob/master/equiaxis.md
    '''
    try:
        style.use(stl)
        if hybrid != None:
            if __isHyb(hybrid)==True:
                x,y=hybrid
            else:
                y=hybrid
                hybrid=None
        if d!={} and y==[] and x==[] :
            replacementX=[]
            replacementY=[]
            for ele in d:
                replacementX.append(ele)
                replacementY.append(d[ele])
            x=replacementX
            y=replacementY
        else:
            if x!=[] and y==[]:
                y=x.copy()
                x=[i for i in range(len(y))]
            elif x==[]:
                x=[i for i in range(len(y))]
            else:
                pass
        plt.plot(x,y,label=label,color=color, marker=mark,markersize=markersize)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        if (equiAxis==True):
            plt.axis('square')
            axes = plt.gca()
            axes.set_xlim([min(x)-1,max(x)+1])
            axes.set_ylim([min(y)-1,max(y)+1])
        plt.title(title+f'\nequiAxis={equiAxis}')
        plt.legend()
        plt.show()
    except Exception as e:
        print(str(e)+'ERROR ID - Graph')

# Used to compare two graphs
def compGraph(hybrid1=None,hybrid2=None,x1=[],y1=[],x2=[],y2=[],xlabel='dataPiece',ylabel='Amplitude',label1='myData-1',label2='myData-2',color1='red',color2='blue',title='Graph',markersize=7,stl='dark_background',fit=True,d1={},d2={},equiAxis=False):
    '''
    Documentation: https://pypi.org/project/AMD/
    Compares two plots via Graph.
    Learn about equiAxis through this link:-https://github.com/SayadPervez/Arduino_Master_Delta/blob/master/equiaxis.md
    '''
    try:
        if hybrid1 != None:
            if __isHyb(hybrid1)==True:
                x1,y1=hybrid1
            else:
                y1=hybrid1
                hybrid1=None
        if hybrid2 != None:
            if __isHyb(hybrid2)==True:
                x2,y2=hybrid2
            else:
                y2=hybrid2
                hybrid2=None
        style.use(stl)
        if (d1!={} or d2!={})or (x1!=[] or x2!=[]):
            fit=False
        if d1!={}:
            replacementX=[]
            replacementY=[]
            for ele1 in d1:
                replacementX.append(ele1)
                replacementY.append(d1[ele1])
            x1=replacementX
            y1=replacementY
        if d2!={}:
            replacementX=[]
            replacementY=[]
            for ele in d2:
                replacementX.append(ele)
                replacementY.append(d2[ele])
            x2=replacementX
            y2=replacementY
        if fit == True:
            def Map(a_value,frm,to):
                percent=(a_value/frm) * 100
                ret_value=(percent*to)/100
                return(ret_value)
            if x1 == []:
                x1=[i for i in range(len(y1))]
            if x2 == []:
                x2=[j for j in range(len(y2))]
            if(len(x1)>=len(x2)):
                nli=[]
                for p in range(len(x2)):
                    x2[p]=Map(x2[p],len(x2),len(x1))
            else:
                nli=[]
                for p in range(len(x1)):
                    x1[p]=Map(x1[p],len(x1),len(x2))
            plt.plot(x1,y1,label=label1,color=color1, marker="o",markersize=markersize,linewidth=2)
            plt.plot(x2,y2,label=label2,color=color2, marker="x",markersize=markersize,linewidth=2)
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            if (equiAxis==True):
                plt.axis('square')
                axes = plt.gca()
                axes.set_xlim([min(x1+x2)-1,max(x1+x2)+1])
                axes.set_ylim([min(y1+y2)-1,max(y1+y2)+1])
            plt.title(f"{title}\nWith Fit Enabled   equiAxis={equiAxis}")
            plt.legend()
            plt.show()
        else:
            if x1 == [] :
                x1=[i for i in range(len(y1))]
            if x2 == [] :
                x2=[j for j in range(len(y2))]
            plt.plot(x1,y1,label=label1,color=color1, marker="o",markersize=markersize)
            plt.plot(x2,y2,label=label2,color=color2, marker="x",markersize=markersize)
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            if (equiAxis==True):
                plt.axis('square')
                axes = plt.gca()
                axes.set_xlim([min(x1+x2)-1,max(x1+x2)+1])
                axes.set_ylim([min(y1+y2)-1,max(y1+y2)+1])
            plt.title(f"{title}\nWith Fit Disabled   equiAxis={equiAxis}")
            plt.legend()
            plt.show()
    except Exception as e:
        print(str(e)+'ERROR ID - compGraph')

def visualizeSmoothie(hyb,equiAxis=False):
    '''
    Documentation: https://pypi.org/project/AMD/
    Plots a Graph which will show what each level of smoothie would return if a hybrid is passed to it.
    Takes a hybrid as a parameter.
    Learn about equiAxis through this link:-https://github.com/SayadPervez/Arduino_Master_Delta/blob/master/equiaxis.md
    '''
    if __isHyb(hyb)==False :
        visualizeSmoothie(hybridize(hyb))
        return
    else:
        pass
    allx,ally=[],[]
    style.use('default')
    X,Y=hyb
    for i in range(len(Y)):
        sm = smoothie(hyb,i)
        x,y=sm
        for _ in range(len(y)):
            allx.append(x[_])
            ally.append(y[_])
        plt.plot(x,y,label=i)
    if (equiAxis==True):
        plt.axis('square')
        axes = plt.gca()
        axes.set_xlim([min(allx)-1,max(allx)+1])
        axes.set_ylim([min(ally)-1,max(ally)+1])
    plt.title("Visualize Smoothie"+f'\nequiAxis={equiAxis}')
    plt.show()

##############################################################################################################################################
##############################################################################################################################################
'                                                  ARDUINO FUNCTIONS:                                                                        '
##############################################################################################################################################
##############################################################################################################################################

# What this function does is it gets certain lines of data from a com port and removes the repeated values and also the escape sequence characters !!!
def ardata(COM,lines=50,baudrate=9600,timeout=1,squeeze=True,dynamic=False,msg='a',dynamicDelay=0.5,numeric=True):
    '''
    Documentation: https://pypi.org/project/AMD/
    '''
    try:
        i=0
        all=list()
        if(type(COM)==type(1)):
            ser=serial.Serial('COM{}'.format(COM),baudrate = baudrate, timeout=timeout)
        else:
            ser=serial.Serial('{}'.format(COM),baudrate = baudrate, timeout=timeout)
        while(i<=lines):
            if(dynamic==True):
                ser.write(bytearray(msg,'utf-8'))
                time.sleep(dynamicDelay)
            all.append(__escape(ser.readline().decode('ascii')))
            time.sleep(0.1)
            i+=1
        all=__remnull__(all)
        All=[]
        if numeric==True:
            for k in range(len(all)):
                try:
                    All.append(float(all[k]))
                except:
                    pass
        else:
            All=all
        if(squeeze==False):
            return(All)
        else:
            return(compress(All))
        pass

    except Exception as e:
        print(str(e)+'ERROR ID - ardata')

#reads only one line of data from a comport:
def readSerial(COM,baudrate=9600,timeout=1):
    '''
    Documentation: https://pypi.org/project/AMD/
    '''
    try:
        data=ardata(COM,2,baudrate,timeout,numeric=False)
        return(data[0])
    except Exception as e:
        print(str(e)+'\nERROR ID - readSerial')

# writes only one line to a com port !
def writeSerial(COM,baudrate=9600,timeout=1,msg=""):
    '''
    Documentation: https://pypi.org/project/AMD/
    '''
    try:
        ardata(COM,2,baudrate,timeout,dynamic=True,msg=msg)
    except Exception as e:
        print(str(e)+'\nERROR ID - writeSerial')

# to get a single dynamic communication between arduino and python !
def dynamicSerial(COM,baudrate=9600,timeout=1,msg="a",dynamicDelay=0.5):
    '''
    Documentation: https://pypi.org/project/AMD/
    '''
    try:
        return(ardata(COM,2,baudrate,timeout,squeeze=False,dynamic=True,msg=msg,dynamicDelay=dynamicDelay))
    except Exception as e:
        print(str(e)+"\nERROR ID - dynamicSerial")

##############################################################################################################################################
##############################################################################################################################################
'                                                  Data Storage and retrival FUNCTIONS:                                                                        '
##############################################################################################################################################
##############################################################################################################################################

#input type gives the type of input as either numeric or alphabetic>>
def __input_type(given):
    try:
        Modified_Input=float(given)
    except Exception:
        return("$#Alpha_type#$")
    return("$#Numeric_type#$")
#******************************************************************************************************************************************************
#elements appends each letter of the given string to a list and returns it back
def __elements(g_string):
    if(__input_type(g_string)=="$#Alpha_type#$"):
        gstring=g_string
    else:
        gstring=str(g_string)
    ng=len(gstring)-1
    lg=list()
    ig=0
    while(ig<=ng):
        lg.append(gstring[ig])
        ig+=1
    return(lg)
#******************************************************************************************************************************************************
# used to create a new text file.
def __creatext(filename):
    F=open(filename,'w+')
    F.close()
#******************************************************************************************************************************************************
# return the number of lines in a given text file
def __lenline(F_Name):
    num_lines = 0
    with open(F_Name, 'r') as nf:
        for line in nf:
            num_lines += 1
    return(num_lines)
#******************************************************************************************************************************************************
# reads a specific line from a given text file.
def __readLine(file_name,Line_num):
    with open(file_name,'r') as f:
        red=f.readlines()[Line_num]
    return(red)
#******************************************************************************************************************************************************
#       Used to return an exact inverse of a given set of symbols like ( , ) , < , > , [ , ]     |||||||||
def __invert(inp):
    n=len(inp)
    Inp=__elements(inp)
    o=0
    while(o<n):
        check=Inp[o]
        if(Inp[o]=="<"):
            Inp[o]=">"
        elif(Inp[o]=="("):
            Inp[o]=")"
        elif(Inp[o]=="["):
            Inp[o]="]"
        elif(Inp[o]==">"):
            Inp[o]="<"
        elif(Inp[o]==")"):
            Inp[o]="("
        elif(Inp[o]=="]"):
            Inp[o]="["
        else:
            pass
        o+=1
    return(''.join(Inp))
#******************************************************************************************************************************************************
#Used to reverse a string.................... pervez >> zevrep
def __reverse(str):
    strin=__elements(str)
    string=__invert(strin)
    n=len(string)
    revs="0"*n
    reversed=__elements(revs)
    j=n-1
    i=0
    while(i<n):
        reversed[i]=string[j]
        i+=1
        j-=1
    return(''.join(reversed))
#******************************************************************************************************************************************************
# used to get a piece of string from a given text file with a set of symbols called as indicators>>>>>>>
def __ext(file,identifier="",type=""):
    try:
        all_lines=list()
        n=__lenline(file)
        line_num=0
        while(line_num<n):
            with open(file,'r') as f:
                if(type==""):
                    try:
                        red=f.readlines()[line_num]
                        all_lines.append(str(red))
                    except Exception:
                        pass
                elif(type=="d"):
                    try:
                        red=f.readlines()[line_num]
                        all_lines.append(decode(str(red)))
                    except Exception:
                        pass
            line_num+=1
        if(identifier==""):
            return(all_lines)
        else:
            pass
        j=0
        E_=list()
        while(j<n):
            try:
                line=all_lines[j]
                st_e=line.index(identifier)
                end_e=line.index(__reverse(identifier))
                e_=line[st_e+len(identifier):end_e]
                E_.append(e_)
                j+=1
            except Exception as e:
                if (str(e)=="substring not found"):
                    pass
                    j+=1
                else:
                    print(str(e))
        return(E_)
    except Exception as e:
        if (str(e)=="substring not found"):
            pass
        else:
            print(str(e))
#******************************************************************************************************************************************************
# Assuming x to be enclosed within >> and  << between )) and ((
def extract(name,path=None):
    '''
    Documentation: https://pypi.org/project/AMD/
    Function Category : AMD custom Data_Base
    Used to extract x and y values from an AMD custom Data_Base.
    Returns an hybrid.
    The function header is as follows: extract(name,path=None)
    name takes either the absolute path of the text file if located in another directory or
                      the name of the text file if located in the same directory as the program.
    path is an optional parameter which is to be specified the directory in which the AMD custom Data_Base is located.
    '''
    if '.txt' in name:
        name=name[:name.index('.txt')]
    if path==None:
        path=__cwd()+'\\'+str(name)+'.txt'
        name=path
    else:
        name=path+'\\'+str(name)+'.txt'
    xVal=__ext(name,'>>')
    yVal=__ext(name,'))')
    if len(xVal)<=0:
        raise Exception('No X values found in the destination file. The file may be Corrupt or Empty !!')
    if len(yVal)<=0:
        raise Exception('No Y values found in the destination file. The file may be Corrupt or Empty !!')
    newX,newY=[],[]
    xBool=0
    yBool=0
    for _ in range(len(xVal)):
        try:
            newX.append(float(xVal[_]))
        except Exception:
            xBool+=1
    for _ in range(len(yVal)):
        try:
            newY.append(float(yVal[_]))
        except Exception:
            yBool+=1
    if xBool==0:
        xVal=newX
    else:
        pass
    if yBool==0:
        yVal=newY
    else:
        pass
    if(len(xVal)!=len(yVal)):
        raise Exception("\n Corrupt File !! \n Check the file contents properly !")
    return(xVal,yVal)
#******************************************************************************************************************************************************
# Returns current working directory
def __cwd():
    import os
    workingDir=os.getcwd()
    return(workingDir)
#******************************************************************************************************************************************************
# AMD way of writing to text files.
def __writeHybrid(hybrid,fileName):
    import os
    x,y=hybrid
    with open(fileName,'a') as f:
        for _ in range(len(x)):
            f.write(f'>>{x[_]}<<\t)){y[_]}((\n')
        f.write('_')
#******************************************************************************************************************************************************
# Deletes everything in a given text file
def __delAll(name,path):
    if '.txt' in name:
        name=name[:name.index('.txt')]
    import os
    if path!='default':
        os.chdir(path)
    sname=name + '.txt'
    fileName=os.getcwd()+'\\'+str(sname)
    with open(fileName,'w') as f:
        f.write('')
#******************************************************************************************************************************************************
# actual extract funtion to be used
def save(hybrid,name='default',path='default'):
    '''
    Documentation: https://pypi.org/project/AMD/
    Function Category : AMD custom Data_Base
    Used to save x and y values of a custom hybrid in a custom textfile called as AMD Custom Data_Base
    The function header is as follows: save(hybrid,name='default',path='default')
    name takes either the absolute path of the text file if located in another directory or
                      the name of the text file if located in the same directory as the program.
        If name is not provided, a AMD custom Data_Base is automatically created in the folder in which the operating program is located in.
    path is an optional parameter which is to be specified the directory in which the AMD custom Data_Base is located.
    '''
    if '.txt' in name:
        name=name[:name.index('.txt')]
    if __isHyb(hybrid)==False:
        raise Exception('Parameter passed is not of hybrid type !')
    import os
    if path!='default':
        os.chdir(path)
    if name=='default':
        cwd=__cwd()
        allDirs=os.listdir()
        textFiles=[]
        AMDirs=[]
        for _ in range(len(allDirs)):
            if '.txt' in allDirs[_]:
                textFiles.append(allDirs[_])
        for __ in range(len(textFiles)):
            if 'AMD_' in textFiles[__]:
                AMDirs.append(textFiles[__])
        # Till now AMDirs have all the list of AMD text files.
        AMDIndices=[]
        for ___ in range(len(AMDirs)):
            AMDIndices.append(int((AMDirs[___])[AMDirs[___].index('AMD_')+4:AMDirs[___].index('.txt')]))
        if AMDIndices!=[]:
            precidingNumb=max(AMDIndices)+1
        else:
            precidingNumb=0
        name='AMD_'+str(precidingNumb)
    sname=name + '.txt'
    allDirs=os.listdir()
    textFiles=[]
    for _ in range(len(allDirs)):
        if '.txt' in allDirs[_]:
            textFiles.append(allDirs[_])
    if sname in textFiles:
        save(hybrid,'AMD_Cache',path)
        raise Exception('A text file with the name you specified already exists.\nPlease use appendSave function to add the data to a pre-existing file.\nPlease use rewriteSave to delete the contents in the specified file and write to it again !\nCurrently your data has been saved in the AMD_Cache.txt file of your specified directory.\n You can copy paste the contents manually too !')
    __creatext(sname)
    # Till now a text file has been created for use. Now writing to it remains !!
    fileName=os.getcwd()+'\\'+str(sname)
    __writeHybrid(hybrid,fileName)
#******************************************************************************************************************************************************
# add data to a pre existing file
def appendSave(hybrid,name,path='default'):
    '''
    Documentation: https://pypi.org/project/AMD/
    Function Category : AMD custom Data_Base
    Used to save x and y values of a custom hybrid in a custom textfile called as AMD Custom Data_Base
    The save is added to a pre-existing file.
    The function header is as follows: appendSave(hybrid,name,path='default')
    name takes either the absolute path of the text file if located in another directory or
                      the name of the text file if located in the same directory as the program.
    path is an optional parameter which is to be specified the directory in which the AMD custom Data_Base is located.
    '''
    if '.txt' in name:
        name=name[:name.index('.txt')]
    if __isHyb(hybrid)==False:
        raise Exception('Parameter passed is not of hybrid type !')
    import os
    if path!='default':
        os.chdir(path)
    sname=name + '.txt'
    fileName=os.getcwd()+'\\'+str(sname)
    __writeHybrid(hybrid,fileName)
#******************************************************************************************************************************************************
# replace data to a pre existing file
def rewriteSave(hybrid,name,path='default'):
    '''
    Documentation: https://pypi.org/project/AMD/
    Function Category : AMD custom Data_Base
    Used to save x and y values of a custom hybrid in a custom textfile called as AMD Custom Data_Base
    This function deletes all the contents in the existing file and rewrites it from the start.
    The function header is as follows: rewriteSave(hybrid,name,path='default')
    name takes either the absolute path of the text file if located in another directory or
                      the name of the text file if located in the same directory as the program.
    path is an optional parameter which is to be specified the directory in which the AMD custom Data_Base is located.
    '''
    if '.txt' in name:
        name=name[:name.index('.txt')]
    if __isHyb(hybrid)==False:
        raise Exception('Parameter passed is not of hybrid type !')
    import os
    if path!='default':
        os.chdir(path)
    sname=name + '.txt'
    fileName=os.getcwd()+'\\'+str(sname)
    __delAll(name,path)
    __writeHybrid(hybrid,fileName)
#******************************************************************************************************************************************************
# extract X values of a AMD specific file
def extractX(name,path=None):
    '''
    Documentation: https://pypi.org/project/AMD/
    Function Category : AMD custom Data_Base
    Used to extractX x values from an AMD custom Data_Base.
    Returns a list of X values.
    The function header is as follows: extract(name,path=None)
    name takes either the absolute path of the text file if located in another directory or
                      the name of the text file if located in the same directory as the program.
    path is an optional parameter which is to be specified the directory in which the AMD custom Data_Base is located.
    '''
    if '.txt' in name:
        name=name[:name.index('.txt')]
    if path==None:
        path=__cwd()+'\\'+str(name)+'.txt'
        name=path
    else:
        name=path+'\\'+str(name)+'.txt'
    xVal=__ext(name,'>>')
    if len(xVal)<=0:
        raise Exception('No X values found in the destination file. The file may be Corrupt or Empty !!')
    newX=[]
    xBool=0
    for _ in range(len(xVal)):
        try:
            newX.append(float(xVal[_]))
        except Exception:
            xBool+=1
    if xBool==0:
        xVal=newX
    else:
        pass
    return(xVal)
#******************************************************************************************************************************************************
# extract Y values of a AMD specific file
def extractY(name,path=None):
    '''
    Documentation: https://pypi.org/project/AMD/
    Function Category : AMD custom Data_Base
    Used to extractY y values from an AMD custom Data_Base.
    Returns a list of Y values.
    The function header is as follows: extract(name,path=None)
    name takes either the absolute path of the text file if located in another directory or
                      the name of the text file if located in the same directory as the program.
    path is an optional parameter which is to be specified the directory in which the AMD custom Data_Base is located.
    '''
    if '.txt' in name:
        name=name[:name.index('.txt')]
    if path==None:
        path=__cwd()+'\\'+str(name)+'.txt'
        name=path
    else:
        name=path+'\\'+str(name)+'.txt'
    yVal=__ext(name,'))')
    if len(yVal)<=0:
        raise Exception('No Y values found in the destination file. The file may be Corrupt or Empty !!')
    newY=[]
    yBool=0
    for _ in range(len(yVal)):
        try:
            newY.append(float(yVal[_]))
        except Exception:
            yBool+=1
    if yBool==0:
        yVal=newY
    else:
        pass
    return(yVal)
#******************************************************************************************************************************************************
