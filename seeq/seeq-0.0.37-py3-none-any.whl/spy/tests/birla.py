import os
import re
import sys

import pandas as pd

from seeq import spy
from seeq.spy.assets import Model, Asset, Mixin


class BirlaModel(Model):

    def import_production_targets(self):
        production_targets_df = pd.DataFrame()
        production_targets_dir = os.path.join(os.getcwd(), 'production_targets')
        csv_files = [x for x in os.listdir(production_targets_dir) if x.endswith('.csv')]
        for csv_file in csv_files:
            csv = pd.read_csv(os.path.join(production_targets_dir, csv_file), parse_dates=True, index_col='Timestamp')
            grades = csv['Grade'].drop_duplicates()
            for grade in grades:
                unit = csv['Unit'].drop_duplicates().iloc[0]
                grade_signals = csv[csv['Grade'] == grade].drop(columns=['Unit', 'Grade'])
                grade_metadata = pd.DataFrame(index=grade_signals.columns)
                grade_metadata['Interpolation Method'] = 'step'
                grade_metadata['Maximum Interpolation'] = '120d'
                grade_metadata['Path'] = 'North Bend (Dev) >> Specialty Unit >> ' + unit + ' >> Production Targets'
                grade_metadata['Asset'] = grade
                grade_metadata['Name'] = grade_metadata.index
                grade_metadata['Type'] = 'Signal'
                push_results_df = spy.push(data=grade_signals, metadata=grade_metadata, errors='raise')
                production_targets_df = production_targets_df.append(push_results_df, ignore_index=True, sort=True)

        return production_targets_df

    @staticmethod
    def get_non_conformant_product_codes():
        return {
            'CSCU': 200,
            'RLU': 300
        }


class BlastAir(Asset):

    def __init__(self, definition, parent):
        super().__init__(definition)
        self.parent = parent  # type: Furnace

    @Asset.Attribute()
    def Actual(self, metadata):
        return {
            'Type': 'Signal',
            'Formula': '$f.resample(1min).remove($s1ao).setMaxInterpolation(20min)',
            'Formula Parameters': {
                '$f': metadata[metadata['Description'].str.contains(r'^(?:VENTURI FURNACE )?BLAST AIR FLOW$',
                                                                    na=False)],
                '$s1ao': self.Oil_Off(metadata)
            }
        }

    @Asset.Attribute()
    def Lower_Bound(self, metadata):
        grades = self.parent.get_grades(metadata)

        splice_fragments = list()
        formula_parameters = dict()

        for grade in grades:
            lower_bound_variable_name = '$BlastAirLowerBound_%s' % grade
            in_production_veriable_name = '$InProduction_%s' % grade
            splice_fragments.append(
                '0.toSignal().splice(%s, %s)' % (lower_bound_variable_name, in_production_veriable_name))

            formula_parameters[lower_bound_variable_name] = {
                'Data ID': ' >> '.join([self.parent.asset_definition['Path'],
                                        self.parent.asset_definition['Asset'],
                                        'Production Targets',
                                        grade,
                                        'Blast Air Lower Bound'])
            }

            formula_parameters[in_production_veriable_name] = {
                'Data ID': ' >> '.join([self.parent.asset_definition['Path'],
                                        self.parent.asset_definition['Asset'],
                                        'Production Targets',
                                        grade,
                                        'In Production'])
            }

        formula_parameters['$GradeChangeCondition'] = {
            'Data ID': ' >> '.join([self.parent.asset_definition['Path'],
                                    self.parent.asset_definition['Asset'],
                                    'Grade Changes'])
        }

        formula = 'add(%s)\n.toStep().resample(15min).remove($GradeChangeCondition).setMaxInterpolation(20min)' % (
            ',\n  '.join(splice_fragments)
        )

        return {
            'Type': 'Signal',
            'Formula': formula,
            'Formula Parameters': formula_parameters
        }

    @Asset.Attribute()
    def Oil_Status_Cleansed(self, metadata):
        if self.parent.asset_definition['Asset'] == 'S2A':
            oil_status = metadata[metadata['Name'] == 'FIC3102S/_.PV_Out#Value']
        else:
            oil_status = metadata[metadata['Name'].str.contains('_ENERG_OIL')]

        return {
            'Type': 'Signal',
            'Formula': '$s1ae.validvalues().tostep().setMaxInterpolation(30d)',
            'Formula Parameters': {
                '$s1ae': oil_status
            }
        }

    @Asset.Attribute()
    def Oil_Off(self, metadata):
        return {
            'Type': 'Condition',
            'Formula': '$a.validValues().valueSearch(isEqualTo(0))',
            'Formula Parameters': {
                '$a': self.Oil_Status_Cleansed(metadata)
            }
        }


class Production_Target(Asset):
    def __init__(self, definition, parent):
        super().__init__(definition)
        self.parent = parent  # type: Furnace

    @Asset.Attribute()
    def In_Production(self, metadata):
        non_conformant_product_codes = BirlaModel.get_non_conformant_product_codes()
        product_code_string = self.asset_definition['Asset']
        if product_code_string in non_conformant_product_codes:
            product_code_number = non_conformant_product_codes[product_code_string]
        else:
            product_code_number = int(re.sub(r'[^0-9]', '', product_code_string))
        unit = self.asset_definition['Unit']
        return {
            'Type': 'Condition',
            'Formula': '$grade.validValues().toStep().valueSearch(isEqualTo(%d))' % product_code_number,
            'Formula Parameters': {
                '$grade': self.parent.Current_Grade(metadata)
            },
            'Unit': unit
        }


class Furnace(Asset):

    def get_grades(self, metadata):
        return metadata['Grade'].drop_duplicates().dropna().tolist()

    @Asset.Attribute()
    def Current_Grade(self, metadata):
        unit = self.asset_definition['Name']
        return {
            'Type': 'Signal',
            'Formula': '$S1AGrade.validValues().toStep().resample(1min)',
            'Formula Parameters': {
                '$S1AGrade': metadata[metadata['Name'].str.contains(unit + '_CURRENT_GRADE')]
            }
        }

    @Asset.Attribute()
    def Grade_Changes(self, metadata):
        return {
            'Type': 'Condition',
            'Formula': '$S1ACleanGrade.runningdelta().valueSearch(isNotBetween(1,-1)).move(-15min,1hr).merge()',
            'Formula Parameters': {
                '$S1ACleanGrade': self.Current_Grade(metadata)
            }
        }

    @Asset.Component()
    def Blast_Air(self, metadata):
        path = self.asset_definition['Path'] + ' >> ' + self.asset_definition['Asset']
        return BlastAir({
            'Name': 'Blast Air',
            'Path': path,
            'Asset': 'Blast Air',
            'Unit': self.asset_definition['Name']
        }, self)

    @Asset.Component()
    def Production_Targets(self, metadata):
        grades = self.get_grades(metadata)
        definitions = list()
        path = self.asset_definition['Path'] + ' >> ' + self.asset_definition['Asset'] + ' >> Production Targets'
        for grade in grades:
            definitions.append(Production_Target({
                'Name': grade,
                'Path': path,
                'Asset': grade,
                'Unit': self.asset_definition['Name']
            }, self))

        return definitions


spy.login(url='https://birlacarbon.seeq.site', username='mark.derbecker@seeq.com', password='RR!Harley')

birla_model = BirlaModel()

prod_targets_file = r'D:\Scratch\BirlaCarbon\production_targets.pickle'
if not os.path.exists(prod_targets_file):
    prod_targets_df = birla_model.import_production_targets()
    prod_targets_df.to_pickle(prod_targets_file)
else:
    prod_targets_df = pd.read_pickle(prod_targets_file)

regex = r'.* >> (\w+) >> Production Targets'
prod_targets_df['Unit'] = prod_targets_df['Path'].str.extract(regex)
prod_targets_df['Grade'] = prod_targets_df['Asset']

prod_targets_df['Template'] = 'Furnace'
prod_targets_df['Path'] = 'North Bend (Dev) >> Specialty Unit'
prod_targets_df['Asset'] = prod_targets_df['Unit']

units = prod_targets_df['Unit'].drop_duplicates().tolist()

blast_air_tags_by_unit = {
    'S1A': 'FIC1104S/_.PV_Out#Value',
    'S1B': 'FIC2104S/_.PV_Out#Value',
    'S2A': 'FIC3101S/_.PV_Out#Value',
    'S2B': 'FIC4104S/_.PV_Out#Value',
    'S2C': 'FIC5104S/_.PV_Out#Value'
}

units_metadata = pd.DataFrame()
for unit in units:
    pickle_file = r'D:\Scratch\BirlaCarbon\unit_%s.pickle' % unit
    if not os.path.exists(pickle_file):
        results = spy.search({
            'Name': '%s_*' % unit,
            'Datasource Name': 'NOBPCGW01*'
        }).append(spy.search({
            'Name': blast_air_tags_by_unit[unit],
            'Datasource Name': 'NOBPCGW01*'
        }), sort=True)

        if unit == 'S2A':
            # Oil status is a weird tag for S2A
            results = results.append(spy.search({
                'Name': 'FIC3102S/_.PV_Out#Value',
                'Datasource Name': 'NOBPCGW01*'
            }), sort=True)

        results.to_pickle(pickle_file)
    else:
        results = pd.read_pickle(pickle_file)

    results['Template'] = 'Furnace'
    results['Path'] = 'North Bend (Dev) >> Specialty Unit'
    results['Asset'] = unit
    units_metadata = units_metadata.append(results, sort=True)

units_metadata = units_metadata.append(prod_targets_df, ignore_index=True, sort=True)

this_module = sys.modules[__name__]
instances_df = spy.assets.instantiate(this_module, units_metadata)

# Add the production targets to the push_metadata so they can be found for formula parameters
push_metadata_df = instances_df.append(prod_targets_df, ignore_index=True, sort=True)

print(push_metadata_df)

spy.push(metadata=push_metadata_df, errors='catalog', archive=False, datasource={'Datasource Class': 'Seeq Data Lab',
                                                                                 'Datasource Name': 'Seeq Data Lab'})
