import os
import nbconvert


def jup2py(jup_filename, py_filename=None, save=True):
    # print(
    #     "Please make sure you have saved your jupyter notebook before converting"
    # )
    if jup_filename is None or not jup_filename.endswith(".ipynb"):
        print("Please supply jupter filename with .ipynb extension")
    if py_filename is None:
        py_org_filename = os.path.splitext(jup_filename)[0] + "_original.py"
        py_filename = os.path.splitext(jup_filename)[0] + ".py"

        # Converting jupyter to py through nbconvertor
    py_code = nbconvert.export(nbconvert.PythonExporter(), jup_filename)
    mycode = py_code[0].split("\n")
    clean_code = []
    for index, line in enumerate(mycode):
        # Removing which are either "\n" or denotes the "Input" Tag for jupyter notebook
        if line == "\n" or (line.startswith("# In[")) or line is None or line == "":
            pass
        # Commenting the magic functions or the command line
        elif line.startswith("get_ipython()"):
            line = "#" + line
            clean_code.append(line)
        # Remove the jup2py line itself
        elif "jup2py" in line:
            pass
        else:
            clean_code.append(line)
    clean_code = "\n".join(clean_code)
    # Saving back the .py file
    if save:
        with open(py_filename, "w") as myfile:
            myfile.writelines(clean_code)
        print(f".py file {py_filename} saved!")
    else:
        return clean_code

