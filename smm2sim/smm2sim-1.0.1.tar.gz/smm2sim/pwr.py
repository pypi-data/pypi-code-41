from scipy import stats
import numpy as np
import pandas as pd
import re

class PWR(object):
    def __init__(self, weight=1, regress_to=None, values=None, pwr=None):
        self.weight = weight
        self.regress_to = regress_to
        if values is None:
            self.values = None
        else:
            self.values = values.copy()
        if pwr is None:
            self.pwr = [x for x in list(self.values) if x != 'Player'][0]
        else:
            self.pwr = pwr
        
    def calculate(self, **kwargs):
        return self
        
    def regress(self, df):
        self.values[pwr] = self.regress_to.regress(df, pwr)
        return self

class SRS(PWR):
    def __init__(self, weight=1, regress_to=None):
        PWR.__init__(self, weight, regress_to, pwr='SRS')
    
    def calculate(self, **kwargs):
        df = kwargs['gamelog'].groupby('Player').agg({'Pts':'mean'})
        df = df.rename(columns={'Pts':'SRS'}).reset_index()
        self.values = df[['Player','SRS']]
        return self
        
class PWRsystems(object):
    def __init__(self, regress_to=None, srs=None, others=None, scale=None):
        self.regress_to = regress_to
        self.systems = []
        self.scale = None
        if isinstance(scale, dict):
            self.scale = scale
        elif scale:
            self.setDefaultScale()
        if (srs is None) and (others is None):
            self.systems.append(SRS())
        else:
            pairs = [(srs, SRS)]
            for system in [{'Arg':x,'Class':y} for x, y in pairs]:
                if type(system['Arg']) is bool:
                    if system['Arg']:
                        self.systems.append(system['Class']())
                elif system['Arg'] is not None:
                    self.systems.append(system['Arg'])
            if others is not None:
                if isinstance(others, PWR):
                    self.systems.append(others)
                else:
                    for system in others:
                        self.systems.append(system)
                        
    def setDefaultScale(self):
        self.scale = {'st_dev':1.75,'mean':5.5}

    def combine(self):
        if (len(self.systems) > 1) and (self.scale is None):
            self.setDefaultScale()
        self.combined = self.systems[0].values[['Player']]
        for system in self.systems:
            self.combined = pd.merge(self.combined, system.values, on='Player', suffixes=('','_'))
            new_z = stats.zscore(self.combined[system.pwr].values)
            new_weights = [system.weight] * self.combined.shape[0]
            if 'z_scores' not in self.combined:    
                self.combined['z_scores'] = [[x] for x in new_z]
                self.combined['weights'] = [[x] for x in new_weights]
            else:
                self.combined['z_scores'] = [x[0] + [x[1]] for x in list(zip(self.combined['z_scores'].values, new_z))]
                self.combined['weights'] = [x[0] + [x[1]] for x in list(zip(self.combined['weights'].values, new_weights))]
        zipped = zip(self.combined['z_scores'].values, self.combined['weights'].values)
        self.combined['Avg_z'] = [np.inner(x, y) / np.sum(y) for x, y in zipped]
        if self.scale is None:
            self.combined['PWR'] = self.combined[self.systems[0].pwr].values
        else:
            self.combined['PWR'] = self.combined['Avg_z'].values * self.scale['st_dev'] + self.scale['mean']
        return PWR(regress_to=self.regress_to, values=self.combined[['Player','PWR']], pwr='PWR')