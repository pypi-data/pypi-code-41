import numpy as np
import math
import random
#激活函数
def ReLu(z):
    return z if z > 0.0 else 0.0
class Matrix(object):
    def __init__(self, row, column):
        self.Cols = column
        self.Rows = row
        self.Vals = np.zeros((row, column)) #矩阵值
        return
    #由二维数组构建
    @staticmethod
    def from2dArray(raw : np.ndarray):
        self = Matrix(0, 0)
        self.Rows = len(raw)
        self.Cols = len(raw[0])
        self.Vals = np.zeros((self.Rows, self.Cols))
        for i in range(self.Rows):
            for j in  range(self.Cols):
                self.Vals[i][j] = raw[i][j]
        return self
    #从列表获得一个单列矩阵
    @staticmethod
    def fromArray(raw : list):
        self = Matrix(len(raw), 1)
        for i in range(self.Rows):
            self.Vals[i][0] = raw[i]
        return self
    def dot(self, matrx):
        rst = Matrix(self.Rows, matrx.Cols)
        if self.Cols == matrx.Rows:
            for i in range(self.Rows):
                for j in range(matrx.Cols):
                    sum = 0.0
                    for k in range(self.Cols):
                        sum += self.Vals[i][k] * matrx.Vals[k][j]
                    rst.Vals[i][j] = sum
        return rst
    def zeroing(self):
        for i in range(self.Rows):
            for j in range(self.Cols):
                self.Vals[i][j] = 0.0
        return
    def multiply_add_assign(self, val):
        rst = Matrix(self.Rows, self.Cols)
        for i in range(self.Rows):
                for j in range(self.Cols):
                    rst.Vals[i][j] = val * self.Vals[i][j]
        return rst
    #operator"+="
    def add_and_assign(self, mtrx):
        if self.Cols == mtrx.Cols and self.Rows == mtrx.Rows:
            for i in range(self.Rows):
                for j in range(self.Cols):
                    self.Vals[i][j] += mtrx.Vals[i][j]
        return
    #随机化矩阵值
    def randomize(self):
        for i in range(self.Rows):
            for j in  range(self.Cols):
                self.Vals[i][j] = abs(0.01 * np.random.randn())
        return
    def toArray(self):
        rst = [1.0] * (self.Cols * self.Rows)
        for i in range(self.Rows):
            for j in range(self.Cols):
                rst[i * self.Cols + j] = self.Vals[i][j]
        return rst
    def addBias(self):
        rst = Matrix(self.Rows + 1, 1)
        for i in range(self.Rows):
            rst.Vals[i][0] = self.Vals[i][0]
        rst.Vals[self.Rows][0] = 1.0
        return rst
    def activate(self):
        rst = Matrix(self.Rows, self.Cols)
        for i in range(self.Rows):
             for j in range(self.Cols):
                 rst.Vals[i][j] = ReLu(self.Vals[i][j])
        return rst
    def mutate(self, rate):
        for i in range(self.Rows):
             for j in range(self.Cols):
                 if random.random() < rate:
                     #replace the randomGaussian() for lacking this function
                     self.Vals[i][j] += np.random.randn() / 3.0
                     if self.Vals[i][j] > 1.0:
                         self.Vals[i][j] = 1.0
                     elif self.Vals[i][j] < -1.0:
                         self.Vals[i][j] = -1.0
        return
    #矩阵杂交
    #限定 : shape(matrx.Vals) == shape(self.Vals)
    def crossover(self, matrx):
        rst = Matrix(self.Rows, self.Cols)
        randC = math.floor(random.random() * self.Cols)
        randR = math.floor(random.random() * self.Rows)
        for i in range(self.Rows):
            for j in range(self.Cols):
                if i < randR or (i == randR and j <= randC) :
                    rst.Vals[i][j] = self.Vals[i][j]
                else:
                    rst.Vals[i][j] = matrx.Vals[i][j]
        return rst
    def clone(self):
        rst = Matrix(self.Rows, self.Cols)
        for i in range(self.Rows):
            for j in range(self.Cols):
                rst.Vals[i][j] = self.Vals[i][j] 
        return rst
    def setVals(self, vals : list):
        for i in range(self.Rows):
            for j in range(self.Cols):
                self.Vals[i][j] = vals[i * self.Cols + j]
        return
    def __str__(self):
        str = "|"
        for i in range(self.Rows - 1):
            for j in range(self.Cols):
                str += "{},\t".format(self.Vals[i][j])
            str += "|\n|"
        for j in range(self.Cols):
            str += "{},\t".format(self.Vals[self.Rows - 1][j])
        str += "|\n"
        return str
    def rotate_90(self):
        rst = Matrix(self.Cols, self.Rows)
        for i in range(self.Rows):
            for j in range(self.Cols):
                rst.Vals[j][self.Cols - i] = self.Vals[i][j]
        return rst
    def rotate_180(self):
        rst = Matrix(self.Rows, self.Cols)
        for i in range(self.Rows):
            for j in range(self.Cols):
                rst.Vals[i][j] = self.Vals[self.Rows - 1 - i][self.Cols - 1 - j]
        return rst
    #return : the Matrix result of convolution"self * mtrx"
    #in use: self -> buffer of some picture
    #        mtrx -> conv sum(assert mtrx.Rows == mtrx.Cols)
    def conv_full(self, mtrx):
        #rotate conv_sum:
        mtrx = mtrx.rotate_180()
        #expand picture:
        pic = Matrix(self.Rows + 2 * (mtrx.Rows - 1),\
                     self.Cols + 2 * (mtrx.Cols - 1))
        s_row = mtrx.Rows - 1
        s_col = mtrx.Cols - 1
        for i in range(self.Rows):
            for j in range(self.Cols):
                pic.Vals[s_row + i][s_col + j] = self.setVals[i][j]
        #conv------------------------------------------------------
        conv_rst = Matrix(pic.Rows - mtrx.Rows + 1, pic.Cols - mtrx.Cols + 1)
        for i in range(conv_rst.Rows):
            for j in range(conv_rst.Cols):
                sum = 0.0
                for r in range(mtrx.Rows):
                    for c in range(mtrx.Cols):
                        sum += mtrx.Vals[r][c] * pic.Vals[i + r][j + c]
                conv_rst.Vals[i][j] = sum
        #----------------------------------------------------------
        return conv_rst
    def conv_same(self, mtrx):
        #rotate conv_sum:
        mtrx = mtrx.rotate_180()
        #expand picture:
        pic = Matrix(self.Rows + 2 * (mtrx.Rows - 1),\
                     self.Cols + 2 * (mtrx.Cols - 1))
        s_row = mtrx.Rows - 1
        s_col = mtrx.Cols - 1
        for i in range(self.Rows):
            for j in range(self.Cols):
                pic.Vals[s_row + i][s_col + j] = self.Vals[i][j]
        #conv------------------------------------------------------
        conv_rst = Matrix(self.Rows, self.Cols)
        shift_r = int(mtrx.Rows >> 1)
        shift_c = int(mtrx.Cols >> 1)
        for i in range(conv_rst.Rows):
            for j in range(conv_rst.Cols):
                sum = 0.0
                for r in range(mtrx.Rows):
                    for c in range(mtrx.Cols):
                        sum += mtrx.Vals[r][c] * pic.Vals[i + r + shift_r][j + c + shift_c]
                conv_rst.Vals[i][j] = sum
        #----------------------------------------------------------
        return conv_rst
    def conv_valid(self, mtrx):
        #rotate conv_sum:
        mtrx = mtrx.rotate_180()
        #conv------------------------------------------------------
        conv_rst = Matrix(self.Rows - mtrx.Rows + 1, self.Cols - mtrx.Cols + 1)
        for i in range(conv_rst.Rows):
            for j in range(conv_rst.Cols):
                sum = 0.0
                for r in range(mtrx.Rows):
                    for c in range(mtrx.Cols):
                        sum += mtrx.Vals[r][c] * self.Vals[i + r][j + c]
                conv_rst.Vals[i][j] = sum
        #----------------------------------------------------------
        return conv_rst
############################################################