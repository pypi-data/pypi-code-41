import os
import glob

def runAllScriptsInDir(dir):
    os.chdir(dir)
    print(f"*** Run tests in {dir} ***")
    for f in glob.glob("*.py"):
        if f != "__init__.py":
            print(f"Run test {f}")


listOfDirs = list()
for (dirpath, dirnames, filenames) in os.walk('.'):
    if '__pycache__' not in dirpath and dirpath != '.':
        listOfDirs += [dirpath]

for l in listOfDirs:
    runAllScriptsInDir(l)


#    print(f"dirpath={dirpath}")
#    print(f"dirnames={dirnames}")
#    for f in filenames:
#        if f.endswith(".py") and f != 'run_all.py':
#            listOfFiles += [os.path.join(dirpath, f)]

#for f in listOfFiles:
#    os.system(f"python {f}")
