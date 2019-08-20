from AuditModule.util import Logging as LOGG
import json

# Logger
Logger = LOGG.get_logger()

def fetch_function_stack_frame(function_stack):
    """
    This method fetches the detailed information regarding the function call
    :return: Detailed information about the function call
    """
    try:
        application_context = list(function_stack[1])[1].split("\\")[-1].replace(".py", "")
        service_context = list(function_stack[2])[1].split("\\")[-1].replace(".py", "")
        action = json.dumps(list(function_stack[2])[3])
        Logger.debug("Function Stack frame Data ==> " + json.dumps(list(function_stack[1])[0].f_back.f_locals,
                                                                        default= lambda o: '<not serializable>'))
        data = json.loads(json.dumps(list(function_stack[0])[0].f_back.f_locals,
                                     default=lambda o: '<not serializable>'))
        function_stack_frame_data = {"application_context": application_context,
                                     "service_context": service_context, "action" : action}
        function_stack_frame_data.update(data)
        return function_stack_frame_data
    except Exception as e:
        Logger.error('Error in fetching function stack frame ', str(e))
        raise Exception(str(e))