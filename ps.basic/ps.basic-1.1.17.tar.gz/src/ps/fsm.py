"""

"""

from ps.Basic import Basic , get_html_string
import pprint
import inspect
import sys
from package_version import version


MACHINES = dict()

class FSMError(Exception):
    """Base FSM exception."""
    pass

class TransitionError(FSMError):
    """Transition exception."""
    pass

class StateError(FSMError):
    """State manipulation error."""

class ComputeFunctionTransitionError(FSMError):
    """Transition exception in Compute Function."""

class FiniteStateMachine(object):
    """Generic Finite State Machine.
       The FinitStateMachine provides handler functions (the xxx_fu beyond),
       which will be called on entering a state. The context dictionary 
       (see my_fsm.run...()) ben

       >>> from ps.Basic import Basic
       >>> x = Basic("fsm")
       >>> def error_fu(self,context):  print "error_fu called", self.name
       >>> def fertig_fu(self,context): print "fertig_fu called", self.name
       >>> def start_fu(self,context):  print "start_fu called", self.name
       >>> from ps.fsm import FiniteStateMachine, get_graph, State
       >>> my_fsm = FiniteStateMachine('MY_FSM')
       >>> error  = State('ERROR',               compute_function=error_fu,   error=True, final=True   )
       >>> fertig = State('FERTIG',              compute_function=fertig_fu,  final=True  )
       >>> start  = State('START',               compute_function=start_fu ,  initial=True,    default=error)
       >>> start["WORK"]=fertig
       >>> my_fsm.run(context={})
       start_fu called START
       error_fu called ERROR
       >>> from ps.fsm import get_graph

       ###>>> graph = get_graph(my_fsm)
       ###>>> graph.draw('x.png', prog='dot')
       ###>>> graph.draw('x.svg', prog='dot')
       
    """
    DOT_ATTRS = {
        'directed': True,
        'strict': False,
        'rankdir': 'LR',
        'ratio': '0.3'
    }

    def __init__(self, name ):
        """Construct a FSM."""
        self.name = name
        FiniteStateMachine._setup(self)
        self._setup()
        self.current_state = None
        MACHINES[name] = self
        MACHINES['default'] = MACHINES[name]

    def _setup(self):
        """Setup a FSM."""
        # All finite state machines share the following attributes.
        self.inputs = list()
        self.states = list()
        self.final_states = list()
        self.error_states = list()
        self.init_state = None

    @property
    def all_transitions(self):
        """Get transitions from states.
        
        Returns:
            List of three element tuples each consisting of
            (source state, input, destination state)
        """
        transitions = list()
        for src_state in self.states:
            for input_value, dst_state in src_state.items():
                transitions.append((src_state, input_value, dst_state))
        return transitions
        
    def transition(self, input_value):
        """Transition to the next state."""
        current = self.current_state
        if current is None:
            raise TransitionError('Current state not set.')

        destination_state = current.get(input_value, current.default_transition)
        if destination_state is None: 
            raise TransitionError('Cannot transition from state %r'
                                  ' on input %r.' % (current.name, input_value))
        else:
            self.current_state = destination_state

    def reset(self):
        """Enter the Finite State Machine."""
        self.current_state = self.init_state
        del(self.inputs)
        self.inputs = list() 

    def process(self, input_data):
        """Process input data."""
        self.reset()
        for item in input_data:
            self.transition(item)
    def run(self,context ):
        """Process input data."""
        self.reset()
        current_state = self.init_state
        Basic.logger.debug("FSM: " + self.name + " started in State " + str(current_state), extra={"package_version":version})
        while True:
            my_current_state = self.current_state
            return_value_of_compute_function = my_current_state.compute_function(my_current_state,context)
            Basic.logger.debug(my_current_state.name + "-compute_function returned  " + str(return_value_of_compute_function), extra={"package_version":version}) 
            if isinstance(return_value_of_compute_function,State):
                Basic.logger.debug("%s.run new step: %s's default_handler left context as %s"\
                                  %( self.name, my_current_state.name, get_html_string(context)), extra={"package_version":version})
            else:
                Basic.logger.debug("%s.run new step: %s's compute function left context as %s"\
                                  %( self.name, my_current_state.name, get_html_string(context)), extra={"package_version":version})
            self.inputs.append(return_value_of_compute_function)
            if my_current_state.final == True:
               Basic.logger.debug("Leave run, as " + self.current_state.name + " is a final state ", extra={"package_version":version})
               break
            else:
                self.transition(return_value_of_compute_function)
                Basic.logger.debug("TRANSITION: from State " + my_current_state.name + "<br> ONInput:   '" \
                                   + str(return_value_of_compute_function) + "'<br>To State: " + self.current_state.name \
                                         , extra={"package_version":version})

def default_compute_function(faked_self,context):
                Basic.logger.debug("faked_computing_function called in state " + faked_self.name, extra={"package_version":version}) 
                Basic.logger.debug("context is " + str(context), extra={"package_version":version})
                if faked_self.default_transition == None:
                   raise StateError('A state must either have a default transition \
                                     or an defined compute_function')
                return faked_self.default_transition

class StateComputingFunction(object):
 def __init__(self, allowed_return_values=None ):
       """   """
       self.allowed_return_values = allowed_return_values
 def __call__(self, f):
   """ """
   def wrapped_f(*args):
     ret =  f(*args)
     Basic.logger.debug( "After f(*args), which returned " + str(ret ), extra={"package_version":version})
     if ret not in self.allowed_return_values:
        Basic.logger.error("unallowed return value %s "%(str(ret)) + " allowed are " + str(self.allowed_return_values) \
                           , extra={"package_version":version})
        raise ComputeFunctionTransitionError("return value %s not allowed in state %s"%(str(ret),args[0].name))
     return ret
   return wrapped_f

class State(dict):
    
    """State class."""

    DOT_ATTRS = {
        'shape': 'circle',
        'height': '1.2',
    }
    DOT_FINAL= 'doublecircle'

    def __init__(self, name, initial=False, final=False, error=False, compute_function=None, machine=None, mail_addr = None, default=None):
        """Construct a state."""
        dict.__init__(self)
        self.name                = name
        if compute_function == None: self.compute_function    = default_compute_function
        else:                        self.compute_function    = compute_function
        self.default_transition  = default
        self.final               = final
        self.error               = error
        self.initial             = initial
        self.mail_addr           = mail_addr
        machine = MACHINES['default']
        machine.states.append(self)
        if initial: machine.init_state = self
        if final:   machine.final_states.append(self)
        if error:   machine.error_states.append(self)

    def __getitem__(self, input_value):
        """Make a transition to the next state."""
        next_state = dict.__getitem__(self, input_value)
        return next_state

    def __setitem__(self, input_value, next_state):
        """Set a transition to a new state."""
        if not isinstance(next_state, State):
            raise StateError('A state must transition to another state,'
                             ' got %r instead.' % next_state)
        dict.__setitem__(self, input_value, next_state)

    def __repr__(self):
        """Represent the object in a string."""
        return '<%r %s @ 0x%x>' % (self.name, self.__class__.__name__, id(self))


def get_graph(fsm, title=None):
    """Generate a DOT graph with pygraphviz."""
    try:
        import pygraphviz as pgv
    except ImportError:
        pgv = None    
     

    if   title is None:    title = fsm.name
    elif title is False:   title = ''


    fsm_graph = pgv.AGraph(title=title, size="10.3, 5.3", **fsm.DOT_ATTRS)
    fsm_graph.node_attr.update(State.DOT_ATTRS)

    if fsm.init_state == None:
            raise StateError('A FSM must have a defined init_state')

    for state in [fsm.init_state] + fsm.states:
        color="black"
        shape = State.DOT_ATTRS['shape']
        if hasattr(fsm, 'final_states'):
            if id(state) in [id(s) for s in fsm.final_states]:
                shape = state.DOT_FINAL
        if hasattr(fsm, 'error_states'):
            if id(state) in [id(s) for s in fsm.error_states]:
                color = 'red' 

        try:
            tooltip_str=pprint.pformat(inspect.getdoc(state.compute_function))
        except:
            tooltip_str=None
        if tooltip_str: tooltip = tooltip_str.replace("\\n","&#013;")
        else:           tooltip = "no tooltip"
        fsm_graph.add_node(n=state.name, shape=shape, color=color, tooltip=tooltip)
        if state.mail_addr: 
            l=eval(state.mail_addr)
            for d in l:
                name = d.keys()[0]
                value= d[name]
                fsm_graph.add_node(n="EMAIL_DST"+name+value, label="%s:%s"%(name,value), 
                                   shape="rpromoter", style="filled", 
                                   fillcolor="lightseagreen:orangered",
                                   color = color, tooltip=tooltip)
                fsm_graph.add_edge(state.name, "EMAIL_DST"+ name+value, penwidth=2,
                                   label='send email ', style="dashed", color=color, 
                                    tooltip=tooltip)

    fsm_graph.add_node('null', shape='plaintext', label=' ')
    fsm_graph.add_edge('null', fsm.init_state.name)

    for src, input_value, dst in fsm.all_transitions:
        label = str(input_value)
        fsm_graph.add_edge(src.name, dst.name, label=label)
    for state in fsm.states:
        if state.default_transition is not None:
             if id(state.default_transition) in [id(s) for s in fsm.error_states]:
               fsm_graph.add_edge(state.name, state.default_transition.name, 
                               label='error',color='red',tooltip="werner")
             else:
               fsm_graph.add_edge(state.name, state.default_transition.name, label='else',tooltip="werner")

    return fsm_graph
