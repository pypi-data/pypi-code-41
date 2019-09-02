import yaml
import json
document: str = """
    a: 1
    b: {}
    c: []
    d:
     - milk:
       - dairy
       - soy
     - 2
     - 3
     - eggs
"""

data = yaml.load(document)
print(json.dumps(data, indent=2))
print(data)

doc2: str = """
    - apples
    - oranges
    - milk:
        type: dairy
        milkfat: "2%"
"""

print(json.dumps(yaml.load(doc2), indent=2))

doc3: str = """
    - i_text_in_folder: my_special_name
"""
print(json.dumps(yaml.load(doc3), indent=2))

doc4: str = """
- ImmutableBlock:
    - i_outer_nested_named_list:
        type: NamedList
        children:
            - i_inner_nested_named_list:
                type: NamedList
                children:
                    - i_text_in_inner_nested_named_list
            - i_text_in_outer_nested_named_list
- TemporalBlock:
    - i_outer_nested_named_list:
        type: NamedList
        children:
            - i_inner_nested_named_list:
                type: NamedList
                children:
                    - i_text_in_inner_nested_named_list
            - i_text_in_outer_nested_named_list
"""
print(json.dumps(yaml.load(doc4), indent=2))
