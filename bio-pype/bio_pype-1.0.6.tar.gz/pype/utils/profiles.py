import os
import yaml
from pype.misc import package_files
from pype.env_modules import module_avail, program_string
from pype import __config__

PYPE_PROFILES = __config__.PYPE_PROFILES


def check_profile_files(profile):
    check_dict = dict()
    for key in profile.files:
        resource = profile.files[key]
        if os.path.isfile(resource):
            check_dict[key] = True
        elif os.path.isdir(resource):
            check_dict[key] = True
        else:
            check_dict[key] = False
    return check_dict


def check_programs_env_module(profile):
    check_dict = dict()
    for key in profile.programs:
        resource = profile.programs[key]
        mod_string = program_string(resource)
        try:
            modulepath = resource['modulepath']
        except KeyError:
            modulepath = None
        res_avail = module_avail(resource['path'], modulepath)
        check_dict[key] = False
        for line in res_avail:
            if mod_string in line:
                check_dict[key] = True
    return check_dict


def check_programs_path(profile):
    check_dict = dict()
    for key in profile.programs:
        resource = profile.programs[key]
        res = check_program(resource['path'])
        check_dict[key] = res['is_file']
    return check_dict


def check_program(path):
    is_file = False
    is_exec = False
    fpath, fname = os.path.split(path)
    if fpath:
        if os.path.isfile(path):
            is_file = True
            if os.access(path, os.X_OK):
                is_exec = True
    else:
        for basedir in os.environ["PATH"].split(os.pathsep):
            basedir = basedir.strip('"')
            exe_file = os.path.join(basedir, path)
            if os.path.isfile(exe_file):
                is_file = True
                if os.access(exe_file, os.X_OK):
                    is_exec = True
    return {'is_file': is_file, 'is_exec': is_exec}


def print_checks(check, profile_dict, env_module=False):
    greencol = '\033[92m'
    redcol = '\033[91m'
    endcol = '\033[0m'
    failed = dict()
    for key in check:
        try:
            if env_module:
                path = program_string(profile_dict[key])
            else:
                path = profile_dict[key]['path']
            type_check = 'Program'
        except TypeError:
            path = profile_dict[key]
            type_check = 'File'
        if check[key] is True:
            print('%s%s OK%s - %s path: %s' % (greencol, type_check,
                                               endcol, key, path))
        else:
            failed[key] = {'path': path, 'type': type_check}
    for key in failed:
        print('%s%s ERROR%s - %s path: %s' % (redcol, failed[key]['type'],
                                              endcol, key,
                                              failed[key]['path']))


def get_profiles(profs):
    profiles = package_files(PYPE_PROFILES, '.yaml')
    for profile in sorted(profiles):
        try:
            prof_name = os.path.basename(os.path.splitext(profile)[0])
            profs[prof_name] = Profile(profile, prof_name)
        except AttributeError:
            pass
    return profs


class Profile:

    def __init__(self, path, name):
        self.__path__ = path
        self.__name__ = name
        with open(self.__path__, 'rb') as file:
            profile = yaml.safe_load(file)
            for key in profile:
                setattr(self, key, profile[key])

    def describe(self):
        print("Name       : %s" % self.__name__)
        print("Description: %s" % self.info["description"])
        print("Date       : %s" % self.info["date"])
        print("Files      :")
        for file in self.files:
            print("\tID: %s" % file)
            print("\t\tpath: %s" % self.files[file])
        print("Programs   :")
        for program in self.programs:
            print("\tID: %s" % program)
            print("\t\tname: %s" % self.programs[program]['path'])
            print("\t\tversion: %s" % self.programs[program]['version'])
        print("File Path  : %s" % self.__path__)
