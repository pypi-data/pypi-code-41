from k_torch.layers import Dense, Dropout
from k_torch.models import Sequential
from k_torch.optimizers import Adam

import numpy as np


# data preparation
X_train = [[3,4],[2,3],[4,3],[2,3],[3,4],[2,3],[7,8],[8,9],[9,9]]
y_train = [1.2,1.3,1.4,1.5,1.6,1.7,7,8,8]
X_train = np.asarray (X_train)
y_train = np.asarray(y_train)
y_train = y_train.reshape(-1,1)

# X_val = [[9,7],[1,3]]
# y_val = [7.8,1.6]
# X_val = np.asarray (X_val)
# y_val = np.asarray(y_val)
# y_val = y_val.reshape(-1,1)
#
# model = Sequential()
# model.add(Dense(2), input_shape = (2,))
# model.add(Dense(5))
# model.add(Dense(1))
#
# model.compile(loss ='mse', optimizer=Adam(lr = 0.01))
#
# model.fit(X_train,y_train,nb_epochs=500,verbose=False,should_plot_history=False,validation_data={'X_test' : X_val, 'y_test':y_val})
#
#

model = Sequential()
model.add(Dense(2), input_shape = (2,))
model.add(Dense(5,activation='relu'))
model.add(Dense(1,activation='relu'))
model.add(Dropout(0.1))
model.compile(loss ='mse', optimizer=Adam(lr = 0.01))
history = model.fit(X_train,y_train,epochs=5,verbose=False,should_plot_history=False)