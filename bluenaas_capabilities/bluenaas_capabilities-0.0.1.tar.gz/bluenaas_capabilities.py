import os
import json
import collections
import sciunit
import tornado.ioloop
import tornado.web
import tornado.websocket
from neuron import h

def flatten_dict(d, parent_key='', sep='__'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def unflatten_dict(d, sep='__'):
    resultDict = dict()
    for key, value in d.iteritems():
        parts = key.split(sep)
        d = resultDict
        for part in parts[:-1]:
            if part not in d:
                d[part] = dict()
            d = d[part]
        d[parts[-1]] = value
    return resultDict

class BlueNaaS_Python_Model(sciunit.Capability):

    def get_model_path(self):
        raise NotImplementedError()

    def get_default_parameters(self):
        raise NotImplementedError()

    def get_recorded_vectors(self):
        raise NotImplementedError()

    def get_socket_port(self):
        raise NotImplementedError()

    def initialize(self):
        sciunit.Model.__init__(self)

        model_path, mod_files_path = self.get_model_path()
        if not model_path:
            raise ValueError("Please specify the path to the model's file!")

        self.model_path = os.path.abspath(model_path)
        if mod_files_path:
            self.mod_files_path = os.path.abspath(mod_files_path)
        else:
            self.mod_files_path = os.path.abspath(os.path.dirname(self.model_path))
        self.lib_path = "x86_64/.libs/libnrnmech.so.0" # path to mechanisms once compiled; change if required
        self.compile_load_mod_files()
        global_env = globals()
        local_env = {}
        exec(open(self.model_path).read(), global_env, local_env)
        for key, value in global_env.items():
            setattr(self, key, value)
        for key, value in local_env.items():
            setattr(self, key, value)

        parameters = self.get_default_parameters()
        if parameters:
            self.default_parameters = parameters
        self.apply_parameters(self.default_parameters)

    def compile_load_mod_files(self):
        if not os.path.isfile(os.path.join(self.mod_files_path, self.lib_path)):
            os.system("cd " + self.mod_files_path + "; nrnivmodl")
            h.nrn_load_dll(str(os.path.join(self.mod_files_path, self.lib_path)))

    def evaluate_dict(self, current_ref, d, func_calls):
        for param, param_value in d.items():
            if param == "FUNCTIONS":
                for f_call in (param_value if isinstance(param_value, list) else [param_value]):
                    ind = f_call.find("(")
                    f_call_name = f_call[:ind]
                    f_call_args = f_call[ind:]
                    func_calls.append([getattr(current_ref, f_call_name), f_call_args])
            elif isinstance(param_value, dict):
                if "[" in param:  # to handle arrays/lists
                    ind = param.find("[")
                    param_name = param[:ind]
                    param_index = param[ind:]
                    exec("ref = getattr(current_ref, '{}'){}".format(param_name, param_index))
                else:
                    ref = getattr(current_ref, param)
                self.evaluate_dict(ref, param_value, func_calls)
            else:
                setattr(current_ref, param, param_value)

    def apply_parameters(self, parameters=None):
        if not parameters:
            parameters = self.default_parameters
        func_calls = []
        for key, value in parameters.items():
            if isinstance(value, dict):
                self.evaluate_dict(self, {key:value}, func_calls)
            else:
                setattr(h, key, value)
        if func_calls:
            for f_call in func_calls:
                eval("f_call[0]{}".format(f_call[1]))

    def get_data(self):
        recorded_vectors = self.get_recorded_vectors()
        # find time vector
        time_vector = None
        for vector in recorded_vectors:
            for key, val in vector.items():
                if val.lower() == "time":
                    time_vector = getattr(self, key)
                    recorded_vectors = [item for item in recorded_vectors if item.keys()[0] != key]
                    break
        if time_vector == None:
            raise ValueError("Recorded time vector has not been specified!")

        data = []
        for vector in recorded_vectors:
            for key, val in vector.items():
                if "[" in key:  # to handle arrays/lists
                    ind = key.find("[")
                    vector_name = key[:ind]
                    vector_index = key[ind:]
                    exec("ref = getattr(self, '{}'){}".format(vector_name, vector_index))
                else:
                    ref = getattr(self, key)
                vector_values = ref.to_python()
                if (len(vector_values) == 1) or (len(vector_values) == 2 and vector_values[0]==vector_values[1]):
                    vector_values = [vector_values[0]] * len(time_vector)
                data_item = {'x':time_vector.to_python(),
                             'y':vector_values,
                             'mode':'lines', 'name':val}
                data.append(data_item)
        return data

    def setup_socket(self, update_dt=None):
        port_number = self.get_socket_port()
        if not port_number:
            raise ValueError("Please specify a port number for web socket!")
        self.port = port_number
        self.app = tornado.web.Application([
            (r'/socket', WebSocketHandler, {'model':self, 'update_dt':update_dt}),
            (r"/(.*)", tornado.web.StaticFileHandler, {"path":r"www/"})
            ])
        self.app.listen(self.port)
        tornado.ioloop.IOLoop.instance().start()


class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        print("indexhandler::get")
        self.render('index.html')


class WebSocketHandler(tornado.websocket.WebSocketHandler):

    clients = {}
    client_count = 0
    update_dt = None # ms

    def initialize(self, model, update_dt=None):
        self.model = model
        WebSocketHandler.update_dt = update_dt

    def do_setfields(self, parameters):
        self.model.apply_parameters(unflatten_dict(parameters))
        # flatten `parameters` json as HTML/JS don't use nested hierarchy
        flattened_parameters = flatten_dict(parameters)
        flattened_parameters.pop('FUNCTIONS', None)
        self.send_message_to_all({'command': 'setfields', 'data': flattened_parameters})

    def open(self, *args):
        WebSocketHandler.client_count += 1
        print("websockethandler::open")
        self.id = WebSocketHandler.client_count
        WebSocketHandler.clients[self.id] = self
        self.do_setfields(self.model.default_parameters)

    def on_message(self, message):
        message = json.loads(message)
        command = message['command']
        if command == 'setfields':
            parameters = message.get("parameters", {})
            self.do_setfields(parameters)
        elif command == 'run_simulation':
            if "parameters" in message.keys():
                self.do_setfields(message["parameters"])
            h.init()
            h.finitialize(h.v_init)
            flag = True if h.t + h.dt < h.tstop else False
            while flag:
                flag = True if h.t + h.dt < h.tstop and WebSocketHandler.update_dt else False
                h.continuerun(min(h.tstop, h.t + (WebSocketHandler.update_dt if WebSocketHandler.update_dt else h.tstop)))
                sim_output = self.model.get_data()
                self.send_message_to_all({'command': 'setgraph', 'data': sim_output})
        else:
            print("message received")
            print(message)

    def on_close(self):
        print("websockethandler::on_close")
        if self.id in WebSocketHandler.clients:
            # remove client from the "list" of clients to notify on change
            del WebSocketHandler.clients[self.id]

    def send_message(self, message):
        self.write_message(json.dumps(message))

    def send_message_to_all(self, message):
        for client in WebSocketHandler.clients.values():
            client.send_message(message)
