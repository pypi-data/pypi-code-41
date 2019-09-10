import datetime
import inspect
import logging
import time


def _elapsed_since(start):
    """ Return a formatted string, e.g. '(HH:MM:SS elapsed)' """
    seconds = time.time() - start
    return "({} elapsed)".format(str(datetime.timedelta(seconds=int(seconds))))


def fstr(fstring_text, locals, globals=None):
    """
    Dynamically evaluate the provided fstring_text

    Sample usage:
        format_str = "{i}*{i}={i*i}"
        i = 2
        fstr(format_str, locals()) # "2*2=4"
        i = 4
        fstr(format_str, locals()) # "4*4=16"
        fstr(format_str, {"i": 12}) # "10*10=100"
    """
    locals = locals or {}
    globals = globals or {}
    ret_val = eval(f'f"{fstring_text}"', locals, globals)
    return ret_val


class logged(object):
    """
    Decorator class for logging function start, completion, and elapsed time.

    Sample usage:
        @logged()
        def my_func_a():
            pass

        @logged(log_fn=logging.debug)
        def my_func_b():
            pass

        @logged("doing a thing")
        def my_func_c():
            pass

        @logged("doing a thing with {foo_obj.name}")
        def my_func_d(foo_obj):
            pass

        @logged("doing a thing with '{custom_kwarg}'", custom_kwarg="foo")
        def my_func_d(foo_obj):
            pass
    """

    def __init__(
        self,
        desc_text="'{desc_detail}' call to {fn.__name__}()",
        desc_detail="",
        start_msg="Beginning {desc_text}...",
        success_msg="Completed {desc_text}  {elapsed}",
        log_fn=logging.info,
        **addl_kwargs,
    ):
        """ All arguments optional """
        self.default_context = addl_kwargs.copy()  # start with addl. args
        self.default_context.update(locals())  # merge all constructor args

    def __call__(self, fn):
        """ Call the decorated function """

        def wrapped_fn(*args, **kwargs):
            """
            The decorated function definition. Note that the log needs access to 
            all passed arguments to the decorator, as well as all of the function's
            native args in a dictionary, even if args are not provided by keyword.
            If start_msg is None or success_msg is None, those log entries are skipped.
            """

            def re_eval(context_dict, context_key: str):
                """ Evaluate the f-string in context_dict[context_key], store back the result """
                context_dict[context_key] = fstr(
                    context_dict[context_key], locals=context_dict
                )

            start = time.time()
            fn_context = self.default_context.copy()
            fn_context["fn"] = fn
            fn_context["elapsed"] = None
            fn_arg_names = inspect.getfullargspec(fn).args
            for x, arg_value in enumerate(args, 0):
                fn_context[fn_arg_names[x]] = arg_value
            fn_context.update(kwargs)
            desc_detail_fn = None
            log_fn = fn_context["log_fn"]
            # If desc_detail is callable, evaluate dynamically (both before and after)
            if callable(fn_context["desc_detail"]):
                desc_detail_fn = fn_context["desc_detail"]
                fn_context["desc_detail"] = desc_detail_fn()

            # Re-evaluate any decorator args which are fstrings
            re_eval(fn_context, "desc_detail")
            re_eval(fn_context, "desc_text")
            # Remove 'desc_detail' if blank or unused
            fn_context["desc_text"] = fn_context["desc_text"].replace("'' ", "")
            re_eval(fn_context, "start_msg")
            if fn_context["start_msg"]:
                log_fn(fn_context["start_msg"])  # log start of execution
            ret_val = fn(*args, **kwargs)
            if desc_detail_fn:
                # If desc_detail callable, then reevaluate
                fn_context["desc_detail"] = desc_detail_fn()
            fn_context["elapsed"] = _elapsed_since(start)
            # log the end of execution
            log_fn(fstr(fn_context["success_msg"], locals=fn_context))
            return ret_val

        return wrapped_fn
