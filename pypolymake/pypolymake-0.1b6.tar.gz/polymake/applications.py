#from polymake.main import pm_set_application, functions_in_current_application, arguments

class PolymakeFunctionWrapper(object):
    def __init__(self, app, name):
        if isinstance(app, str):
            app = app.encode('ascii')
        if isinstance(name, str):
            name = name.encode('ascii')
        self._app = app
        self._name = name
        self._args = arguments(self._name)
    def __repr__(self):
        s = "Function {}::{}\n".format(self._app.decode(), self._name.decode())
        args = []
        for arg in self._args:
            args.append("  " + ", ".join(v.decode() + ":" + typ.decode() for (v,typ) in arg))
        return s + "\n".join(args)

    def __call__(self, *args, **kwds):
        raise ValueError

class PolymakeApplication(object):
    def __init__(self, name):
        self._name = name.encode('ascii')
        self._populate_functions()
    def __repr__(self):
        print("Application {}".format(self._name))
    def _populate_functions(self):
        # TODO: this is broken for now...
        return
        pm_set_application(self._name)
        for f in functions_in_current_application():
            try:
                self.__setattr__( f, PolymakeFunctionWrapper(self._name, f))
            except RuntimeError as err:
                print("impossible for now to set {}".format(f))

common   = PolymakeApplication("common")
fulton   = PolymakeApplication("fulton")
group    = PolymakeApplication("group")
matroid  = PolymakeApplication("matroid")
topaz    = PolymakeApplication("topaz")
fan      = PolymakeApplication("fan")
graph    = PolymakeApplication("graph")
ideal    = PolymakeApplication("ideal")
polytope = PolymakeApplication("polytope")
tropical = PolymakeApplication("tropical")

