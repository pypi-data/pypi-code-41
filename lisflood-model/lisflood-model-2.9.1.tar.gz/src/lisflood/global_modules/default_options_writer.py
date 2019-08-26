import os
import xml.dom.minidom
import pprint
from collections import namedtuple

TimeSeries = namedtuple('TimeSeries', 'name, output_var, where, repoption, restrictoption, operation')
ReportedMap = namedtuple('ReportedMap', 'name, output_var, unit, end, steps, all, restrictoption, monthly, yearly')

printer = pprint.PrettyPrinter(indent=4, width=120)
options = {}
optionxml = os.path.join(os.path.dirname(__file__), '../OptionTserieMaps.xml')
domopt = xml.dom.minidom.parse(optionxml)
optDef = domopt.getElementsByTagName("lfoptions")[0]
for optset in optDef.getElementsByTagName("setoption"):
    print(optset.attributes['name'].value)
    options[optset.attributes['name'].value] = bool(int(optset.attributes['default'].value))

options['nonInit'] = not(options['InitLisflood'])

options['timeseries'] = {}
reportTimeSerie = domopt.getElementsByTagName("lftime")[0]
print('---------------------------------------------------')
for repTime in reportTimeSerie.getElementsByTagName("setserie"):
    keys = repTime.attributes.keys()
    name = repTime.attributes['name'].value
    print(name)
    output_var = repTime.attributes['outputVar'].value if 'outputVar' in keys else ''
    where = repTime.attributes['where'].value if 'where' in keys else ''
    repoption = repTime.attributes['repoption'].value.split(',') if 'repoption' in keys else ['']
    restrictoption = repTime.attributes['restrictoption'].value.split(',') if 'restrictoption' in keys else ['']
    operation = repTime.attributes['operation'].value.split(',') if 'operation' in keys else ['']

    t = TimeSeries(name=name, output_var=output_var, where=where,
                   repoption=repoption, restrictoption=restrictoption,
                   operation=operation)
    options['timeseries'][name] = t

options['reportedmaps'] = {}
print('---------------------------------------------------')
reportMap = domopt.getElementsByTagName("lfmaps")[0]
for repMap in reportMap.getElementsByTagName("setmap"):
    keys = repMap.attributes.keys()
    name = repMap.attributes['name'].value
    print(name)
    output_var = repMap.attributes['outputVar'].value if 'outputVar' in keys else ''
    unit = repMap.attributes['unit'].value if 'unit' in keys else ''
    end = repMap.attributes['end'].value.split(',') if 'end' in keys else []
    all_ = repMap.attributes['all'].value.split(',') if 'all' in keys else []
    steps = repMap.attributes['steps'].value.split(',') if 'steps' in keys else []
    restrictoption = repMap.attributes['restrictoption'].value.split(',') if 'restrictoption' in keys else []

    r = ReportedMap(name=name, output_var=output_var, unit=unit, end=end,
                    all=all_, restrictoption=restrictoption, steps=steps,
                    monthly=repMap.attributes.get('monthly') in ('True', '1', 'true', 1),
                    yearly=repMap.attributes.get('yearly') in ('True', '1', 'true', 1),
                    )
    options['reportedmaps'][name] = r


with open(os.path.join(os.path.dirname(__file__), './default_options.py'), 'w') as f:
    f.write("""
from collections import namedtuple


TimeSeries = namedtuple('TimeSeries', 'name, output_var, where, repoption, restrictoption, operation')
ReportedMap = namedtuple('ReportedMap', 'name, output_var, unit, end, steps, all, restrictoption, monthly, yearly')
""")
    f.write('\n\ndefault_options = ' + printer.pformat(options))
