import os, sys
import shutil
import json, re
import click
import platform

from aos.util import popen, exec_cmd, get_aos_project, error
from aos.constant import *
import ConfigParser

class Rpm():
    """ Wrapper for rpm commands """

    def __init__(self, dbpath):
        self.dbpath = dbpath
        self.rpm = "rpm --dbpath %s" % dbpath

    def install(self, install_dir, rpm_dir):
        """ Install rpms to install_dir """

        cmd = "%s -ivh --relocate /=%s %s/*.rpm" % (self.rpm, install_dir, rpm_dir)
        popen(cmd.split())

    def uninstall(self, compname, *opts):
        """ Remove installed rpms """
        args = []
        args += compname
        if opts:
            args += opts

        cmd = "%s -e %s" % (self.rpm, " ".join(args))
        popen(cmd.split())

    def query(self, *opts):
        """ Run rpm query """
        cmd = "%s -q" % (self.rpm)
        args = []
        if opts:
            args += opts

            output, err = exec_cmd(cmd.split() + args)
            return output, err

class Yum():
    """ Wrapper for yum commands """

    def __init__(self, yumconf):
        self.conf = yumconf
        self.yum = "yumx -c %s" % yumconf

    def init_conf(self, baseurl=None):
        """ Create customized yum.conf """

        cf = ConfigParser.ConfigParser()
        cf.add_section("main")
        cf.set("main", "cachedir", "/var/cache/yum/aos")
        cf.set("main", "keepcache", "0")
        cf.set("main", "debuglevel", "2")
        cf.set("main", "logfile", "/var/log/yum.log")
        cf.set("main", "exactarch", "0")
        cf.set("main", "obsoletes", "1")
        cf.set("main", "gpgcheck", "0")
        cf.set("main", "plugins", "0")
        cf.set("main", "installonly_limit", "5")
        cf.set("main", "reposdir", "")
        cf.set("main", "installroot", os.path.dirname(self.conf))

        reponame = "AliOS_Things"
        cf.add_section(reponame)
        cf.set(reponame, "name", "Server")
        if baseurl:
            cf.set(reponame, "baseurl", baseurl)
        else:
            cf.set(reponame, "baseurl", OS_REPO)

        cf.set(reponame, "enable", "1")

        cf.write(open(self.conf, "w"))

    def clean(self):
        """ Clean cached metadata """
        cmd = "%s clean all" % self.yum
        exec_cmd(cmd.split())

    def list(self, remote, *opts):
        """ List installed/remote components """

        cmd = "%s list" % self.yum
        args = []
        suppress_error = False
        if not remote:
            args = ["installed"]

        for opt in opts:
            if "--suppress_error" == opt:
                suppress_error = True
                continue
            args += [ opt ]

        output, err = exec_cmd(cmd.split() + args, suppress_error)
        return output, err

    def search(self, keyword):
        """ Search components with keyword """

        cmd = "%s search %s" % (self.yum, " ".join(keyword))
        popen(cmd.split())

    def install(self, args=None):
        """ TODO: Install components """

        cmd = "%s install" % self.yum
        if args:
            popen(cmd.split() + args)
        else:
            click.echo("Nothing to install ...")

    def uninstall(self, args):
        """ TODO: Remove installed components """

        cmd = "%s remove %s" % (self.yum, " ".join(args))
        popen(cmd.split())

    def update(self, args=None, only_check=None, json_output=None):
        """ TODO: Update installed components """

        if only_check:
            cmd = "%s check-update" % self.yum
            # suppress exit code 100 for yum check-update:
            # 100 if there are packages available for update
            suppress_error = True
            if args:
                output, err = exec_cmd(cmd.split() + list(args), suppress_error)
            else:
                output, err = exec_cmd(cmd.split(), suppress_error)
            return output, err
        else:
            cmd = "%s update" % self.yum

            if args:
                popen(cmd.split() + list(args))
            else:
                popen(cmd.split())

    def download(self, download_dir, args=None):
        """ Download rpms to download_dir """

        cmd = "%s install --downloadonly --downloaddir=%s" % (self.yum, download_dir)
        if args:
            popen(cmd.split() + list(args))
        else:
           click.echo("Nothing to download ...")

    def show(self, json_format=None, remote=None, args=None):
        """ Show components information """

        cmd = "%s info" % self.yum
        if not remote and not args:
            args = ["installed"]

        if not json_format:
            popen(cmd.split() + list(args))
        else:
            json_output = []
            patten = re.compile(r"^(\w+)\s*:\s*(.*)")
            output, ret = exec_cmd(cmd.split() + list(args))
            for line in output.splitlines():
                match = patten.match(line)
                if match:
                    if "Name" == match.group(1):
                        tmp = { "name": match.group(2) }
                        curr_field = None
                    elif "Version" == match.group(1):
                        tmp["version"] = match.group(2)
                    elif "Summary" == match.group(1):
                        tmp["summary"] = match.group(2)
                        curr_field = tmp["summary"]
                    elif "Description" == match.group(1):
                        tmp["description"] = match.group(2)
                        curr_field = tmp["description"]
                    elif not match.group(1) and match.group(2):
                        print match.group(1)
                        print match.group(2)
                        curr_field += " " + match.group(2)
                    else:
                        pass

                if not line.strip():
                    json_output.append(tmp)

            # Get component dependency
            for item in json_output:
                comp_name = item["name"]
                item["depends"] = []
                patten = re.compile(r"\s*(dependency|provider):\s*(.*)")
                cmd = "%s deplist %s" % (self.yum, comp_name)
                output, ret = exec_cmd(cmd.split())
                for line in output.splitlines():
                    match = patten.match(line)
                    if match:
                        if "dependency" == match.group(1):
                            tmp = { "name": match.group(2) }
                        elif "provider" == match.group(1):
                            subpatten = re.compile(r".*.noarch\s*(.*)-r\d*.aos")
                            submatch = subpatten.match(match.group(2))
                            if submatch:
                                tmp["min_version"] = submatch.group(1)
                                tmp["max_version"] = ""
                                item["depends"].append(tmp)
                        else:
                            pass

            click.echo(json.dumps(json_output, sort_keys=True, indent=4))

class CompManager():
    """ Component Manager bases on Rpm/Yum infrastructure """

    def __init__(self, baseurl=None):
        project_dir = get_aos_project()
        if project_dir:
            self.project_dir = project_dir
        else:
            error("Can't find AliOS Things Project directory ...")

        if "Ubuntu" in platform.dist():
            dbpath = os.path.expanduser('~') + "/.rpmdb"
        else:
            dbpath = "/var/lib/rpm"

        self.rpmdb = "%s/%s%s" % (project_dir, ".aos", dbpath)
        self.rpm = Rpm(self.rpmdb)

        self.yumconf = os.path.join(project_dir, ".aos", "yum.conf")
        self.yum = Yum(self.yumconf)
        if not os.path.isfile(self.yumconf):
            self.yum.init_conf(baseurl)

    def install(self, comp_list, check_available=None):
        """ Install components.

        Workaroud: download rpms and then install them
        TODO:      install components directly
        """

        click.echo("Install Component: %s" % " ".join(comp_list))

        download_dir = os.path.join(self.project_dir, ".aos", "downloads")
        install_dir = os.path.join(self.project_dir, OS_NAME)

        # check available for compname
        if check_available:
            for compname in comp_list:
                opts = ["--suppress_error"]
                opts += [ compname ]
                remote = True

                output, err = self.list(remote, *opts)
                if err:
                    error("No matching component found: %s" % compname)
                    sys.exit(1)
                else:
                    click.echo("Component %s available" % compname)

        # cleanup download_dir first
        shutil.rmtree(download_dir)
        os.mkdir(download_dir)

        self.yum.download(download_dir, comp_list)
        if os.listdir(download_dir):
            self.rpm.install(install_dir, download_dir)

    def uninstall(self, compname, *opts):
        """ Remove installed components """

        click.echo("Uninstall component: %s" % " ".join(compname))
        self.rpm.uninstall(compname, *opts)
    
    def update(self, compname=None, only_check=None, json_output=None):
        """ Update installed components """

        if compname:
            click.echo("Update component: %s" % " ".join(compname))
        else:
            click.echo("Update all installed components")

        if only_check:
            output, err = self.yum.update(compname, only_check, json_output)
            return output, err
        else:
            self.yum.update(compname, only_check, json_output)

    def search(self, compname):
        """ Search remote components """

        click.echo("Search component: %s" % " ".join(compname))
        self.yum.search(compname)

    def list(self, remote, *opts):
        """ List installed/remote components """

        output, err = self.yum.list(remote, *opts)
        return output, err

    def show(self, json_format, remote, compname=None):
        """ Show installed/remote components information """

        self.yum.show(json_format, remote, compname)

    def clean(self):
        """ Clean cached metadata """
        self.yum.clean()

    def rpmquery(self, *opts):
        """ Run rpm query """
        output, err = self.rpm.query(*opts)
        return output, err
