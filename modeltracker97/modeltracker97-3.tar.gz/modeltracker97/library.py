import pandas as pd
import uuid
import sqlite3
import os
from sklearn.model_selection import train_test_split 
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn import model_selection
import numpy as np
from sklearn.metrics import balanced_accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
from sklearn.metrics import auc
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.linear_model import Ridge 
from sklearn.linear_model import Lasso
from scipy.spatial.distance import cdist
from sklearn.mixture import GaussianMixture 
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_mutual_info_score
from sklearn.metrics import adjusted_rand_score
from sklearn.cluster import DBSCAN
from sqlalchemy import create_engine
from urllib import parse
import time
from sklearn.linear_model import SGDClassifier
import traceback
parameters={}
PK={}

#saves da
def data(name):
    PK={}
    Data_Table = pd.DataFrame(columns=['Data_Name','Data_ID'])
    if not os.path.isfile('Data_Table.csv'):
        Data_Table.to_csv('Data_Table.csv',header='column_names',index=False)    
    else:
        Data_Table=pd.read_csv('Data_Table.csv')
    #aaa2=(Data_Table.Data_Name=='name').all()  #name
    A=Data_Table[Data_Table['Data_Name'].astype(str).str[:].str.contains(name)]
    b=A.empty
    ID=A['Data_ID']     

    if b==True:
        PK={}
        PK[name] = uuid.uuid4()
        PK2=pd.DataFrame.from_dict(PK, orient='index')
      
        PK2 = PK2.reset_index()
        Data_Table2=PK2
        Data_Table2.columns = ['Data_Name', 'Data_ID']
        Data_Table2['Data_Name'] = Data_Table2['Data_Name'].astype(str)
        Data_Table2['Data_ID'] = Data_Table2['Data_ID'].astype(str)
       # column_names=["Data_Name","Data_ID"
        if not os.path.isfile('Data_Table.csv'):
            Data_Table2.to_csv('Data_Table.csv',header='column_names',index=False)
        else:
            Data_Table2.to_csv('Data_Table.csv',mode='a',header=False, index=False)
        ID=Data_Table2['Data_ID']
    else:
        ID=A['Data_ID'] 

    return ID






def func(lr):
    #parameters[x]=x.get_params() 
    #PK={}
    #global Model_ID
    parameters={}
    PK={}
    #PK3={}
    #PK[lr]=time.time()
    import datetime 
    now = datetime.datetime.now()
  
    idz=now.strftime('%Y-%m-%dT%H:%M:%S') + ('-%02d' % (now.microsecond / 10000))
    PK[lr] = uuid.uuid4()
    PK2=pd.DataFrame.from_dict(PK, orient='index')
  
    PK2 = PK2.reset_index()
    Model_ID=PK2
    Model_ID.columns = ['Model_Detail', 'Model_ID']
    Model_ID['Model_Detail'] = Model_ID['Model_Detail'].astype(str)
    Model_ID['Model_ID'] = Model_ID['Model_ID'].astype(str)
    Model_ID['Time_Stamp']=idz
    sep='('
    x=Model_ID['Model_Detail'][0]
    x1=x.split(sep,1)[0]
    Model_ID['Model_Name']=x1
    #Model_ID['Model_SF']= Model_ID['x']
    
    
   
    return Model_ID

k={}
def func1(x,d):
    #ID=d.loc[0,'Model_ID']
    try:
        ID=d
        #name=x
        print (x)
        print(ID)
        parameters={}
        k={}
        global Parameters3
        parameters[x]=x.get_params() 
        Parameters2=pd.DataFrame.from_dict(parameters, orient='index')
        
        Parameters3 = Parameters2.reset_index()
        Parameters3=Parameters3.melt(id_vars=["index"], 
            var_name=["Param_Name"], 
            value_name="Value")
        Parameters3.columns = ['Model_Name','Param_Name','Value']
        print (Parameters3)
        Parameters3['Model_Name'] = Parameters3['Model_Name'].astype(str)
        Parameters3['Value'] = Parameters3['Value'].astype(str)
        
        Parameters3 = Parameters3[Parameters3.Value != "nan"]
        Parameters3['Model_ID']=ID
        
        #Parameters3.loc[Parameters3.Model_Name==name, 'Model_ID']=ID
        #Parameters4['Model_ID']= np.where(Parameters3['Model_Name']== name, ID,'NA')
        #Parameters3['Model_ID']= np.where(Parameters3['Model_ID']== 'NA', ID,'NA')
        
        #Parameters3.loc[:,"Model_ID"] = ID
        l=Parameters3['Param_Name']
        l=l.tolist()
       # l=[1,2,3,4]
        k={}
        for i in l:
            k[i]=uuid.uuid4()
            #Parameters3.loc[:,"TuningID"]= k[i]
        PK2=pd.DataFrame.from_dict(k, orient='index')
        PK2 = PK2.reset_index()
        PK2.columns = ['Model_Name', 'Tuning_ID']
        PK2=PK2.drop(['Model_Name'],axis=1)
        #Tuning_ID=PK2
        Parameters3['Tuning_ID']=PK2['Tuning_ID']
        Parameters3=Parameters3.drop(['Model_Name'],axis=1)
    except:
        var = traceback.format_exc()   
        with open("error.txt", "a") as myfile:
            myfile.write(var)        
        
    return Parameters3

def func3(x,X_train,y_train,y):
    #ID=y.loc[0,'Model_ID']
    try:
        global Goodness_of_fit
        global var
        ID=y
        scoring = 'r2'
        scoring2 = 'neg_mean_squared_error'
        scoring3 = 'explained_variance'
        #scoring4 = 'balanced_accuracy'
        scoring5 = 'neg_mean_absolute_error'
        seed = 7
        kfold = model_selection.KFold(n_splits=2, random_state=seed)
        r2={}
        MSE={}
        EV={}
        ME={}
        MAE={}
        results={}
        results2={}
        results = model_selection.cross_val_score(x, X_train, y_train,cv=kfold,  scoring=scoring)
        results2 = model_selection.cross_val_score(x, X_train, y_train, cv=kfold,  scoring=scoring2)
        results3 = model_selection.cross_val_score(x, X_train, y_train, cv=kfold,  scoring=scoring3)
     #   results4 = model_selection.cross_val_score(x, X_train, y_train, cv=kfold,  scoring=scoring4)
        results5 = model_selection.cross_val_score(x, X_train, y_train, cv=kfold,  scoring=scoring5)
        r2[x]=results.mean()
        MSE[x]=results2.mean()
        EV[x]=results3.mean()
     #   ME[x]=results4.mean()
        MAE[x]=results5.mean()
        r_squared=pd.DataFrame.from_dict(r2, orient='index')
        r_squared = r_squared.reset_index()
        mse=pd.DataFrame.from_dict(MSE, orient='index')
        mse = mse.reset_index()
        EV=pd.DataFrame.from_dict(EV, orient='index')
        EV = EV.reset_index()
        MAE=pd.DataFrame.from_dict(MAE, orient='index')
        MAE = MAE.reset_index()
        r_squared["g_fit"] = "R_SQUARED"
        r_squared.columns=['Model_Name', 'Value',"Goodness_of_fit"]
        mse["g_fit"] = "MSE"
        mse.columns=['Model_Name', 'Value',"Goodness_of_fit"]
        EV["g_fit"] = "EV"
        EV.columns=['Model_Name', 'Value',"Goodness_of_fit"]
        MAE["g_fit"] = "MAE"
        MAE.columns=['Model_Name', 'Value',"Goodness_of_fit"]
        Goodness_of_fit=r_squared
        Goodness_of_fit['Model_Name'] = Goodness_of_fit['Model_Name'].astype(str)
        Goodness_of_fit=r_squared.append(mse)
        Goodness_of_fit=Goodness_of_fit.append(EV)
        Goodness_of_fit=Goodness_of_fit.append(MAE)
        Goodness_of_fit['Model_Name'] = Goodness_of_fit['Model_Name'].astype(str)
        #Model_ID=ID
        Goodness_of_fit['Model_ID']=ID
        Goodness_of_fit = Goodness_of_fit.reset_index()
        Goodness_of_fit= Goodness_of_fit.drop(['index'],axis=1)
        m=Goodness_of_fit['Value']
        m=m.tolist()
        m=[1,2,3,4]
        d={}
        for i in m:
            d[i]=uuid.uuid4()
           # Parameters3.loc[:,"TuningID"]= k[i]
        PK3=pd.DataFrame.from_dict(d, orient='index')
        PK3 = PK3.reset_index()
        PK3.columns = ['Model_Name','GF_ID2']
        #Tuning_ID=PK2
        Goodness_of_fit['GF_ID']=PK3['GF_ID2']
        #Goodness_of_fit.loc[:,"Model_ID"] = ID
        Goodness_of_fit=Goodness_of_fit.drop(['Model_Name'],axis=1)
    except:
        var = traceback.format_exc()   
        with open("error.txt", "a") as myfile:
            myfile.write(var)
    return Goodness_of_fit



def func4(x,X_train,y_train,y):
    #ID=y.loc[0,'Model_ID']
  
    global Goodness_of_fit
    global var
    try:
        ID=y
       
        #seed = 7
        sep='('
        ad=str(x)  
        ad=ad.split(sep,1)[0]
        if ad=="XGBClassifier":
            pred = x.predict(X_train)
            #pred = [round(value) for value in pred]
            
            pred = np.asarray([np.argmax(line) for line in pred])
        
        else:
            pred=x.predict(X_train)
        Accuracy={}
        AUC={}
        Precision={}
        f1_score2={}
        recall_score2={}
        results={}
        results2={}
        results = accuracy_score(y_train,pred,normalize=True)
        
        #results2 = auc(y_train,pred)
        results2= balanced_accuracy_score(y_train, pred)
        
        results3 = f1_score(y_train,pred, average='weighted')
        
        results4 = precision_score(y_train,pred,average='weighted')
        
        results5 = recall_score(y_train,pred,average='weighted')
        Accuracy[x]=results
        AUC[x]=results2
        Precision[x]=results3
        f1_score2[x]=results4
        recall_score2[x]=results5
        Accuracy=pd.DataFrame.from_dict(Accuracy, orient='index')
        Accuracy = Accuracy.reset_index()
        Balanced_Accuracy=pd.DataFrame.from_dict(AUC, orient='index')
        Balanced_Accuracy = Balanced_Accuracy.reset_index()
        Precision=pd.DataFrame.from_dict(Precision, orient='index')
        Precision = Precision.reset_index()
        f1_score2=pd.DataFrame.from_dict(f1_score2, orient='index')
        f1_score2 = f1_score2.reset_index()
        recall_score2=pd.DataFrame.from_dict(recall_score2, orient='index')
        recall_score2 = recall_score2.reset_index()
        
        Accuracy["g_fit"] = "Accuracy"
        Accuracy.columns=['Model_Name', 'Value',"Goodness_of_fit"]
        Balanced_Accuracy["g_fit"] = "Balanced_Accuracy"
        Balanced_Accuracy.columns=['Model_Name', 'Value',"Goodness_of_fit"]
        Precision["g_fit"] = "Precision"
        Precision.columns=['Model_Name', 'Value',"Goodness_of_fit"]
        f1_score2["g_fit"] = "f1_score"
        f1_score2.columns=['Model_Name', 'Value',"Goodness_of_fit"]
        recall_score2["g_fit"] = "recall_score"
        recall_score2.columns=['Model_Name', 'Value',"Goodness_of_fit"]
        Goodness_of_fit=Accuracy
        Goodness_of_fit['Model_Name'] = Goodness_of_fit['Model_Name'].astype(str)
        Goodness_of_fit=Accuracy.append(Balanced_Accuracy)
        Goodness_of_fit=Goodness_of_fit.append(Precision)
        Goodness_of_fit=Goodness_of_fit.append(f1_score2)
        Goodness_of_fit=Goodness_of_fit.append(recall_score2)
    
        Goodness_of_fit['Model_Name'] = Goodness_of_fit['Model_Name'].astype(str)
        #Model_ID=ID
        Goodness_of_fit['Model_ID']=ID
        Goodness_of_fit = Goodness_of_fit.reset_index()
        Goodness_of_fit= Goodness_of_fit.drop(['index'],axis=1)
        m=Goodness_of_fit['Value']
        m=[1,2,3,4,5]
        d={}
        for i in m:
            d[i]=uuid.uuid4()
           # Parameters3.loc[:,"TuningID"]= k[i]
        PK3=pd.DataFrame.from_dict(d, orient='index')
        PK3 = PK3.reset_index()
        PK3.columns = ['Model_Name','GF_ID2']
        #Tuning_ID=PK2
        Goodness_of_fit['GF_ID']=PK3['GF_ID2']
        #Goodness_of_fit.loc[:,"Model_ID"] = ID
        Goodness_of_fit=Goodness_of_fit.drop(['Model_Name'],axis=1)
   # Goodness_of_fit=Goodness_of_fit[['Goodness_of_fit', 'Value', 'Model_Id', 'GF_ID']]
    except:
        var = traceback.format_exc()
        with open("error.txt", "a") as myfile:
           myfile.write(var)

    return Goodness_of_fit

def cluster(kmeans,X_test,y_test,y):
    x=str(kmeans)
    #sep='('
    #x1=x.split(sep,1)[0]
    if "SpectralClustering" in x:
         pred=kmeans.fit_predict(X_test)
    elif "AgglomerativeClustering" in x:
         pred=kmeans.fit_predict(X_test)
    elif "DBSCAN" in x:
         pred=kmeans.fit_predict(X_test)      
    else:
        pred=kmeans.predict(X_test)    
    

    score2=adjusted_mutual_info_score(y_test,pred)
    score3=adjusted_rand_score(y_test,pred)
    
    if "AgglomerativeClustering" in x:
        score4="0"
    elif "DBSCAN" in x:
        score4="0"
    else:   
        score4=sum(np.min(cdist(X_test, kmeans.cluster_centers_, 'euclidean'), axis=1)) / X_test.shape[0]
    ID=y
   
    
   
    Score={}
    rand={}
    wss={}
    results={}
    results2={}

    Score[kmeans]=score2
    rand[kmeans]=score3
    wss[kmeans]=score4
    Adjusted_mutual_info=pd.DataFrame.from_dict(Score, orient='index')
    Adjusted_mutual_info = Adjusted_mutual_info.reset_index()
    Adjusted_rand_info=pd.DataFrame.from_dict(rand, orient='index')
    Adjusted_rand_info = Adjusted_rand_info.reset_index()
    WSS=pd.DataFrame.from_dict(wss, orient='index')
    WSS = WSS.reset_index()
    
    Adjusted_mutual_info["g_fit"] = "Adjusted_mutual_info"
    Adjusted_mutual_info.columns=['Model_Name', 'Value',"Goodness_of_fit"]
    Adjusted_rand_info["g_fit"] = "Adjusted_rand_info"
    Adjusted_rand_info.columns=['Model_Name', 'Value',"Goodness_of_fit"]
    WSS["g_fit"] = "WSS"
    WSS.columns=['Model_Name', 'Value',"Goodness_of_fit"]    
    Goodness_of_fit=Adjusted_mutual_info
    Goodness_of_fit['Model_Name'] = Goodness_of_fit['Model_Name'].astype(str)
    Goodness_of_fit=Goodness_of_fit.append(Adjusted_rand_info)
    Goodness_of_fit=Goodness_of_fit.append(WSS)

    Goodness_of_fit['Model_Name'] = Goodness_of_fit['Model_Name'].astype(str)
    #Model_ID=ID
    Goodness_of_fit['Model_ID']=ID
    Goodness_of_fit = Goodness_of_fit.reset_index()
    Goodness_of_fit= Goodness_of_fit.drop(['index'],axis=1)
    m=Goodness_of_fit['Value']
    m=[1,2,3]
    d={}
    for i in m:
        d[i]=uuid.uuid4()
       # Parameters3.loc[:,"TuningID"]= k[i]
    PK3=pd.DataFrame.from_dict(d, orient='index')
    PK3 = PK3.reset_index()
    PK3.columns = ['Model_Name','GF_ID2']
    #Tuning_ID=PK2
    Goodness_of_fit['GF_ID']=PK3['GF_ID2']
    #Goodness_of_fit.loc[:,"Model_ID"] = ID
    Goodness_of_fit=Goodness_of_fit.drop(['Model_Name'],axis=1)

    return Goodness_of_fit    


def final(lr,X_train,y_train):
    Model_Table=func(lr)
    ID=Model_Table.loc[0,'Model_ID']
    HP_Table=func1(lr,ID)
    GF_Table=func3(lr,X_train,y_train,ID)
    aaa=[Model_Table,HP_Table,GF_Table]
    Model_Table=aaa[0]
    HP_Table=aaa[1]
    GF_Table=aaa[2]
    if not os.path.isfile('Model_Table.csv'):
        Model_Table.to_csv('Model_Table.csv',header='column_names')
    else:
        Model_Table.to_csv('Model_Table.csv',mode='a',header=False)


    if not os.path.isfile('HP_Table.csv'):
        HP_Table.to_csv('HP_Table.csv',header='column_names')
    else:
        HP_Table.to_csv('HP_Table.csv',mode='a',header=False)

    if not os.path.isfile('GF_Table.csv'):
        GF_Table.to_csv('GF_Table.csv',header='column_names')
    else:
        GF_Table.to_csv('GF_Table.csv',mode='a',header=False)
    return [Model_Table,HP_Table,GF_Table]

def csv(aaa):
    Model_Table=aaa[0]
    HP_Table=aaa[1]
    GF_Table=aaa[2]
    if not os.path.isfile('Model_Table.csv'):
        Model_Table.to_csv('Model_Table.csv',header='column_names')
    else:
        Model_Table.to_csv('Model_Table.csv',mode='a',header=False,index=False)


    if not os.path.isfile('HP_Table.csv'):
        HP_Table.to_csv('HP_Table.csv',header='column_names')
    else:
        HP_Table.to_csv('HP_Table.csv',mode='a',header=False,index=False)

    if not os.path.isfile('GF_Table.csv'):
        GF_Table.to_csv('GF_Table.csv',header='column_names')
    else:
        GF_Table.to_csv('GF_Table.csv',mode='a',header=False,index=False)
    return Model_Table

class data:
    def __init__(self,path2):
        self.path2=path2
    
    def save(self):
        path2=self.path2
        PK={}

        Data_Table = pd.DataFrame(columns=['Data_Name','Data_ID'])
        if not os.path.isfile('Data_Table.csv'):
            Data_Table.to_csv('Data_Table.csv',header='column_names',index=False)    
        else:
            Data_Table=pd.read_csv('Data_Table.csv')
        #aaa2=(Data_Table.Data_Name=='name').all()  #name
        A=Data_Table[Data_Table['Data_Name'].astype(str).str[:].str.contains(path2)]
           
        b=A.empty
        ID=A['Data_ID']     
    
        if b==True:
            PK={}
            PK[path2] = uuid.uuid4()
            PK2=pd.DataFrame.from_dict(PK, orient='index')
          
            PK2 = PK2.reset_index()
            Data_Table2=PK2
            Data_Table2.columns = ['Data_Name', 'Data_ID']
            Data_Table2['Data_Name'] = Data_Table2['Data_Name'].astype(str)
            Data_Table2['Data_ID'] = Data_Table2['Data_ID'].astype(str)
           # column_names=["Data_Name","Data_ID"
            if not os.path.isfile('Data_Table.csv'):
                Data_Table2.to_csv('Data_Table.csv',header='column_names',index=False)
            else:
                Data_Table2.to_csv('Data_Table.csv',mode='a',header=False, index=False)
            ID=Data_Table2['Data_ID']
            print("Generated a new DID")
        else:
            ID=A['Data_ID']
            print("Found your DID")
    
        return print("DID: " +ID )


class tracker:
    def __init__(self,lr,X_test,y_test):
        self.lr=lr
        self.X_test=X_test
        self.y_test=y_test
    
    
      
    def save(self):#,lr=None,X_test=None,y_test=None):
        
        lr=self.lr
        X_test=self.X_test
        y_test=self.y_test
        #k=self.k
        
      
        Model_Table=func(lr)
        ID=Model_Table.loc[0,'Model_ID']
        HP_Table=func1(lr,ID)
        
        from sklearn.utils.testing import all_estimators
        from sklearn import base

        estimators = all_estimators()
        x=[]
        for name, class_ in estimators:
            if issubclass(class_, base.ClassifierMixin):
                x.append(name)
        x.append("XGBClassifier")
        y=[]
        for name, class_ in estimators:
            if issubclass(class_, base.RegressorMixin):
                y.append(name)
        y.append("XGBRegressor")
        z=[]
        for name, class_ in estimators:
            if issubclass(class_, base.ClusterMixin):
                z.append(name)
        sep='('
        ad=str(lr)  
        ad=ad.split(sep,1)[0]
        if ad in y:
            GF_Table=func3(lr,X_test,y_test,ID)
        elif ad in x:
            GF_Table=func4(lr,X_test,y_test,ID)
        else:
            GF_Table=cluster(lr,X_test,y_test,ID) 
        #GF_Table=func3(lr,X_test,y_test,ID)
        aaa=[Model_Table,HP_Table,GF_Table]
        Model_Table=aaa[0]
        HP_Table=aaa[1]
        GF_Table=aaa[2]
        if not os.path.isfile('Model_Table.csv'):
            Model_Table.to_csv('Model_Table.csv',header='column_names',index=False)
        else:
            Model_Table.to_csv('Model_Table.csv',mode='a',header=False,index=False)
    
    
        if not os.path.isfile('HP_Table.csv'):
            HP_Table.to_csv('HP_Table.csv',header='column_names',index=False)
        else:
            HP_Table.to_csv('HP_Table.csv',mode='a',header=False,index=False)
    
        if not os.path.isfile('GF_Table.csv'):
            GF_Table.to_csv('GF_Table.csv',header='column_names',index=False)
        else:
            GF_Table.to_csv('GF_Table.csv',mode='a',header=False,index=False)
         
        engine = create_engine('mssql+pyodbc://admin_login:%s@manutd8.database.windows.net/IICS_Logs?driver=SQL+Server+Native+Client+11.0'% parse.unquote_plus('Miracle@123')) 

        connection = engine.connect()

            
            
        Model_Table.to_sql('Model_Table', con = engine, if_exists = 'append', chunksize = 1000,index=False)
        HP_Table.to_sql('HP_Table', con = engine, if_exists = 'append', chunksize = 1000,index=False)
        GF_Table.to_sql('GF_Table', con = engine, if_exists = 'append', chunksize = 1000,index=False)
        nice=[Model_Table,HP_Table,GF_Table]
        nice2="Tables updated !"
        
  
        return print(nice, nice2) 
    
    
    
    
    def classification(self):#,lr=None,X_test=None,y_test=None):
        lr=self.lr
        X_test=self.X_test
        y_test=self.y_test
        
        
  
        Model_Table=func(lr)
        ID=Model_Table.loc[0,'Model_ID']
        HP_Table=func1(lr,ID)
        GF_Table=func4(lr,X_test,y_test,ID)
        aaa=[Model_Table,HP_Table,GF_Table]
        Model_Table=aaa[0]
        HP_Table=aaa[1]
        GF_Table=aaa[2]
        if not os.path.isfile('Model_Table.csv'):
            Model_Table.to_csv('Model_Table.csv',header='column_names')
        else:
            Model_Table.to_csv('Model_Table.csv',mode='a',header=False)
    
    
        if not os.path.isfile('HP_Table.csv'):
            HP_Table.to_csv('HP_Table.csv',header='column_names')
        else:
            HP_Table.to_csv('HP_Table.csv',mode='a',header=False)
    
        if not os.path.isfile('GF_Table.csv'):
            GF_Table.to_csv('GF_Table.csv',header='column_names')
        else:
            GF_Table.to_csv('GF_Table.csv',mode='a',header=False)
        return [Model_Table,HP_Table,GF_Table]
    
    def clustering(self):#,lr=None,X_test=None,y_test=None):
        lr=self.lr
        X_test=self.X_test
        y_test=self.y_test
        
        
        
        Model_Table=func(lr)
        ID=Model_Table.loc[0,'Model_ID']
        HP_Table=func1(lr,ID)
        GF_Table=cluster(lr,X_test,y_test,ID)
        aaa=[Model_Table,HP_Table,GF_Table]
        Model_Table=aaa[0]
        HP_Table=aaa[1]
        GF_Table=aaa[2]
        if not os.path.isfile('Model_Table.csv'):
            Model_Table.to_csv('Model_Table.csv',header='column_names')
        else:
            Model_Table.to_csv('Model_Table.csv',mode='a',header=False)
    
    
        if not os.path.isfile('HP_Table.csv'):
            HP_Table.to_csv('HP_Table.csv',header='column_names')
        else:
            HP_Table.to_csv('HP_Table.csv',mode='a',header=False)
    
        if not os.path.isfile('GF_Table.csv'):
            GF_Table.to_csv('GF_Table.csv',header='column_names')
        else:
            GF_Table.to_csv('GF_Table.csv',mode='a',header=False)
        return print( [Model_Table,HP_Table,GF_Table] +"Tables Updated !")
        
















