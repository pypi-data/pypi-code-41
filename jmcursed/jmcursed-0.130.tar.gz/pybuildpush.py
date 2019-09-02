import subprocess, os

run = lambda x : subprocess.run([x], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)



def get_current_ver():
    """ 
    Get the current version from setup.py; ie the local version, as a float.
    """
    
    f = run("cat setup.py | grep version")
    m = f.stdout.decode().split("n=")[1].strip("'").strip(",").strip()
    s = ""
    for i in range(0, len(m)):
        try:
	        if m[i] == ".":
		        s += "."
	        else:
	    	    s += str(int(m[i]))
        except:
	        continue
    print("Current version, from setup.py: {}".format(s))
    return float(s)

def get_current_pypi_ver():
    """ Get the PyPI remote version, as a float. """
    x = run("pip3 search jmcursed")

    ret = x.stdout.decode()

    if "(" in ret and ")" in ret:

        version = ret.split("(")[1].split(")")[0]
        print(version)
        print("{:1.2f}".format(float(version)))
        return float(version)


def inc_ver(ver, by: ("M","m","p") = "p"):
    """ 
    Given then floats returned by either of the above two, 
    increase the version number by Major, Minor, or Patch releases.
    """
    if by == "M":
        ver += 1.0
    elif by == "m":
        ver += 0.1
    elif by == "p":
        ver += 0.01
    return ver


x = get_current_ver()
y = get_current_pypi_ver()
print("Cur: {} PyPi: {} / mismatch: {}".format(x, y, x-y))
new = inc_ver(x, "p")
### This is cheating, but replace old ver with new version.
run("sed -i 's/{}/{:1.2f}/' setup.py".format(x, new))
## Then run setup.py
setup = subprocess.run(["python3 setup.py bdist_wheel sdist"], shell=True)
## Then finally, upload the version to PyPI.
uploaded = run("twine upload dist/*")
## and then clean up after ourselves:
clean = run("rm -rf build/ dist/ jmcursed.egg-info")
print("Don  e")
