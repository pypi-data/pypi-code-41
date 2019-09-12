import cupy as cp
import h5py


#加载数据的function
def load_data():
    train_dataset = h5py.File('../datasets/train_signs.h5', "r")
    train_set_x_orig = cp.array(train_dataset["train_set_x"][:])  # your train set features
    train_set_y_orig = cp.array(train_dataset["train_set_y"][:])  # your train set labels

    test_dataset = h5py.File('../datasets/test_signs.h5', "r")
    test_set_x_orig = cp.array(test_dataset["test_set_x"][:])  # your test set features
    test_set_y_orig = cp.array(test_dataset["test_set_y"][:])  # your test set labels


    train_set_y_orig = train_set_y_orig.reshape((1, train_set_y_orig.shape[0]))
    test_set_y_orig = test_set_y_orig.reshape((1, test_set_y_orig.shape[0]))

    train_set_x_orig=train_set_x_orig.transpose(0,3,1,2)

    test_set_x_orig=test_set_x_orig.transpose(0,3,1,2)

    return train_set_x_orig, train_set_y_orig.T, test_set_x_orig, test_set_y_orig.T
