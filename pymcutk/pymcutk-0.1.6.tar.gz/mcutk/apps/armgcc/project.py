import os
import re
import glob

from mcutk.apps.projectbase import ProjectBase
from mcutk.exceptions import ProjectNotFound

class Project(ProjectBase):
    """
    ARMGCC project object

    This class could parser the settings in CMakeLists.txt & build_all.sh.
    Parameters:
        prjpath: path of CMakeLists.txt

    """

    PROJECT_EXTENSION = 'CMakeLists.txt'

    @classmethod
    def frompath(cls, path):
        """Return a project instance from a given file path or directory.

        If path is a directory, it will search the project file and return an instance.
        Else this will raise mcutk.apps.exceptions.ProjectNotFound.
        """

        if os.path.isfile(path):
            return cls(path)

        if glob.glob(path + "/CMakeLists.txt") and glob.glob(path + "/build_all.*"):
            return cls(path + "/CMakeLists.txt")

        raise ProjectNotFound("Not found armgcc project in path: %s"%path)



    def __init__(self, prjpath, *args, **kwargs):
        super(Project, self).__init__(prjpath, *args, **kwargs)
        self._appname = None
        self._conf = self._get_all_configuration()
        self._targets = self._conf.keys()
        self.armgcc_cmake = self.__get_armgcc_cmake()



    @property
    def name(self):
        """Return the application name

        Returns:
            string --- app name
        """
        return self._appname




    def _get_all_configuration(self):
        """Parse settings from CMakeLists.txt.

        Returns:
            dict -- targets configuration
        """
        targets = dict()

        with open(self.prjpath, 'r') as fh:
            content = fh.read()

        # extract output name
        output_keywords = [
            r'add_library\(.+(\.)?\w+',
            r'add_executable\(.+(\.)?\w+',
            r'set_target_properties\(\w+(\.)?\w+',
            r'TARGET_LINK_LIBRARIES'
        ]

        excutable = None
        for kw in output_keywords:
            s = re.compile(kw).search(content)
            if s != None:
                excutable = s.group(0).split('(')[1].strip()
                break
        else:
            raise ValueError("Unable to detect output definition in CMakeLists.txt. [%s]"%self.prjpath)
        self._appname = excutable.split('.')[0]

        # extract build types
        for m in re.findall("CMAKE_C_FLAGS_\w+ ", content):
            tname = m.replace('CMAKE_C_FLAGS_', '').lower().strip()
            if tname not in targets:
                targets[tname] = "{}/{}".format(tname, excutable)

        return targets




    def __get_armgcc_cmake(self):
        try:
            script_file = glob.glob(os.path.dirname(self.prjpath) + "/build_all.*")[0]
        except Exception:
            raise IOError("Cannot find build_all.* file,armgcc can not read info from this file!")

        with open(script_file, "r") as fh:
            filecontent = fh.readlines()

        armgcc_cmake = ''
        for line in filecontent:
            if "-DCMAKE_TOOLCHAIN_FILE=" in line:
                armgcc_cmake = line.split("-DCMAKE_TOOLCHAIN_FILE=")[1].split(" ")[0]
                break

        return armgcc_cmake


