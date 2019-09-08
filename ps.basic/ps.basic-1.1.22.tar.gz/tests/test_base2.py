from unittest import TestCase
import os, sys, pytest,time
from ps.Basic import Basic, DEV_STAGES, hms_string, ps_shell, template_writer, EXEC,  get_html_string
from ps.Basic import send_a_mail

from configparser import ParsingError


class TestBasic(TestCase):
    @classmethod
    def setup_class(klass):
        """This method is run once for each class before any tests are run"""

    @classmethod
    def teardown_class(klass):
        """This method is run once for each class _after_ all tests are run"""
        pass

    def setUp(self):
        """This method is run once before _each_ test method is executed"""
        if os.getenv("DEV_STAGE", False):           del os.environ["DEV_STAGE"]
        if os.getenv("BASIC_CONFIGFILE_DIR", False): del os.environ["BASIC_CONFIGFILE_DIR"]

        fileList = os.listdir(".")
        for f in fileList:
            if "lock" in f:
              os.remove(f)

        # Reset the singleton mechanism to enable tests
        if Basic.INSTANCE: 
             Basic.logger =  "not_yet_defined"
             Basic.log_file_name          = "not_yet_defined"
             del(Basic.INSTANCE)
             Basic.INSTANCE = None
        # pass

    @staticmethod
    def tearDown():
        """This method is run once after _each_ test method is executed"""


    def test_that_an_notfound_config_file_raises_sys_exit_if_usage_of_config_file_is_forced(self):
        for stage in DEV_STAGES:
           os.environ["DEV_STAGE"] = stage
           with pytest.raises(SystemExit) :
              b = Basic.get_instance("Tests_x", force_usage_of_config_file=True)
              assert(False)

    def test_that_an_notfound_config_file_not_raises_sys_exit_if_usage_of_config_file_is_not_forced(self):
        for stage in DEV_STAGES:
           os.environ["DEV_STAGE"] = stage
           b = Basic.get_instance("Tests_x", force_usage_of_config_file=False)
           b.__exit__(1, 2, 3)
           assert(True)

    #def test_that_an_inproper_configured_cfg_file_raises_an_error(self):
    def test_that_an_not_given_herald_url_with_force_usage_of_config_file_raises_an_error(self):
        for stage in DEV_STAGES:
            #with pytest.raises(ParsingError) :
            with pytest.raises(SystemExit) :
               os.environ["DEV_STAGE"] = stage
               fp = open("Tests2" + DEV_STAGES[stage]['suffix'] + ".cfg", "w")
               fp.write("[section]\n")
               fp.write("    name : value  \n")
               b = Basic.get_instance("Tests2", guarded_by_lockfile=True,force_usage_of_config_file=True)
               b.__exit__(1, 2, 3)

