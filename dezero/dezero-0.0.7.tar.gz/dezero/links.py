import contextlib
import numpy as np
import dezero.functions as F
from dezero.core import Variable


class Link:

    def __init__(self):
        self._within_init_scope = False
        self._params = set()

    def __setattr__(self, name, value):
        if isinstance(value, Variable) and self._within_init_scope:
            self._params.add(value)
        super().__setattr__(name, value)

    def params(self):
        for param in self._params:
            yield param

    def cleargrads(self):
        for param in self.params():
            param.cleargrad()

    @contextlib.contextmanager
    def init_scope(self):
        old_flg = self._within_init_scope
        self._within_init_scope = True

        yield

        self._within_init_scope = old_flg

    def serialize(self, serializer):
        d = self.__dict__
        for name, value in d.items():
            if isinstance(value, Variable):
                serializer(name, value.data)


class Chain(Link):

    def __init__(self):
        super().__init__()
        self._children = set()

    def __setattr__(self, name, link):
        if isinstance(link, Link) and self._within_init_scope:
            self._children.add(link)
        super().__setattr__(name, link)

    def params(self):
        for link in self._children:
            for param in link.params():
                yield param

    def serialize(self, serializer):
        super().serialize(serializer)
        d = self.__dict__
        for key, value in d.items():
            if isinstance(value, Link):
                value.serialize(serializer[key])


class Linear(Link):

    def __init__(self, in_size, out_size, nobias=False):
        super().__init__()

        I, O = in_size, out_size
        with self.init_scope():
            self.W = Variable(np.random.randn(I, O) * np.sqrt(1/I), name='W')
            if nobias:
                self.b = None
            else:
                self.b = Variable(np.zeros(O), name='b')

    def __call__(self, x):
        y = F.matmul(x, self.W)
        if self.b is not None:
            y += self.b
        return y


class EmbedID(Link):

    def __init__(self, in_size, out_size):
        super().__init__()
        with self.init_scope():
            self.W = Variable(np.random.randn(in_size, out_size), name='W')

    def __call__(self, x):
        y = self.W[x]
        return y


class Classifier(Chain):

    def __init__(self, predictor,
                 lossfun=F.softmax_cross_entropy,
                 accfun=F.accuracy):
        super().__init__()

        self.lossfun = lossfun
        self.accfun = accfun
        self.y = None
        self.loss = None
        self.accuracy = None

        with self.init_scope():
            self.predictor = predictor

    def __call__(self, x, t):
        self.y = self.predictor(x)
        self.loss = self.lossfun(self.y, t)
        
        if self.accfun is not None:
            self.accuracy = self.accfun(self.y, t)
        return self.loss


class RNN(Chain):

    def __init__(self, in_size, hidden_size):
        super().__init__()

        I, H = in_size, hidden_size
        with self.init_scope():
            self.x2h = Linear(I, H)
            self.h2h = Linear(H, H)

        self.h = None

    def reset_state(self):
        self.h = None

    def __call__(self, x):
        if self.h is None:
            h_new = F.tanh(self.x2h(x))
        else:
            h_new = F.tanh(self.x2h(x) + self.h2h(self.h))

        self.h = h_new
        return h_new


class LSTM(Chain):

    def __init__(self, in_size, hidden_size):
        super().__init__()

        I, H = in_size, hidden_size
        with self.init_scope():
            self.x2f = Linear(I, H)
            self.x2i = Linear(I, H)
            self.x2o = Linear(I, H)
            self.x2u = Linear(I, H)
            self.h2f = Linear(H, H, nobias=True)
            self.h2i = Linear(H, H, nobias=True)
            self.h2o = Linear(H, H, nobias=True)
            self.h2u = Linear(H, H, nobias=True)

        self.reset_state()

    def reset_state(self):
        self.h = None
        self.c = None

    def __call__(self, x):
        if self.h is None:
            N, D = x.shape
            H, H = self.h2f.W.shape
            self.h = np.zeros((N, H), np.float32)
            self.c = np.zeros((N, H), np.float32)

        f = F.sigmoid(self.x2f(x) + self.h2f(self.h))
        i = F.sigmoid(self.x2i(x) + self.h2i(self.h))
        o = F.sigmoid(self.x2o(x) + self.h2o(self.h))
        u = F.tanh(self.x2u(x) + self.h2u(self.h))

        c = (f * self.c) + (i * u)
        h = o * F.tanh(c)

        self.h, self.c = h, c
        return h


class LSTM2(Chain):

    def __init__(self, in_size, hidden_size):
        super().__init__()

        I, H = in_size, hidden_size
        with self.init_scope():
            self.x2d = Linear(I, 4*H)
            self.h2d = Linear(H, 4*H)

        self.reset_state()

    def reset_state(self):
        self.h = None
        self.c = None

    def __call__(self, x):
        H = self.h2d.W.shape[0]
        if self.h is None:
            N, D = x.shape
            self.h = np.zeros((N, H), np.float32)
            self.c = np.zeros((N, H), np.float32)
        d = self.x2d(x) + self.h2d(self.h)

        f = F.sigmoid(d[:,:H])
        i = F.sigmoid(d[:,H:2*H])
        o = F.sigmoid(d[:,2*H:3*H])
        u = F.tanh(d[:,3*H:])

        c = (f * self.c) + (i * u)
        h = o * F.tanh(c)

        self.h, self.c = h, c
        return h