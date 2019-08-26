gap = r'''meta = {{
    'author': '{}',
    'title': '{}',
    'type': 'gap',
    'shuffle': True,
    'instances': 1,
    'gap_length': 20,
}}

task = """ description

[gap(1.0P)]Answer A, Answer B, Answer C[/gap]

This is a numeric gap and follows the syntax: <value>(,<min>,<max>)
[numeric(1.0P)]5, 0, 10[/numeric]

[select]
[ ] Answer A
[2] Answer B
[4] Answer C
[/select]

"""

feedback = """ feedback """
'''

order = r'''meta = {{
    'author': '{}',
    'title': '{}',
    'type': 'order',
    'instances': 1,
    'points': {}, # total number of points
}}

task = """ decription """

order = """ Answer A -- Answer B -- Answer C """

feedback = """ feedback """
'''

choice = r'''meta = {{
    'author': '{}',
    'title': '{}',
    'type': '{}',
    'instances': 1,
    'shuffle': True,
    'points': {}, # points per correct question
}}

task = """ decription """

choices = """
    [ ] Answer A
    [ ] Answer B
    [X] Answer C
"""

feedback = """ feedback """
'''

free = r'''meta = {{
    'author': '{}',
    'title': '{}',
    'type': 'free',
    'instances': 1,
    'points': {},
}}

task = """ decription """

feedback = """ feedback """
'''

javaScript = r'''meta = {{
    'author': '{}',
    'title': '{}',
    'type': 'javaScript',
    'instances': 1,
}}

task = """ Enter your task here. 
Except for code in between script tags (<script>...</script>).
Also avoid apperances of curly brackets in this block. 
Restructure your code so the curly brackets will appear in the javaScriptCode block!"""

correctAnswers = """
Answer A : 100.0P
Answer B : 2.0P
Answer C : 30.5P
"""

appendedData = """
image_1 : objects/img.png 
"""

javaScriptCode = """ Enter anything that's in between script tags. 
You don't need to add the tags at the beginning and at the end.
IMPORTANT: Your code should be able to change the value of the gap
used for the evaluation. You can use:
document.getElementsByName("gap_0")[0].value = ...;"""

feedback = """ feedback """
'''

config_sample = """[META]
author = {}
output = {}

[UPLAODER]
user = root
pass = homer
host = http://localhost:8000/ilias/
rtoken = c13456ec3d71dc657e19fb826750f676
"""


