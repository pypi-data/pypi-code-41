import os
import subprocess


def get_module_cmd():
    try:
        modules_home = os.environ.get('MODULESHOME')
        if modules_home:
            modules_path = os.path.join(modules_home, 'init/python.py')
            if os.path.exists(modules_path):
                modules = {}
                execfile(modules_path, modules)
                try:
                    return modules['module']
                except KeyError as e:
                    raise EnvModulesError(e)
            else:
                raise EnvModulesError("No python script %s" % modules_path)
        else:
            raise EnvModulesError(
                "No MODULESHOME variable found in the environment")
    except EnvModulesError as e:
        raise


def module_avail(module=None, modulepath=None):
    modulepath_cmd = 'module use %s' % modulepath
    command = 'module avail'
    if module:
        command = '%s %s' % (command, module)
    if modulepath is not None:
        modulepath_cmd = 'module use %s' % modulepath
        command = '%s && %s' % (modulepath_cmd, command)
    call_proc = subprocess.Popen(command, shell=True,
                                 stderr=subprocess.PIPE)
    while True:
        try:
            yield next(call_proc.stderr).decode('utf-8')
        except StopIteration:
            break


def program_string(program_dict):
    return '%s/%s' % (program_dict['path'], program_dict['version'])


class EnvModulesError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)
