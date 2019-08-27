import logging
import os
import sys
import argparse
import yaml
from typing import Dict

from .variable import Variable


class Config:
    class __Config:
        def __init__(self):
            # variables maps the "path" of a variable to an instance of class Variable
            self.variables = {}
            self.namespace = ""
            self.parser = argparse.ArgumentParser(description='Arguments')
            self.parser.add_argument("-c", type=str, default="", help="relative path to config file")

        def define_var(self, name, default, description, type, is_list=False, possible_values=None):
            if self.namespace:
                name = self.namespace + "." + name
            name = name.lower()
            variable = Variable(name, default, description, type, is_list, possible_values)
            self.__add_variables(variable)

            if possible_values is not None:
                self.parser.add_argument("--" + variable.name, type=type, help=f"{variable.description}, need to be in {possible_values}")
            else:
                # Bool is a special case : we want to use str to specify the value. 
                if type == bool:
                    type = str
                self.parser.add_argument("--" + variable.name, type=type, help=variable.description)

        def __add_variables(self, variable: Variable):
            """add variable to variables dict and create path corresponding with the variable name. 

            Args:
                variable (Variable): variable to add
            """
            splited_path = variable.name.split(".")
            variables_sub_group = self.variables
            for sub_path in splited_path[:-1]:
                if not sub_path in variables_sub_group:
                    variables_sub_group[sub_path] = {}
                variables_sub_group = variables_sub_group[sub_path]
            if splited_path[-1] not in variables_sub_group:
                variables_sub_group[splited_path[-1]] = variable
            else:
                raise KeyError("variable already defined")

        def convert_to_dict(self):
            return self._convert_to_dict(self.variables)

        @classmethod
        def _convert_to_dict(cls, variables):
            out_dict = {}
            for key in variables:
                if type(variables[key]) == Variable:
                    out_dict[key] = variables[key].get_value()
                else:
                    out_dict[key] = cls._convert_to_dict(variables[key])
            return out_dict

    __instance = None

    def __init__(self):
        if not Config.__instance:
            Config.__instance = Config.__Config()

    @classmethod
    def clear(cls):
        cls.__instance = Config.__Config()

    @classmethod
    def _set_namespace(cls, name):
        cls.__instance.namespace = name

    @classmethod
    def define_int(cls, var_name, default, description):
        cls.__instance.define_var(var_name, default, description, int)

    @classmethod
    def define_float(cls, var_name, default, description):
        cls.__instance.define_var(var_name, default, description, float)

    @classmethod
    def define_str(cls, var_name, default, description):
        cls.__instance.define_var(var_name, default, description, str)

    @classmethod
    def define_str_list(cls, var_name, default, description):
        cls.__instance.define_var(var_name, default, description, str, is_list=True)

    @classmethod
    def define_int_list(cls, var_name, default, description):
        cls.__instance.define_var(var_name, default, description, int, is_list=True)

    @classmethod
    def define_float_list(cls, var_name, default, description):
        cls.__instance.define_var(var_name, default, description, float, is_list=True)

    @classmethod
    def define_bool(cls, var_name, default, description):
        cls.__instance.define_var(var_name, default, description, bool)

    @classmethod
    def define_enum(cls, var_name, default, possible_values, desciption):
        cls.__instance.define_var(var_name, default, desciption, str, possible_values=possible_values)

    @classmethod
    def get_var(cls, name):
        path = name.split(".")
        variables = cls.__instance.variables
        for sub_path in path:
            variables = variables[sub_path.lower()]

        if type(variables) == Variable:
            return variables.get_value()
        else:
            return variables

    @classmethod
    def set_var(cls, name, val):
        path = name.split(".")
        variables = cls.__instance.variables
        for sub_path in path:
            variables = variables[sub_path]

        assert type(variables) == Variable
        variables.set_value(val)

    @classmethod
    def get_dict(cls):
        return cls.__instance.convert_to_dict()

    @classmethod
    def write_conf(cls, file_path):
        with open(file_path, "w") as f:
            yaml.dump(cls.get_dict(), f, default_flow_style=False)

    @classmethod
    def load_conf(cls, config_file_name="config.yml", auto_update_yml=True, no_conf_file=False):
        """This method load the conf in 3 steps:
        1. Load the config.yml file if exist, or load a file specified by -c option when starting the program
        2. Load the env variables 
        3. parse the python commande line

        Args:
            config_file_name: default name of the config file. can by overwitten by -c option
            auto_update_yml: If true then add in the yml new vars

        """
        args = cls.__instance.parser.parse_args()

        if args.c:
            config_file_name = args.c
        if not no_conf_file:
            if not os.path.exists(config_file_name):
                logging.info(f"Create config file {config_file_name} with default value")
                cls.write_conf(config_file_name)
                logging.info("Please update config file and restart")
                logging.info("You can find information on all parameters by running with --help")

        # 1
        if not no_conf_file:
            with open(config_file_name, 'r') as stream:
                yml_content = yaml.safe_load(stream)
            cls.load_dict(yml_content, cls.__instance.variables)

            if auto_update_yml:
                cls.write_conf(config_file_name)

        # 2
        for var in os.environ:
            path = ".".join(var.lower().split("__"))
            try:
                cls.set_var(path, os.environ[var])
                logging.info(f"Load env variable {var}={os.environ[var]}")
            except KeyError:
                pass

        # 3
        for key in vars(args):
            if key == "c" or vars(args)[key] is None:
                continue

            # # Special case for store_true and store_false
            # if cls.get_var(key).type == bool:


            cls.set_var(key, vars(args)[key])
            logging.info(f"Load variable {key} = {vars(args)[key]} from command line args")

    @staticmethod
    def load_dict(loading_dict, variables):
        for key in loading_dict:
            if type(loading_dict[key]) == dict:
                Config.load_dict(loading_dict[key], variables[key])
            else:
                variables[key].set_value(loading_dict[key])

    @classmethod
    def _append_namespace(cls, name):
        if cls.__instance.namespace == "":
            cls._set_namespace(name)
        else:
            cls._set_namespace(cls.__instance.namespace + "." + name)

    @classmethod
    def _pop_namespace(cls):
        cls._set_namespace(".".join(cls.__instance.namespace.split(".")[:-1]))

    @classmethod
    def namespace(cls, name):
        class _ConfigNamespace:
            def __init__(self, name):
                cls._append_namespace(name)

            def __enter__(self):
                return self

            def __exit__(self, type, value, traceback):
                cls._pop_namespace()

        return _ConfigNamespace(name)


Config()
