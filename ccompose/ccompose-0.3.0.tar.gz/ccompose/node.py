# -*- coding: utf-8 -*-
from jinja2 import Template

# The graph nodes
class Node(object):
    docker_cmd = {
        "service create": Template('docker container create --name {{name}} {{hostname}} {{ports}} {{expose}} {{links}} {{dns}} {{networks}} {{volumes}} {{entrypoint}} {{env}} {{image}} {{command}}'),
        "volume create": Template('docker volume create {{driver}} {{labels}} {{options}} {{name}}'),
        "network create": Template('docker network create {{attachable}} {{driver}} {{name}}'),
        "service remove": Template('docker container rm {{name}}'),
        "volume remove": Template('docker volume rm {{name}}'),
        "network remove": Template('docker network rm {{name}}'),
        "service start": Template('docker start {{name}}'),
        "service stop": Template('docker stop {{name}}'),
        "service build": Template('docker build -f {{build.dockerfile}} -t {{image}} {{build.args}} {{build.context}}'),
        "service inspect": Template("{{inspect.variable}}=`docker inspect -f '{{inspect.what}}' {{inspect.from}}`")
    }

    inspected = {}

    def __init__(self, config, type="service"):
        self.__name = config['name']
        self.__config = config
        self.__build = config.get('build')
        self.__type = type
        self.__depends = set()
        self.__dep_networks = set()
        self.__dep_volumes = set()
        self.__dep_services = set()

    @property
    def config(self):
        return self.__config

    @property
    def build(self):
        return self.__build

    @property
    def type(self):
        return self.__type

    @property
    def name(self):
        return self.__name

    @property
    def dep_services(self):
        return self.__dep_services

    @property
    def dep_volumes(self):
        return self.__dep_volumes

    @property
    def dep_networks(self):
        return self.__dep_networks

    @property
    def depends(self):
        return self.__depends

    @staticmethod
    def makeAnArray( fromValueListOrDict ):
        if isinstance( fromValueListOrDict, list ):
            return fromValueListOrDict
        elif isinstance( fromValueListOrDict, dict ):
            return [k+"="+v for k,v in fromValueListOrDict.items()]
        return [fromValueListOrDict]

    @staticmethod
    def output(operationName, node):
        template = Node.docker_cmd.get(node.type+" "+operationName)
        if template is not None:
            if node.type is 'service' and operationName is 'create':
                output = []
                inspect = node.config.get('inspect')
                if inspect is not None:
                    variable = inspect.get('variable')
                    if variable not in Node.inspected:
                        _template = Node.docker_cmd.get('service inspect')
                        output.append( _template.render(node.config) )
                        Node.inspected[variable] = True
                output.append( template.render(node.config) )
                return output
            elif operationName is 'build' and node.config.get('build') is not None:
                return [template.render(node.config)]
            elif operationName is not 'build':
                return [template.render(node.config)]

    def addDepNetwork(self, nameOrArrayOfNames):
        if nameOrArrayOfNames is not None:
            self.__dep_networks |= set(self.makeAnArray(nameOrArrayOfNames))
            self.__depends |= self.__dep_networks

    def addDepVolume(self, nameOrArrayOfNames):
        if nameOrArrayOfNames is not None:
            self.__dep_volumes |= set(self.makeAnArray(nameOrArrayOfNames))
            self.__depends |= self.__dep_volumes

    def addDepService(self, nameOrArrayOfNames):
        if nameOrArrayOfNames is not None:
            self.__dep_services |= set(self.makeAnArray(nameOrArrayOfNames))
            self.__depends |= self.__dep_services
