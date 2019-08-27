from sklearn.model_selection import train_test_split
import numpy as np
np.random.seed(1337)  # for reproducibility
import math
from sklearn.utils import shuffle

class Data():

    def __init__(self,csv_name):
        self.csv_name = csv_name
        print('--函式說明--')
        print('函式1: Data_organization()     =>用於將資料做前處理，整理成類別跟輸入資料\n')
        print('函式2: split_train_test_data() =>用於將資料分割成訓練資料及測試資料\n')
        print('函式2: show()                  =>用於顯示目前所有資料的狀況為何?\n')
        print('-----------')
        print('--變數說明--')
        print('Data_Input   =>所有資料的輸入變項')
        print('Data_Level   =>所有資料的類別\n')
        print('x_train      =>訓練資料的輸入變項')
        print('y_train      =>訓練資料的類別\n')
        print('x_test       =>測試資料的輸入變項')
        print('y_test       =>測試資料的類別')

    def Data_organization(self):
        fp = open(self.csv_name,'r',encoding="utf-8")
        All_Lines = fp.readlines()
        Data_Input = []
        Data_Level = []

        for Line in All_Lines:
            Data_Split = Line.replace('\n','').split(',')
            Data_Level.append(Data_Split[0]) 
            Data_Input_stack = []
            for everyInput in range(1,len(Data_Split),1):
                Data_Input_stack.append(everyInput)
            Data_Input.append(Data_Input_stack)

        self.Data_Input = Data_Input
        self.Data_Level = Data_Level

    def split_train_test_data(self,split_size):
        #用於分割Trainging Data 跟Testing Data
        if split_size>=1 or split_size <=0:
            print('請將分割的比例調整到0~1之間!')
            return 0
        data = np.array(self.Data_Input)
        label = np.array(self.Data_Level)
        Data, Label = shuffle(data, label , random_state = 3)

        self.x_train, self.x_test, self.y_train, self.y_test = train_test_split(Data, Label,test_size=split_size,random_state=4)
        print('--顯示Train Data 跟Testing Data的數量--')
        Training_Level = {}
        for index in self.y_train:
            if index not in Training_Level:
                Training_Level[index] = 0
            Training_Level[index] = Training_Level[index]+1
        sorted(Training_Level.keys())
        print('-Training Data-')
        print('類別\t數量')
        for Level_index in Training_Level:
            print(str(Level_index)+'\t'+str(Training_Level[Level_index]))

        Testing_Level = {}
        for index in self.y_test:
            if index not in Testing_Level:
                Testing_Level[index] = 0
            Testing_Level[index] = Testing_Level[index]+1
        sorted(Testing_Level.keys())
        print('-Testing Data-')
        print('類別\t數量')
        for Level_index in Testing_Level:
            print(str(Level_index)+'\t'+str(Testing_Level[Level_index]))
        print('Finish Split')

    def show(self):
        print('-顯示數據集-')
        print('以下顯示的為我們所輸入的數據集')
        print('類別:拿來預測後最後的結果為何(EX:是否會下雨)')
        print('(1):要拿來預測的變項之一(EX:溫度)')
        print('(2):要拿來預測的變項之一(EX:濕度)')
        print('(3):要拿來預測的變項之一(EX:雲量)')
        print('PS.僅會顯示前10項資訊')
        print('\n\n============================================')
        print('類別\t',end = '')
        for index in range(0,len(self.Data_Input[0]),1):
            print('('+str(index+1)+')\t',end = '')
        print()

        if(len(self.Data_Level)>10):
            for Level_Index in range(0,10,1):
                print(self.Data_Level[Level_Index]+'\t',end = '')
                for Input_Index in range(0,len(self.Data_Input[Level_Index]),1):
                    print(str(self.Data_Input[Level_Index][Input_Index])+'\t',end = '')
                print()
        else:
            for Level_Index in range(0,len(self.Data_Input[Level_Index]),1):
                print(self.Data_Level[Level_Index]+'\t',end = '')
                for Input_Index in range(0,len(self.Data_Input[Level_Index]),1):
                    print(self.Data_Input[Level_Index][Input_Index]+'\t',end = '')
                print()

    def question(self):
        print('--函式說明--')
        print('函式1: Data_organization()     =>用於將資料做前處理，整理成類別跟輸入資料\n')
        print('函式2: split_train_test_data() =>用於將資料分割成訓練資料及測試資料\n')
        print('函式2: show()                  =>用於顯示目前所有資料的狀況為何?\n')
        print('-----------')
        print('--變數說明--')
        print('Data_Input   =>所有資料的輸入變項')
        print('Data_Level   =>所有資料的類別\n')
        print('x_train      =>訓練資料的輸入變項')
        print('y_train      =>訓練資料的類別\n')
        print('x_test       =>測試資料的輸入變項')
        print('y_test       =>測試資料的類別')
