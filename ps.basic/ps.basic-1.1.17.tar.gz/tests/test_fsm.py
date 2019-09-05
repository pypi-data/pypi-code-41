from unittest import TestCase
import os, sys
from ps.Basic import Basic, DEV_STAGES, hms_string, ps_shell, template_writer, EXEC,  get_html_string
from ps.fsm import FiniteStateMachine, State, get_graph, TransitionError, StateError, FSMError

class TestFSM(TestCase):
    def setUp(self):
        """This method is run once before _each_ test method is executed"""
        if os.getenv("DEV_STAGE", False):           del os.environ["DEV_STAGE"]
        if os.getenv("BASIC_CONFIGFILE_DIR", False): del os.environ["BASIC_CONFIGFILE_DIR"]
        self.my_fsm = FiniteStateMachine('TEST_FSM')

    def tearDown(self):
        """This method is run once after _each_ test method is executed"""
        del(self.my_fsm)
 
    def test_create_a_fsm(self):
     assert(self.my_fsm.name == "TEST_FSM")
     assert(len(self.my_fsm.error_states) == 0)
     assert(len(self.my_fsm.final_states) == 0)
     assert(len(self.my_fsm.inputs) == 0)
     assert(len(self.my_fsm.states) == 0)
     assert(self.my_fsm.init_state == None)
     assert(self.my_fsm.current_state == None)

    def test_that_an_transition_on_an_faulty_fsm_raises_transition_error(self):
      with self.assertRaises(TransitionError) as context:
        self.my_fsm.transition("ANY")

       
    def test_that_an_impossible_transition_raises_transition_error(self):
      start  = State('START',  initial=True )
      self.my_fsm.reset()  #current state becomes init state
      with self.assertRaises(TransitionError) as context:
        self.my_fsm.transition("ANY")

    def test_that_an_impossible_state_raises_state_error(self):
      start  = State('START',  initial=True )
      self.my_fsm.reset()  #current state becomes init state
      with self.assertRaises(StateError) as context:
        start["input"]=None

    def test_that_all_transition_is_ok(self):
      start  = State('START',  initial=True )
      fin    = State('FIN',  final=True )
      start["input"]=fin
      start["input2"]=fin
      #self.my_fsm.reset()  #current state becomes init state
      l=self.my_fsm.all_transitions
      assert(len(l) == 2)
     
    def test_simple_transition(self):
      start  = State('START',  initial=True )
      fin    = State('FIN',  final=True )
      start["input"]=fin
      start["input2"]=fin
      self.my_fsm.reset()  #current state becomes init state
      self.my_fsm.transition("input")
      assert(self.my_fsm.current_state == fin)

    def test_simple_process(self):
      start  = State('START',  initial=True )
      middle = State('MIDDLE')
      fin    = State('FIN',  final=True )
      start["input"]=middle
      middle["input2"]=fin
      self.my_fsm.reset()  #current state becomes init state
      self.my_fsm.process(["input","input2"])
      assert(self.my_fsm.current_state == fin)

    def test_simple_run(self):
      context={}
      def fu(state,context):
       context[state.name]="visited"
       if state.name == "START":  return "input" 
       if state.name == "MIDDLE": return "input2" 
       if state.name == "FIN":    return "ii" 
      start  = State('START' ,  compute_function=fu, initial=True )
      middle = State('MIDDLE',  compute_function=fu)
      fin    = State('FIN'   ,  compute_function=fu, final=True )
      start["input"]=middle
      middle["input2"]=fin
      self.my_fsm.reset()  #current state becomes init state
      self.my_fsm.run(context)
      assert(self.my_fsm.current_state == fin)
      assert("START" in context.keys())
      assert("MIDDLE" in context.keys())
      assert("FIN" in context.keys())
      assert("input" in self.my_fsm.inputs)
      assert("input2" in self.my_fsm.inputs)
      assert("ii" in self.my_fsm.inputs)
      #assert("input2" in self.my_fsm.inputs)

 
