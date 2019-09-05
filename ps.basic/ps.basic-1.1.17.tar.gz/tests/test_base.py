from unittest import TestCase
import os, sys, pytest,time
from ps.Basic import Basic, DEV_STAGES, hms_string, ps_shell, template_writer, EXEC,  get_html_string
from ps.Basic import send_a_mail

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

    def test_that_it_is_possible_to_create_a_base_object_for_the_dev_stages(self):
        log_files = ['LOG/Tests_d.log', 'LOG/Tests_i.log', 'LOG/Tests.log', 'LOG/Tests_t.log']
        for stage in DEV_STAGES:
            for log_file in log_files:
                try:    os.remove(log_file)
                except: pass
            os.environ["DEV_STAGE"] = stage
            # Reset the singleton mechanism to enable tests
            if Basic.INSTANCE: 
                Basic.logger =  "not_yet_defined"
                Basic.log_file_name          = "not_yet_defined"
                del(Basic.INSTANCE)
                Basic.INSTANCE = None
            b = Basic.get_instance("Tests",guarded_by_lockfile=True)
            c = Basic.get_instance("Tests",guarded_by_lockfile=True)
            assert (b is c)
            assert (Basic.suffix in ['_d', '_i', '_t', ''])
            assert (Basic.config_file_name in [os.path.join(os.getcwd(),'Tests_d.cfg'),
                                               os.path.join(os.getcwd(), 'Tests_i.cfg'),
                                               os.path.join(os.getcwd(), 'Tests.cfg'),
                                               os.path.join(os.getcwd(), 'Tests_t.cfg'),])
            assert (Basic.logging_port in [9020, 9022, 9024, 9010])
            assert (Basic.log_file_name in log_files)
            assert ("table" in open(Basic.log_file_name).read())
            b.__exit__(1, 2, 3)

    #  currently output (in the test) is not captured correctly in py.27
    # TBD:  reintegrate the assert statement. Currently at least the method is called. 
    def test_that_it_is_possible_to_set_the_verbose_mode(self):
        #from StringIO import StringIO
        for stage in DEV_STAGES:
            os.environ["DEV_STAGE"] = stage
            saved_stdout = sys.stdout
            try:
              #out = StringIO()
              #sys.stdout = out
              b = Basic.get_instance("Tests" )
              b.verbose()
              Basic.logger.info("HURZ")
              #output = out.getvalue().strip()
              #assert("HURZ" in output)
            finally:
              pass
              #sys.stdout = saved_stdout 

    def test_that_an_impossible_dev_stage_raises_an_keyError(self):
        with pytest.raises(KeyError) :
           os.environ["DEV_STAGE"] = "NOT_AN_ALLOWED_DEV_STAGE"
           b = Basic.get_instance("Tests", guarded_by_lockfile=True)
           b.__exit__(1, 2, 3)



    # if BASIC_CONFIGFILE_DIR is set, the path to the configfile is written to stdout. 
    # This is tested via doctest in Basic.py
    def test_that_an_BASIC_CONFIGFILE_DIR_environment_variable_is_checked_properly(self):
        for stage in DEV_STAGES:
            os.environ["DEV_STAGE"] = stage
            os.environ["BASIC_CONFIGFILE_DIR"] = "/tmp"
            b = Basic.get_instance("Tests", guarded_by_lockfile=True)
            sys.stdout.write(Basic.config_file_name)
            assert (
                Basic.config_file_name in ['/tmp/Tests_d.cfg', '/tmp/Tests_i.cfg', '/tmp/Tests.cfg',
                                           '/tmp/Tests_t.cfg'])
            b.__exit__(1, 2, 3)

            #    TBD: make this work
            #    @raises(ParsingError)

    def test_that_an_inproper_configured_cfg_file_raises_an_error(self):
        return
        for stage in DEV_STAGES:
          with pytest.raises(ParsingError) :
            os.environ["DEV_STAGE"] = stage
            if Basic.INSTANCE: 
                Basic.logger =  "not_yet_defined"
                Basic.log_file_name          = "not_yet_defined"
                del(Basic.INSTANCE)
                Basic.INSTANCE = None
            fp = open("Tests2" + DEV_STAGES[stage]['suffix'] + ".cfg", "w")
            fp.write("[section]\n")
            fp.write("    name : value  \n")
            b = Basic.get_instance("Tests2", guarded_by_lockfile=True,force_usage_of_config_file=True)
            b.__exit__(1, 2, 3)

    def test_get_html_string(self):
        assert ("<table><tr><td>A</td><td>B</td></tr></table>" == get_html_string({"A":"B"}))

    def test_hms_string(self):
        assert ("00:00:00" == hms_string(0))
        assert ("00:00:59" == hms_string(59))
        assert ("00:01:00" == hms_string(60))
        assert ("00:01:01" == hms_string(61))
        assert ("00:10:00" == hms_string(600))
        assert ("01:00:00" == hms_string(3600))
        assert ("01:00:01" == hms_string(3601))
        assert ("01:10:01" == hms_string(4201))

    def test_ps_shell1(self):
        for stage in DEV_STAGES:
            os.environ["DEV_STAGE"] = stage
            b = Basic.get_instance("Tests", guarded_by_lockfile=True)
            stdou, stder, exitcode, time_needed = ps_shell("ls -1")
            assert (0 == exitcode)
            assert ("00:00:00" <= time_needed)
            assert ("00:00:10" > time_needed)
            b.__exit__(1, 2, 3)

    def test_ps_shell_failure(self):
        for stage in DEV_STAGES:
            os.environ["DEV_STAGE"] = stage
            b = Basic.get_instance("Tests", guarded_by_lockfile=True)
            stdou, stder, exitcode, time_needed = ps_shell("Unmoegliches Kommando")
            b.__exit__(1, 2, 3)
            assert ([''] != stder)
            assert (exitcode != 0)
            assert ("00:00:00" <= time_needed)
            assert ("00:00:10" > time_needed)

    def test_ps_shell_exception(self):
        for stage in DEV_STAGES:
            os.environ["DEV_STAGE"] = stage
            b = Basic.get_instance("Tests", guarded_by_lockfile=True)
            # env_p==-1 ==> exception
            stdou, stder, exitcode, time_needed = ps_shell(["Unmoegliches Kommando"], env_p=-1)
            b.__exit__(1, 2, 3)
            assert ('ERROR' in stdou)
            assert ('Traceback' in "".join(stder))
            assert (exitcode != 0)
            assert ("00:00:00" <= time_needed)
            assert ("00:00:10" > time_needed)

    #
    # TBD: send a mail has to be implemented for python 3
    def test_ps_send_mail(self):
        for stage in DEV_STAGES:
            os.environ["DEV_STAGE"] = stage
            b = Basic.get_instance("Tests", guarded_by_lockfile=True)
            send_a_mail("Sender", ["l_send_to_p"], "subject", "text", files=[], server="localhost", test_only=True)
            b.__exit__(1, 2, 3)

    def test_ps_send_mail_buffering_on_dev_stage_TESTING(self):
        os.environ["DEV_STAGE"] = "TESTING" 
        b = Basic.get_instance("Tests", guarded_by_lockfile=True)
        import ps
        assert(ps.Basic.Basic.curr_mail_sender      == "")
        assert(ps.Basic.Basic.curr_mail_recipients  == "")
        assert(ps.Basic.Basic.curr_mail_subject     == "")
        assert(ps.Basic.Basic.curr_mail_text        == "")
        send_a_mail("Sender", ["l_send_to_p"], "subject", "text", files=[], server="localhost", test_only=True)
        assert("l_send_to_p" in ps.Basic.Basic.curr_mail_recipients) 
        assert("Sender"    == ps.Basic.Basic.curr_mail_sender)
        assert("subject"   == ps.Basic.Basic.curr_mail_subject)
        assert("text"      == ps.Basic.Basic.curr_mail_text) 
        b.__exit__(1, 2, 3)


    def test_ps_send_mail_with_attachement(self):
        for stage in DEV_STAGES:
            f = open("/tmp/testmail", "w")
            os.environ["DEV_STAGE"] = stage
            b = Basic.get_instance("Tests", guarded_by_lockfile=True)
            send_a_mail("Sender", ["l_send_to_p"], "subject", "text", files=["/tmp/testmail"], server="localhost",
                        test_only=True)
            b.__exit__(1, 2, 3)

    def test_ps_send_mail_with_exception(self):
        for stage in DEV_STAGES:
            os.environ["DEV_STAGE"] = stage
            b = Basic.get_instance("Tests", guarded_by_lockfile=True)
            send_a_mail("Sender", ["l_send_to_p"], "subject", "text", files=[], server="gibbesnich")
            b.__exit__(1, 2, 3)

    def test_template_writers(self):
        PATTERNS = {"DE": {"A": "ERFOLG: Wert %(variable_name)s", },
                    "EN": {"A": "SUCCESS: Value %(variable_name)s", },
                    }
        for stage in DEV_STAGES:
            res = template_writer(PATTERNS, "DE", "A", {"variable_name": "value"})
            assert (res == "ERFOLG: Wert value")
            res = template_writer(PATTERNS, "EN", "A", {"variable_name": "value"})
            assert (res == "SUCCESS: Value value")

    def test_rsync_from_localhost(self):
        self.skipTest('not tested, till user rights for jenkins based tests are settled to ONE host/user')
        for stage in DEV_STAGES:
            os.environ["DEV_STAGE"] = stage
            project_name = "Test_rsync"
            if stage.startswith("P"): ext = ""
            if stage.startswith("I"): ext = "_i"
            if stage.startswith("D"): ext = "_d"
            if stage.startswith("T"): ext = "_t"
            ps_shell("mkdir -p /tmp/test")
            ps_shell("/bin/rm -fR /tmp/test/src")
            fp = open("%s%s.cfg" % (project_name, ext), "w")

            cfg = """
[DEFAULT]
path_to_product_dir=TMP
DESTINATION_HOST=localhost
destination_dir=/tmp/test
[RSYNC]
cmd=rsync -Ltzvr --chmod=a+rwx,g+rwx,o-wx --delete --bwlimit=1800 --checksum --block-size=1024 --inplace --stats --progress --rsync-path=/usr/bin/rsync %(path_to_product_dir)s  %(DESTINATION_HOST)s:%(destination_dir)s 
         """.replace("TMP", os.path.join(os.getcwd(), "src"))
            fp.write(cfg)
            fp.close()
            b = Basic.get_instance(project_name, guarded_by_lockfile=True)
            e = EXEC(Basic, dictionary={"DESTINATION_HOST": "x"})
            cmd = Basic.config_parser.get("RSYNC", "cmd")
            sys.stdout.write(cmd)
            ret = e.lexec(cmd)
            b.__exit__(1, 2, 3)
            assert ("ps" in os.listdir("/tmp/test/src"))
