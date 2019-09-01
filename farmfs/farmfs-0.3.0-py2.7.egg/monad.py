class State:
  # runState :: s->(a,s)
  def __init__(self, runState):
    self.runState = runState
  def bind(self, k):
    def binder(s):
      (a, nxt) = self.runState(s)
      return runState(k(a), nxt)
    return State(binder)
# return a -> State a
  @staticmethod
  def _return(a):
    return State(lambda s: (a, s))


# runState :: State s a -> s -> (a, s)
def runState(state, s):
  return state.runState(s)

# evalState :: State s a -> s -> a
def evalState(state, s):
  return runState(state, s)[0]

# execState :: State s a -> s -> s
def execState(state, s):
  return runState(state, s)[1]

#(>>=) :: Monad m => m a -> (a -> m b) -> m b
def bind(m_a, k):
  return m_a.bind(k)

# (>>) :: Monad m => m a -> m b -> m b
# m >> k =  m >>= \_ -> k
def then(m, k):
  return bind(m, lambda unused: k)

# get :: State s s
get = State(lambda s: (s,s))

# gets :: MonadState s m => (s -> a) -> m a
# get >>= return (\x->x+1)
def gets(f):
  return bind(get, lambda s: get._return(f(s)))

# put :: s -> State s ()
# put s = State $ \_ -> ((), s)
def put(s):
  return State(lambda unused: (None, s))

# modify :: (s -> s) -> State s ()
# modify f = get >>= \x -> put (f x)
def modify(f):
 return bind(get, lambda x: put(f(x)))

class Maybe:
  def __init__(self, value):
    self.value = value
  def bind(self, k):
    if self.value is None:
      return Maybe(None)
    else:
      return k(self.value)
# return a -> State a
  @staticmethod
  def _return(a):
    return Maybe(a)

def Just(a):
  return Maybe(a)

def Nothing():
  return Maybe(None)

# maybe :: b -> (a -> b) -> Maybe a -> b
def maybe(b, f, m_a):
  if m_a.value is None:
    return b
  else:
    return f(m_a.value)

# liftM :: Monad m => (a1 -> r) -> m a1 -> m r
def liftM(f):
  def lifter(m_a1):
    return bind(m_a1, lambda a1: m_a1._return(f(a1)))
  return lifter

# <$!> :: Monad m => (a -> b) -> m a -> m b
fmapM = liftM

# >=> :: Monad m => (a -> m b) -> (b -> m c) -> a -> m c
def fish(f, g):
  def fishy(a):
    m_b = f(a)
    m_c = bind(m_b, lambda b: g(b))
    return m_c
  return fishy

