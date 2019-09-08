from unittest import TestCase
import os, sys,pytest
import ps
from ps.Basic import Basic, DEV_STAGES, hms_string, ps_shell, template_writer, EXEC,  get_html_string
from ps.fsm import FiniteStateMachine, State, get_graph, TransitionError, StateError, FSMError, StateComputingFunction, ComputeFunctionTransitionError



@StateComputingFunction(allowed_return_values=["a"])
def x_fu(state,context):
    """ The documentation &#92;n of the function &#92;n """

    context["MY_NAME"]="The x Value"
    return "b" 
@StateComputingFunction(allowed_return_values=["a"])
def y_fu(state,context):
    context["MY_NAME"]="The y Value"
    return "a" 



class TestDecorator(TestCase):

    def setUp(self):
        """This method is run once before _each_ test method is executed"""
        if os.getenv("BASIC_CONFIGFILE_DIR", False): del os.environ["BASIC_CONFIGFILE_DIR"]
        os.environ["DEV_STAGE"]="TESTING"
        # Reset the singleton mechanism to enable tests
        if Basic.INSTANCE:
             del(Basic.INSTANCE)
             Basic.INSTANCE = None

        x=ps.Basic.Basic.get_instance("TEST_FSM")
        self.my_fsm = FiniteStateMachine('TEST_FSM')

    def tearDown(self):
        """This method is run once after _each_ test method is executed"""
        del(self.my_fsm)

    def test_decorator_that_global_function(self):
      x=State("test_state",compute_function=y_fu,initial=True, final=True)
      context=dict()
      self.my_fsm.run(context)
      assert(context["MY_NAME"]=="The y Value")

    def test_decorator_that_global_functionalso_raises_ComputeFunctionTransitionError(self):
      with pytest.raises(ComputeFunctionTransitionError):
        x=State("test_state",compute_function=x_fu,initial=True, final=True)
        context=dict()
        self.my_fsm.run(context)
        assert(context["MY_NAME"]=="The x Value")

    def test_decorator_that_an_unallowed_return_value_raises_ComputeFunctionTransitionError(self):
      @StateComputingFunction(allowed_return_values=["a"])
      def x_fu(state,context):
         context["MY_NAME"]="The Value"
         return "b" 

      with pytest.raises(ComputeFunctionTransitionError):
        x=State("test_state",compute_function=x_fu,initial=True, final=True)
        context=dict()
        self.my_fsm.run(context)
        assert(context["MY_NAME"]=="The Value")

    def test_decorator_that_context_is_written(self):
      @StateComputingFunction(allowed_return_values=["a1_str","a2_str"])
      def a_fu(state,context):
         if "a_name" in context.keys(): return "a2_str"
         else: context["a_name"]="visited"
         return "a1_str" 

      @StateComputingFunction(allowed_return_values=["b1_str"])
      def b_fu(state,context): return "b1_str" 

      @StateComputingFunction(allowed_return_values=["fin"])
      def c_fu(state,context): return "fin"

      a=State("A",compute_function=a_fu,initial=True)
      b=State("B",compute_function=b_fu,default=a)
      c=State("C",compute_function=c_fu, final=True)
      a["a1_str"]=b
      b["b1_str"]=a
      a["a2_str"]=c
      #sys.stdout.write("keys are" +  a.keys())
      context=dict()
      self.my_fsm.run(context)
      assert(context["a_name"]=="visited")
   
class TestState(TestCase):
    def setUp(self):
        """This method is run once before _each_ test method is executed"""
        if os.getenv("BASIC_CONFIGFILE_DIR", False): del os.environ["BASIC_CONFIGFILE_DIR"]
        self.my_fsm = FiniteStateMachine('TEST_FSM')

        # pass

   
    def test_state_that_all_transition_keys_are_listed(self):
      x=State("test_state")
      x["A"] = x
      assert("A" in x.keys())
      assert("B" not in x.keys())


class TestGraph(TestCase):
    def setUp(self):
        """This method is run once before _each_ test method is executed"""
        if os.getenv("BASIC_CONFIGFILE_DIR", False): del os.environ["BASIC_CONFIGFILE_DIR"]
        self.my_fsm = FiniteStateMachine('TEST_FSM')

    def test_that_picture_generation_with_unset_init_state_raise_StateError(self):
      with pytest.raises(StateError):
        x=State("X")
        y=State("Y")
        x.compute_function =  x_fu
        y.compute_function =  x_fu
        g=get_graph(self.my_fsm, title="title")      
        for format in ["svg", "png"]:
          g.draw('TEST_FSM.%s' % (format), prog='dot')

    def test_that_we_are_able_to_generate_a_picture(self):
      x=State("X",initial=True)
      y=State("Y")
      x.compute_function =  x_fu
      y.compute_function =  x_fu
      y.mail_addr = '[{"SECTION_IN_CFG_FILE":"VALUE"}]'
      x["A"] = y 
      assert("A" in x.keys())
      assert("B" not in x.keys())
      g=get_graph(self.my_fsm, title="title")      
      for format in ["svg", "png"]:
        g.draw('TEST_FSM.%s' % (format), prog='dot')

      
 
