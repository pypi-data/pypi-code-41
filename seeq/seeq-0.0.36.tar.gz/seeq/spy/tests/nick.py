from seeq import spy
import pandas as pd

from seeq.spy.assets import Asset

pd.set_option('display.max_colwidth', -1)

spy.login(username="nicholas.gigliotti@seeq.com", password="Seeq2019!", url="https://birlacarbon.seeq.site",
          auth_provider="Seeq")


class Site(Asset):
    @Asset.Component()
    def Units(self, metadata):
        unit_names = metadata['Unit'].dropna().drop_duplicates().tolist()
        unit_definitions = list()
        for unit_name in unit_names:
            unit_definition = Unit({
                'Name': unit_name,
            }, parent=self).build(metadata[metadata['Unit'] == unit_name])
            unit_definitions.extend(unit_definition)
        return unit_definitions


class Unit(Asset):
    @Asset.Component()
    def Reactors(self, metadata):
        reactor_names = metadata['Reactor'].dropna().drop_duplicates().tolist()
        reactor_definitions = list()
        for reactor_name in reactor_names:
            reactor_definition = Reactor({
                'Name': reactor_name,
            }, parent=self).build(metadata[metadata['Reactor'] == reactor_name])
            reactor_definitions.extend(reactor_definition)
        return reactor_definitions


class Reactor(Asset):
    @Asset.Attribute()
    def Make_Oil_Flow_Rate(self, metadata):
        return metadata[metadata['Description'].str.contains('MAKE OIL|MAKEOIL')]

    @Asset.Attribute()
    def Blast_Air_Flow_Rate(self, metadata):
        metadata1 = metadata[metadata['Description'].str.contains('BLAST AIR')]
        metadata2 = metadata1[~metadata1['Description'].str.contains('VENTURI')]

        if len(metadata2) != 1:
            return None

        if metadata2.iloc[0]['Value Unit Of Measure'] != 'ft³/h':
            return {
                'Name': 'Blast Air Flow Rate',
                'Type': 'Signal',
                'Formula': "($tag * 1000).setUnits('ft³/h')",
                'Formula Parameters': {
                    '$tag': metadata2
                },
            }
        else:
            return metadata2

    @Asset.Attribute()
    def Blast_Gas_Flow_Rate(self, metadata):
        metadata1 = metadata[metadata['Description'].str.contains('BLAST GAS')]
        return metadata1[~metadata1['Description'].str.contains('AUXILIARY')]

    @Asset.Attribute()
    def Oil_Status(self, metadata):
        metadata2 = metadata[metadata['Name'].str.contains('AN')]
        if len(metadata2) != 1:
            return None

        return {
            'Type': 'Signal',
            'Formula': "$tag.validValues().toStep().setmaxInterpolation(30 days)",
            'Formula Parameters': {
                '$tag': metadata2
            },
        }


unit1_vars = spy.search({'Name': '/^FIC1[1-4]+0[2-4]+\.PV.*/', 'Type': 'StoredSignal'})
oil_status_1 = spy.search({'Name': '/^XS1[1-5]+02C_AN$/', 'Description': '/OIL/'})
unit1_df = unit1_vars.append(oil_status_1)
other_units = spy.search({'Name': '/^FIC[2-5]+10[1-4]+.\.PV./'})
all_units = unit1_df.append(other_units)
all_units['Reactor'] = 'RX' + all_units['Name'].str.extract(pat='\w{2,3}(.).*')
all_units['Unit'] = 'Unit ' + all_units['Name'].str.extract(pat='\w{2,3}.(.).*')
all_units['Site'] = 'North Bend'
all_units['Instance Path'] = 'Nick Dev'
all_units['Instance Asset'] = 'North Bend'
instance_df = spy.assets.instantiate(Site, all_units)
print(instance_df)
push_results_df = spy.push(metadata=instance_df, errors='catalog')
push_results_df
