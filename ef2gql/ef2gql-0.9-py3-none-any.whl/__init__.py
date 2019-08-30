import os

def get_fieldname(line):
    res = line.strip().replace(' { get; set; }', '').split(' ')[-1:]
    return str(res[0])

def get_graphtype(line, fieldName):
    csType = str(line.strip().replace(' { get; set; }', '').split(' ')[-2:][0]).replace('?', '')
    switcher = {
        'int': 'IntGraphType',
        'string': 'StringGraphType',
        'DateTime': 'DateTimeGraphType',
        'bool': 'BooleanGraphType'
    }
    res = switcher.get(csType, 'NotSimpleType')
    if res == 'NotSimpleType':
        if 'ICollection' in line:
            res = 'ListGraphType<{}>'.format(fieldName)
        else:
            print('Warning: Messed up on making graphql type for :\n' + line)
            
    return res

def get_description(line, fieldName):
    res = 'The {}'.format(fieldName)
    return res

def iterateModels(efdir, generateGraphType):
    for file in os.listdir(efdir):
        filepath = os.path.join(efdir, file)
        if filepath.endswith(".cs"):
            with open(filepath) as f:
                content = f.readlines()
                generateGraphType(content)

def generateGraphTypeWithDir(graphQLTypeDir):
    def generateGraphType(efModelFileContent):
        graphTypeContent = ''
        makeGraphType = True
        fileName = ''
        for line in efModelFileContent:
            if 'using Microsoft.EntityFrameworkCore;' in line:
                makeGraphType = False
                break;
            elif 'namespace ' in line:
                graphTypeContent += '''
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using GraphQL.Types;
using {}

'''.format(line.strip().replace('namespace ', '') + ';') + line.strip() + '''.GraphTypes
{
'''
            elif 'public partial class ' in line:
                cls = str.replace(line, 'public partial class ', '').strip()
                fileName = cls + 'Type' + '.cs'
                graphTypeContent += line.rstrip() + '''Type : ObjectGraphType<{}>
    {{'''.format(cls) + '''
        public {}
    '''.format(fileName.replace('.cs', '()')) + '''    {{
            Name = "{}";
    '''.format(cls)
            elif '{ get; set; }' in line:
                if 'virtual' in line: break
                fieldName = get_fieldname(line)
                graphType = get_graphtype(line, fieldName + 'Type')
                description = get_description(line, fieldName)
                graphTypeContent += '''        Field(u => u.{}, type: typeof({})).Description("{}");
    '''.format(fieldName, graphType, description)
        
        graphTypeContent += '''    }
    }
}
        '''
                
        if makeGraphType:
            filePath = os.path.join(graphQLTypeDir, fileName)
            with open(filePath, 'a') as gqlTypeFile:
                gqlTypeFile.write(graphTypeContent)
                
    return generateGraphType
    
def getPathInput(prompt, default=''):
    res = input(prompt)
    if res == '':
        res = default
    res = os.path.join(os.getcwd(), os.path.realpath(res))
    print('>> ' + res)
    return res
    
def main():
    efModelDir = getPathInput('''The path to your EF Models [./]:\n>> ''')
    graphQLTypeDir = getPathInput('''The path to where your GraphTypes will be generated [./GraphTypes]:\n>> ''', 'GraphTypes')
    generateGraphType = generateGraphTypeWithDir(graphQLTypeDir)
    iterateModels(efModelDir, generateGraphType)
    print("\n>> finished")
        
if __name__ == "__main__":
    main()
    