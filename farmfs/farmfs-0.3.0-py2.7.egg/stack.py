# Stack implementation using state monad.
from farmfs.monad import State, runState, bind, then

empty = []

pop = State(lambda xs: (xs[0], xs[1:]))

def push(a):
  return State(lambda xs: (None, [a]+xs))

tos = State(lambda xs: (xs[0], xs))

#Implementation of a stack machine using state monad.
def binaryOp(f):
  return bind(pop, lambda a:
          bind(pop, lambda b:
              push(f(a,b))))
add = binaryOp(lambda x, y: x+y)
sub = binaryOp(lambda x, y: x-y)
mul = binaryOp(lambda x, y: x*y)
div = binaryOp(lambda x, y: x/y)
mod = binaryOp(lambda x, y: x%y)

def unaryOp(f):
  return bind(pop, lambda a:
          push(f(a)))

inc = unaryOp(lambda x: x+1)
double = unaryOp(lambda x: x*2)

def branchif(condition, left, right):
  return State( \
          lambda s: runState(left,s) \
          if condition(s) \
          else runState(right,s))

jmp_reg = None
def set_jmp(target):
  def setter(s):
    print "Setting jmp to", target
    global jmp_reg
    jmp_reg = target
    return (None, s)
  return State(setter)

def long_jmp():
  return State(lambda s: runState(jmp_reg,s))

#Implementation of factorial in stack machine language.
mulall = branchif(lambda s: len(s) == 1, tos, then(mul, long_jmp()))

rollall = branchif(
    lambda s: s[0] != 1,
    bind(tos, lambda top:
      then(
        push(top-1),
        long_jmp())),
    tos)
factorial = \
    then(set_jmp(rollall),
        then(rollall,
          then(set_jmp(mulall),
            mulall)))
