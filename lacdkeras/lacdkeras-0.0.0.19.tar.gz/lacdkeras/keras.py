import keras
import numpy as np
np.random.seed(1337)
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import Dense
from keras.utils import to_categorical
from keras.utils import np_utils
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.optimizers import SGD
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle

#這邊的資料是用來畫圖的,可以忽略!
class lacdkeras_model():

    def __init__(self):
        self.activation = 'relu'
        self.epoch = 20
        self.batch_size = 128
        print('--函式說明--')
        print('函式1: set_activation(變數名稱)\t\t\t=>用於設定活化函數為何\n')
        print('函式2: set_epoch(代數)\t\t\t\t=>用於設定要訓練幾代\n')
        print('函式3: set_train_data(變項資料,分類為何)\t=>用於設定要訓練的資料為何\n')
        print('函式4: set_test_data(變項資料,分類為何)\t\t=>用於設定批量大小為何\n')
        print('函式5: set_neuron_level(神經元個數的陣列)\t=>用於設定隱藏層數量及層數為何\n')
        print('函式6: predict_data()\t\t\t\t=>用於預測新的數據,單筆資料可以放入List(),多筆資料可以使用雙層List\n')
        print('------單筆資料可以放入List(),多筆資料可以使用雙層List')
        print('------多筆資料可以使用雙層List\n')
        print('函式7: get_acc()\t\t\t\t=>用於得到此模型的正確率,回傳(訓練正確率,測試正確率)\n')
        print('函式8: run_model\t\t\t\t=>開始跑神經網絡\n')
        print('函式9: show_history()\t\t\t\t=>用於顯示訓練過程\n')
        print('-----------')

    def set_activation(self,activation_name):
        activation_names = np.array(['relu','sigmoid'])
        if activation_name in activation_names:
            self.activation = activation_name
            print('Activation設定為:'+activation_name)
        else:
            print('目前不支援:'+activation_name)
            print('Activation將會預設為relu')

    def set_epoch(self,epoch):
        
        if epoch >10000:
            print('epoch請勿設定超過10000代，以避免系統當機!')
            return 
        elif epoch <1 :
            print('epoch請勿設定小於1代，以避免系統當機!')
            return

        self.epoch = epoch
        print('epoch設定為:'+str(epoch))

    def set_batch_size(self,batch_size):

        if batch_size >1000:
            print('batch_size請勿設定超過1000，以避免系統當機!')
            return 
        elif batch_size <1 :
            print('batch_size請勿設定小於1，以避免系統當機!')
            return

        self.batch_size = batch_size
        print('batch_size設定為:'+str(batch_size))

    def set_train_data(self,x_train,y_train):
        try:
            self.x_train = x_train
            self.Input_size = len(self.x_train[0])

            self.y_train = np_utils.to_categorical(y_train)
            self.Output_size = len(self.y_train[0])
            print('訓練資料設定成功')
        except:
            print('訓練資料輸入錯誤，請重新確認輸入資料的格式!')
        

    def set_test_data(self,x_test,y_test):
        try:
            self.x_test = x_test
            self.y_test = np_utils.to_categorical(y_test)
            print('測試資料設定成功')
        except:
            print('測試資料輸入錯誤，請重新確認輸入資料的格式!')
    def set_neuron_level(self,neuron_count):
        #check neuron_count correct
        for neuron in neuron_count:
            if neuron <=0:
                print('neuron 設定錯誤，不可小於等於0')
                return
            elif neuron>10000:
                print('neuron 設定錯誤，不可大於10000')
                return
        print('===========')
        print('neuron設定成功')
        self.neuron_count = neuron_count

        try:
            print('輸入層:\t'+str(self.Input_size)+'\t個輸入項')
            for neuron_index in range(0,len(neuron_count),1):
                print('第'+str(neuron_index+1)+'層:\t'+str(neuron_count[neuron_index])+'\t個神經元')
            print('輸出層:\t'+str(self.Output_size)+'\t個輸出項')
            print('===========')
        except:
            print('請先設定training_data跟testing_data')
            print('再做神經元及層數設定!')
        #check End

    def run_model(self):
        
        self.model = Sequential()#先將模型初始化
        if len(self.neuron_count)>0:
            self.model.add(Dense(units = self.neuron_count[0],activation= self.activation,input_shape = (self.Input_size,)))
            for level_Index in range(1,len(self.neuron_count),1):
                self.model.add(Dense(units = self.neuron_count[level_Index],activation= self.activation))

            self.model.add(Dense(output_dim = self.Output_size,activation='softmax'))
        else:
            print('Linear Regression model')
            self.model.add(Dense(output_dim = self.Output_size,activation= 'softmax',input_shape = (self.Input_size,)))
        self.model.compile(loss='categorical_crossentropy', optimizer=SGD(lr=0.01, momentum=0.9, nesterov=True), metrics=['accuracy'])
        self.model.summary()#顯示目前建立的模型結構


        self.train_history = self.model.fit(self.x_train, self.y_train,      #輸入 與 輸出
                  nb_epoch = self.epoch,       #子代數
                  batch_size = self.batch_size,#批量大小 一次參考多少的數據 4=> 00 01 10 11一同參考
                  verbose = 1 ,           #是否顯示訓練過程 1=>是  2=>否
                  validation_data=(self.x_test, self.y_test)) #拿來預測的資料  (此使用與輸入相同的資料!)
        #train_history 為紀錄更新的軌跡圖

        #最後輸出測試資料跟訓練資料的正確率!
        score = self.model.evaluate(self.x_train, self.y_train,)
        self.train_acc = score[1]
        print ('\nTrain Acc:', score[1])
        score = self.model.evaluate(self.x_test, self.y_test)
        self.test_acc = score[1]
        print ('\nTest Acc:', score[1])
        #開始使用修正完的參數做預測，並將"預測"的結果放置在classes裡面
        classes = self.model.predict_classes(self.x_test, batch_size=self.batch_size)
    
    def predict_data(self,predict_data):
        if not isinstance(predict_data[0], list):
            test = predict_data
            predict_data = []
            predict_data.append(test)


        if len(predict_data[0]) != self.Input_size:
            print('預測的變項數量不一喔!')
            print('需要的變項個數為:'+str(self.Input_size))
            print('但是輸入的變項個數為:'+str(len(predict_data[0])))
            return 

        predict_data = np.array(predict_data)
        classes = self.model.predict_classes(predict_data, batch_size=self.batch_size)
        
        print('預測類別',end = '')
        for Input_index in range(0,self.Input_size,1):
            print('\t變項'+str(Input_index+1),end = '')
        print()

        for dataindex in range(0,len(predict_data),1):
            print(str(classes[dataindex])+'\t\t',end = '')
            for Input_index in predict_data[dataindex]:
                print(str(Input_index)+'\t',end = '')
            print()
        print('========')
        print('預測完畢!')
    #用於獲得正確率
    def get_acc(self):
        return self.train_acc,self.test_acc

    #這邊的資料是用來畫圖的,可以忽略!
    def show_history(self):
        plt.subplot(211)
        plt.plot(self.train_history.history['acc'])
        plt.plot(self.train_history.history['val_acc'])
        plt.title('Train_Test History')
        plt.ylabel('acc')
        plt.legend(['train_acc', 'test_acc'], loc='upper left')
        

        plt.subplot(212)
        plt.plot(self.train_history.history['loss'])
        plt.plot(self.train_history.history['val_loss'])
        plt.ylabel('loss')
        plt.xlabel('Epoch')
        plt.legend(['train_loss', 'test_loss'], loc='upper left')
        plt.show()

    def question(self):
        print('--函式說明--')
        print('函式1: set_activation(變數名稱)\t\t\t=>用於設定活化函數為何\n')
        print('函式2: set_epoch(代數)\t\t\t\t=>用於設定要訓練幾代\n')
        print('函式3: set_train_data(變項資料,分類為何)\t=>用於設定要訓練的資料為何\n')
        print('函式4: set_test_data(變項資料,分類為何)\t\t=>用於設定批量大小為何\n')
        print('函式5: set_neuron_level(神經元個數的陣列)\t=>用於設定隱藏層數量及層數為何\n')
        print('函式6: predict_data()\t\t\t\t=>用於預測新的數據,單筆資料可以放入List(),多筆資料可以使用雙層List\n')
        print('------單筆資料可以放入List(),多筆資料可以使用雙層List')
        print('------多筆資料可以使用雙層List\n')
        print('函式7: get_acc()\t\t\t\t=>用於得到此模型的正確率,回傳(訓練正確率,測試正確率)\n')
        print('函式8: run_model\t\t\t\t=>開始跑神經網絡\n')
        print('函式9: show_history()\t\t\t\t=>用於顯示訓練過程\n')
        print('-----------')

class lacdkeras_data():

    def __init__(self):
        print('--函式說明--')
        print('函式1: set_csvdata(檔案名稱)\t\t\t=>用於將資料做前處理，整理成類別跟輸入資料\n')
        print('----請注意資料格式為----')
        print('-類別\t變項1\t變項2\t變項3')
        print('0\t1\t2\t3')
        print('0\t1\t6\t2')
        print('1\t5\t4\t4')
        print('1\t2\t4\t5')
        print('====================')
        print('函式2: split_train_test_data()\t\t\t=>用於將資料分割成訓練資料及測試資料\n')
        print('函式3: show()\t\t\t\t\t=>用於顯示目前所有資料的狀況為何?\n')
        print('-----------')
        print('--變數說明--')
        print('Data_Input   =>所有資料的輸入變項')
        print('Data_Level   =>所有資料的類別\n')
        print('x_train      =>訓練資料的輸入變項')
        print('y_train      =>訓練資料的類別\n')
        print('x_test       =>測試資料的輸入變項')
        print('y_test       =>測試資料的類別')

    def set_csvdata(self,csv_name):
        self.csv_name = csv_name
        fp = open(self.csv_name,'r',encoding="utf-8")
        All_Lines = fp.readlines()
        Data_Input = []
        Data_Level = []

        #第一行為資料集,不放
        for Line_index in range(1,len(All_Lines),1):
            Line_sentence = All_Lines[Line_index].replace('\t',',')

            while(',,' in Line_sentence):
                Line_sentence = Line_sentence.replace(',,',',')

            Data_Split = Line_sentence.replace('\n','').split(',')
            Data_Level.append(Data_Split[0]) 
            Data_Input_stack = []
            for everyInput in range(1,len(Data_Split),1):
                Data_Input_stack.append(Data_Split[everyInput])
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
        print('函式1: set_csvdata(檔案名稱)\t\t\t=>用於將資料做前處理，整理成類別跟輸入資料\n')
        print('函式2: split_train_test_data()\t\t\t=>用於將資料分割成訓練資料及測試資料\n')
        print('函式3: show()\t\t\t=>用於顯示目前所有資料的狀況為何?\n')
        print('-----------')
        print('--變數說明--')
        print('Data_Input   =>所有資料的輸入變項')
        print('Data_Level   =>所有資料的類別\n')
        print('x_train      =>訓練資料的輸入變項')
        print('y_train      =>訓練資料的類別\n')
        print('x_test       =>測試資料的輸入變項')
        print('y_test       =>測試資料的類別')

