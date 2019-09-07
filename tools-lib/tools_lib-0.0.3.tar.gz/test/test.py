import tools_lib as tl

data = {
'name': {'The name is "Yogesh"': "", '''The name is "Yogesh ['"'] "''': {"name": "12hjuwf"}}
}

result = tl.dictToJSON(data, "data.json", pretty=True)
print(result)

tl.tprint("hello")
