import urllib2
import sys
import bs4
import os
import shutil
from progress.spinner import PixelSpinner
from time import sleep
import cursor

cwd = os.getcwd()
spinner = PixelSpinner()
base_url = "https://unpkg.com/"

def stable_retry(ExceptionType=Exception,
                 tries=5, delay=5, backoff=1.20):
    def real_decorator(function):
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return function(*args, **kwargs)
                except ExceptionType as e:
                    print(
                        "\n%s, Api connecion failed Retrying in %d seconds..." %
                        (str(e), mdelay))
                    sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
                spinner.next()
            print(
                "Failed to connect to API within {0} Tries".format(tries))
            return function
        return f_retry
    return real_decorator

def install(package):
    package_version = get_package(package)
    spinner.message = "Installing %s" % package_version
    package_name = package_version.split("@")[0]
    if os.path.isdir(package_name):
        return "%s is already installed" % package_version
    else:
        os.mkdir(package_name)
        os.chdir(package_name)
    url = "%sbrowse/%s/" % (base_url, package_version)
    path = "%s/js-packages/%s" % (cwd, package_name)
    if not os.path.isdir(path):
        os.mkdir(path)
    traverse(url, path)
    os.chdir(cwd)
    return package_version

def uninstall(package):
    package_name = get_package(package)
    spinner.message = "Uninstalling %s" % package_name
    shutil.rmtree(package_name.split("@")[0])
    return package_name

def get_package(package):
    if not os.path.isdir("js-packages"):
        os.mkdir("js-packages")
    os.chdir("js-packages")
    url = "https://unpkg.com/browse/%s/" % package
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    return response.geturl().split("/")[-2]


def traverse(package_url, path):
    spinner.next()
    response = urllib2.urlopen(package_url)
    content_type = response.info().getheader('Content-Type').split(";")[0]
    ignore = ["/", "../", "js", "scss/", "less/", "src/"]
    if response.getcode() == 200:
        if content_type == "text/html":
            if not os.path.isdir(path):
                os.mkdir(path)
            os.chdir(path)
            html = response.read()
            data = bs4.BeautifulSoup(html, "html.parser")
            for l in data.find_all("a"):
                href = l.get("href", None)
                if href is not None:
                    if l["href"] not in ignore:
                        if "/browse" not in l["href"]:
                            if "https://" not in l["href"]:
                                file_url = "%s%s" % (package_url , l["href"])
                                if file_url[-1] == "/":
                                    new_path = "%s/%s" % (path, file_url.split("/")[-2])
                                else:
                                    file_url = file_url.replace("/browse", "")
                                    new_path = "%s/%s" % (path, file_url.split("/")[-1])
                                traverse(file_url, new_path)
            os.chdir("..")
        else:
            with open("%s" % (response.geturl().split("/")[-1]), "w") as f:
                f.write(response.read())
    return True

def main():
    if len(sys.argv) > 2:
        print "Searching for %s" % sys.argv[2]
        cmd = sys.argv[1]
        if cmd == "install":
            installed_package_version = install(sys.argv[2])
            with open("%s/snakeskin.txt" % cwd, "a") as f:
                f.write(installed_package_version + "\n")
                f.close()
        elif cmd == "uninstall":
            uninstalled_package_version = uninstall(sys.argv[2])
            with open("%s/snakeskin.txt" % cwd, "r") as f:
                packages = f.read().split("\n")
            packages.remove(uninstalled_package_version)
            with open("%s/snakeskin.txt" % cwd, "w") as f:
                for package in packages:
                    f.write("{}\n".format(package))
                f.write("\n")
            
    else:
        if os.path.isfile("%s/snakeskin.txt" % cwd):
            with open("%s/snakeskin.txt" % cwd, "r") as f:
                packages = f.read().split("\n")
            for package in packages:
                if len(package) > 0:
                    install(package)
    print "\n"

if __name__ == "__main__":
    main()
    cursor.show()