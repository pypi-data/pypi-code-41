import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Tangly",
    version="2.1.2",
    author="Rafael Rayes",
    author_email="rafa@rayes.com.br",
    description="This package lets you display lists in form of tables!",
    long_description="""
'''Note. If the tables are messed up
here it is probably becuase of your computer font'''
''' This is a test verison, if it fails, use older ones'''


This package lets you display lists in form of tables!

to import it we run

```
import tangly
```


Now see what we can do to display a table with students and scores:

First we create a list with our data:

```
my_list = [["Johny", "57"],
	   ["Nath", "89"],
	   ["Alex", "78"],]
```
Here we defined our list of students and their respective scores.
To display this as a table we use the 'table()' command:
```
tangly.table(my_list)
```
This will be the output:
```
┌────────┬─────────┐
| first  | second  |
├────────┼─────────┤
| Johny  | 57      |
| Nath   | 89      |
| Alex   | 78      |
└────────┴─────────┘
```
Notice that the columns names are 'first' and 'second'. To change this we use some additional parameters:

```
tangly.table(my_list, 'Student' , 'Score' )

```

This will be the output:

```
┌──────────┬────────┐
| Student  | Score  |
├──────────┼────────┤
| Johny    | 57     |
| Nath     | 89     |
| Alex     | 78     |
└──────────┴────────┘
```

Much Better.


For help inside python type:
```
tangly.help()
```
""",
    long_description_content_type="text/markdown",
    url="https://github.com/rrayes3110/Tangly-Tables",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
