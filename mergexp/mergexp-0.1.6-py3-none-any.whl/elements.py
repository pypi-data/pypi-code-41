import uuid

class Op():
    EQ = '='
    LT = '<'
    LE = '<='
    GT = '>'
    GE = '>='
    CHOICE = '?'
    SELECT = '[]'

class ConstraintGenerator():
    def __init__(self, name):
        self.name = name

    def __lt__(self, spec):
        return Constraint(self.name, value=spec, op=Op.LT)

    def __le__(self, spec):
        return Constraint(self.name, value=spec, op=Op.LE)

    def __eq__(self, spec):
        return Constraint(self.name, value=spec, op=Op.EQ)

    def __ne__(self, spec):
        return Constraint(self.name, value=spec, op=Op.NE)

    def __gt__(self, spec):
        return Constraint(self.name, value=spec, op=Op.GT)

    def __ge__(self, spec):
        return Constraint(self.name, value=spec, op=Op.GE)

class Constraint():
    def __init__(self, name, value=None, op=None):
        self.name = name
        self.value = value
        self.op = op

    def xir(self):
        return {
            'value__': self.value,
            'constraint__': self.op
        }

__xp = {}
def experiment(topo):
    global __xp
    __xp['topo'] = topo


class Topology():
    """A topology contains devices interconnected by networks. Topologies must
    be given a name.
    """
    def __init__(self, name, devices=[], nets=[]):
        self.name = name
        self.devices = devices
        self.nets = nets
        self.topos = []

    def connect(self, nodes, *args):

        endpoints = []
        for x in nodes:
            if isinstance(x, str):
                n = self.__getitem__(x)
                if n is None:
                    continue
                endpoints.append(n.endpoint())
            else:
                endpoints.append(x.endpoint())

        #endpoints = [x.endpoint() for x in nodes]
        net = Network(endpoints, *args)
        self.nets.append(net)
        return net

    def device(self, name, *args):
        d = Device(name, *args)
        self.devices.append(d)
        return d

    def xir(self):
        return {
            'id': self.name,
            'nodes': list(map(lambda x: x.xir(), self.devices)),
            'links': list(map(lambda x: x.xir(), self.nets)),
            'nets': list(map(lambda x: x.xir(), self.nets)),
            'props': { 'name': self.name }
        }

    def __getitem__(self, key):

        if isinstance(key, str):
            for x in self.devices:
                if x.name == key:
                    return x
            return None

        if isinstance(key, tuple):
            res = []
            for x in self.devices:
                if x.name in key:
                    res.append(x)
            return res

        return None



class Device():
    def __init__(self, name, *args):
        self.name = name
        self.spec = args
        self.endpoints = []
        self.props = {}

    def endpoint(self):
        e = Endpoint()
        e.device = self
        self.endpoints.append(e)
        return e

    def xir(self):
        for x in self.spec:
            self.props[x.name] = x.xir()
        return {
            'id': self.name,
            'endpoints': [x.xir() for x in self.endpoints],
            'props': self.props,
            #'props': {x.name: x.xir() for x in  self.spec},
        }

class IP():
    def __init__(self):
        self.addrs = []
        self.mtu = 1500

    def xir(self):
        return { 'addrs': self.addrs, 'mtu': self.mtu }

class Endpoint():
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.props = {}
        self.ip = IP()
        self.device = None

    def xir(self):
        self.props['ip'] = self.ip.xir()
        return { 'id': self.id, 'props': self.props }

class Network():

    def __init__(self, endpoints, *args):
        self.name = str(uuid.uuid4())
        self.endpoints = endpoints
        self.spec = args
        self.props = {}

    def endpoint(self, x):
        return self[x]

    def __getitem__(self, x):

        if isinstance(x, Device):
            for e in self.endpoints:
                if e.device == x:
                    return e
            raise IndexError()

        raise TypeError()

    def xir(self):
        for x in self.spec:
            self.props[x.name] = x.xir()
        return {
            'id': self.name,
            'endpoints': [ x.xir()  for x in self.endpoints],
            'props': self.props,
        }

