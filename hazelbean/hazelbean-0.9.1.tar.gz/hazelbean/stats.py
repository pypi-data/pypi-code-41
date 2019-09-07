import os, sys, shutil, subprocess

import pprint
from collections import OrderedDict
import numpy as np
import pandas as pd

import hazelbean as hb
import math
from osgeo import gdal
import contextlib
import logging
import statsmodels.api as sm
import sklearn
import time
import json
import pickle
from sklearn.linear_model import LassoCV, LassoLarsCV, LassoLarsIC
from sklearn import datasets
import matplotlib.pyplot as plt

L = hb.get_logger('hazelbean stats')


class RegressionFrame(object):
    def __init__(self):
        self.inputs = OrderedDict() # Stores user input information (file locations, set membership) for GLOBAL UNPROCESSED inputs that may be different resolutions, extents, etc.
        self.aligned_inputs = OrderedDict() # Subset of inputs for all spatial variables that have been clipped and resampled to generate identical numpy array shapes.
        self.sources = OrderedDict() # Subset of aligned inputs that have been loaded as in-memory arrays.
        self.variables = OrderedDict() # Subset of along with any transforms of something that e.g. logs the sources. Not actually calculated until regression time to minimize memory impact.
        self.df = None
        self.stride_rate = 1

        self.variable_sets = OrderedDict()
        self.loaded_data = OrderedDict()

        # Running list to store results
        self.results = OrderedDict()

    def __str__(self):
        return 'RegressionFrame object: ' \
               '\n    Sources: ' + str([i for i in self.sources.keys()]) + '' \
               '\n    Variables: ' + str([i for i in self.variables.keys()]) + '' \

    def save_to_path(self, output_path):
        with open(output_path, 'wb') as output:
            pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)

    def load_from_path(self, input_path):
        print ('CHOSE NOT to do this as a method and instead is a module level function')

    def add_input(self, input_label, input_path, tags=None):
        new_input = hb.RegressionInput(input_label, input_path, self, tags=tags)
        self.inputs[input_label] = new_input



    def add_aligned_input(self, input_label, input_path, tags=None):
        new_aligned_input = hb.RegressionAlignedInput(input_label, input_path, self, tags=tags)
        self.aligned_inputs[input_label] = new_aligned_input

    def add_source(self, source_label, source_path, tags=None):
        new_source = hb.RegressionSource(source_label, source_path, self, tags=tags)
        self.sources[source_label] = new_source

        # if add_as_variable is True:
        #     # Always add a new variable of the linear transform of the source when a new source is created.
        #     self.add_variable(new_source.label, new_source.label, variable_type=None)
        return new_source

    # CONSIDER making all source_label labels etc be direct object references.
    def add_variable(self, variable_label, source_label, tags=None):
    # def add_variable(self, variable_label, source_label, variable_type=None):
        variable_type = 'asdf'
        new_variable = hb.RegressionVariable(variable_label, source_label, self, tags=tags)
        self.variables[variable_label] = new_variable
        return new_variable

    def add_variables_by_tags(self, variable_label, source):
        # Variable sets are a named list of variables where the first is assumed to be the depvar and all the others are
        # the indvars that constitute what will be run in a regression.


        for tag in source.tags:
            print('tag', tag)
        # print('tags', tags)
        # print([i.tags for i in self.sources.values()])
        # indvars = [i for i in self.sources.values() if all(tag in i.tags for tag in tags)]
        # print('indvars', indvars)
        # all(elem in list1 for elem in list2)

    def add_variable_set(self, variable_set_label, depvar_label, indvars):
        # Variable sets are a named list of variables where the first is assumed to be the depvar and all the others are
        # the indvars that constitute what will be run in a regression.
        self.variable_sets[variable_set_label] = [depvar_label] + indvars

    def add_variable_set_by_tags(self, variable_set_label, depvar_label, tags):
        # Variable sets are a named list of variables where the first is assumed to be the depvar and all the others are
        # the indvars that constitute what will be run in a regression.
        print('tags', tags)
        print([i.tags for i in self.sources.values()])
        indvars = [i for i in self.sources.values() if all(tag in i.tags for tag in tags)]
        print('indvars', indvars)
        # all(elem in list1 for elem in list2)

        self.variable_sets[variable_set_label] = [depvar_label] + indvars

    def initialize_variable_set(self, variable_set_label):
        L.info('Starting to initialize_variable_set for variable_set ' + str(variable_set_label))

        L.info('Initializing DF by adding depvar with a range() object as index.')

        self.current_variable_set = variable_set_label
        self.current_depvar_label = self.variable_sets[variable_set_label][0]

        # Load the first array out of order to get the shape of data needed to be created
        first_array = hb.load_gdal_ds_as_strided_array(self.variables[self.current_depvar_label].path, self.stride_rate)
        first_array_shape = first_array.shape
        n_obs = first_array.size
        n_vars = len(self.variable_sets[variable_set_label])

        # Create an array that calculates efficiently if ALL values are valid in each pixel-stack.
        all_valid_array = np.full(n_obs, 1, np.int8)

        # For the depvar, and later each indvar, write as zero where its not valid.
        current_valid_mask = first_array != self.sources[self.current_depvar_label].ndv
        all_valid_array[~current_valid_mask.flatten()] = 0

        # Initialize the data array with a NDV.
        data = np.full((n_obs, n_vars), -9999., dtype=np.float64)
        data[:, 0] = first_array.flatten().astype(np.float64)

        # Iterate through all of the post-depvar variables, overwriting the NDV in the data with their value and
        # also keeping track of pixel-stack validity.
        for c, variable_label in enumerate(self.variable_sets[variable_set_label][1:]):
            variable = self.variables[variable_label]
            if variable.variable_type is 'dummy':
                L.info('Adding dummy variable to DF for ' + str(variable.source_value))

                # For dummy variables, we only want to load the array once, and on this read, we also need to determine validity.
                if variable.source.data is None:
                    variable.source.data = hb.load_gdal_ds_as_strided_array(variable.source.path, self.stride_rate).astype(np.float64)
                    current_valid_mask = variable.source.data != variable.source.ndv
                    all_valid_array[~current_valid_mask.flatten()] = 0

                dummy_valid_mask = variable.source.data == variable.source_value

                # For dummies, there are three possible values, 0, 1, and NDV. Use separate masks to achieve this.
                data[:, c + 1][current_valid_mask.flatten() & ~dummy_valid_mask.flatten()] = 0
                data[:, c + 1][dummy_valid_mask.flatten()] = 1

            elif variable.variable_type is 'square':
                L.info('Adding squared variable to from ' + str(variable.source_label))

                if variable.source.data is None:
                    variable.source.data = hb.load_gdal_ds_as_strided_array(variable.source.path, self.stride_rate).astype(np.float64)

                current_valid_mask = variable.source.data != variable.ndv
                all_valid_array[~current_valid_mask.flatten()] = 0
                data[:, c + 1][current_valid_mask.flatten()] = variable.source.data.flatten()[current_valid_mask.flatten()] ** 2
            elif variable.variable_type is 'cube':
                L.info('Adding cubed variable to from ' + str(variable.source_label))

                if variable.source.data is None:
                    variable.source.data = hb.load_gdal_ds_as_strided_array(variable.source.path, self.stride_rate).astype(np.float64)

                current_valid_mask = variable.source.data != variable.ndv
                all_valid_array[~current_valid_mask.flatten()] = 0
                data[:, c + 1][current_valid_mask.flatten()] = variable.source.data.flatten()[current_valid_mask.flatten()] ** 3
            elif variable.variable_type is 'quad':
                L.info('Adding cubed variable to from ' + str(variable.source_label))

                if variable.source.data is None:
                    variable.source.data = hb.load_gdal_ds_as_strided_array(variable.source.path, self.stride_rate).astype(np.float64)

                current_valid_mask = variable.source.data != variable.ndv
                all_valid_array[~current_valid_mask.flatten()] = 0
                data[:, c + 1][current_valid_mask.flatten()] = variable.source.data.flatten()[current_valid_mask.flatten()] ** 4
            elif variable.variable_type is 'quint':
                L.info('Adding cubed variable to from ' + str(variable.source_label))

                if variable.source.data is None:
                    variable.source.data = hb.load_gdal_ds_as_strided_array(variable.source.path, self.stride_rate).astype(np.float64)

                current_valid_mask = variable.source.data != variable.ndv
                all_valid_array[~current_valid_mask.flatten()] = 0
                data[:, c + 1][current_valid_mask.flatten()] = variable.source.data.flatten()[current_valid_mask.flatten()] ** 5
            elif variable.variable_type is 'ln':
                L.info('Adding cubed variable to from ' + str(variable.source_label))

                if variable.source.data is None:
                    variable.source.data = hb.load_gdal_ds_as_strided_array(variable.source.path, self.stride_rate).astype(np.float64)

                current_valid_mask = variable.source.data != variable.ndv
                all_valid_array[~current_valid_mask.flatten()] = 0
                data[:, c + 1][current_valid_mask.flatten()] = np.log(variable.source.data.flatten()[current_valid_mask.flatten()])
            elif variable.variable_type is 'log10':
                L.info('Adding cubed variable to from ' + str(variable.source_label))

                if variable.source.data is None:
                    variable.source.data = hb.load_gdal_ds_as_strided_array(variable.source.path, self.stride_rate).astype(np.float64)

                current_valid_mask = variable.source.data != variable.ndv
                all_valid_array[~current_valid_mask.flatten()] = 0
                data[:, c + 1][current_valid_mask.flatten()] = np.log10(variable.source.data.flatten()[current_valid_mask.flatten()])
            else:
                current_valid_mask = variable.source.data != variable.ndv
                all_valid_array[~current_valid_mask.flatten()] = 0
                data[:, c + 1][current_valid_mask.flatten()] = hb.load_gdal_ds_as_strided_array(variable.source.path, self.stride_rate).astype(np.float64).flatten()[current_valid_mask.flatten()]

        df = pd.DataFrame(data=data, columns=self.variable_sets[variable_set_label], copy=False)

        L.info('n. obs before dropping anything: ' + str(len(df.index)))


        hb.pp('df', df.describe(include='all'))
        for col in df.columns:
            print(df[col].describe())

        df = df[(df != -9999.0).all(1)]
        L.info('n. obs after dropping NDV from array: ' + str(len(df.index)))
        L.info('number valid in all_valid_array:', np.sum(all_valid_array))


        return df, all_valid_array.reshape(first_array_shape)
    def get_stride_rate_from_desired_sample_size_and_path(self, sample_size, input_path):
        n_rows, n_cols = hb.get_raster_info_hb(input_path)['shape']
        unsampled_size = n_rows * n_cols
        stride_rate = 1

        if unsampled_size > sample_size:
            while True:
                stride_rate += 1
                cur_n_rows = int(math.floor(n_rows / stride_rate))
                cur_n_cols = int(math.floor(n_cols / stride_rate))

                if cur_n_rows * cur_n_cols <= sample_size:
                    return stride_rate
        else:
            return stride_rate

    def make_dummies_from_source(self, source, values_to_use=None):

        if values_to_use is None:

            if source.data is None:
                source.data = hb.load_gdal_ds_as_strided_array(source.path, self.stride_rate)
                # source.data = hb.as_array(source.path)
            values_to_use = np.unique(source.data).astype(np.int)

            L.info('Making dummy variables for:', str(values_to_use))

        for value in values_to_use:
            label = source.label + '_dummy' + str(value)
            v = self.add_variable(label, source.label, 'dummy')
            v.source_value = value

    def make_variable_transform_from_source(self, source_label, transform_type):
        if source_label not in self.sources:
            L.warning('Attempted to make transform ' + str(source_label) + ' but this was not in the current sources.')
        else:
            source = self.sources[source_label]

            if source.data is None:
                source.data = hb.load_gdal_ds_as_strided_array(source.path, self.stride_rate)

            if transform_type == 'square':
                label = source.label + '_square'
                v = self.add_variable(label, source.label, 'square')

            if transform_type == 'cube':
                label = source.label + '_cube'
                v = self.add_variable(label, source.label, 'cube')

            if transform_type == 'quad':
                label = source.label + '_quad'
                v = self.add_variable(label, source.label, 'quad')

            if transform_type == 'quint':
                label = source.label + '_quint'
                v = self.add_variable(label, source.label, 'quint')

            if transform_type == 'log':
                label = source.label + '_log'
                v = self.add_variable(label, source.label, 'log')

            if transform_type == 'log10':
                label = source.label + '_log10'
                v = self.add_variable(label, source.label, 'log10')

    def run_sm_lm(self, variable_set_label, regression_label, df, output_dir=None, has_constant=True):
        self.coeff_labels = self.variable_sets[variable_set_label][1:] # NOTE dropping depvar
        depvar_label = self.variable_sets[variable_set_label][0]
        lm_sm = sm.OLS(df.iloc[:, 0], df[self.coeff_labels], hasconst=has_constant).fit()

        self.coeff_values = lm_sm.params

        hb.write_to_file(str(lm_sm.summary()), os.path.join(output_dir, variable_set_label + '_sm_summary.txt'))
        lm_sm.params.to_csv(os.path.join(output_dir, variable_set_label + '_sm_params.csv'))

        result = OrderedDict()
        result['depvar_label'] = depvar_label
        result['coefficients'] = OrderedDict(zip(list(lm_sm.params.index), list(lm_sm.params.values)))
        result['variable_set_label'] = variable_set_label
        result['regression_label'] = regression_label
        self.results[regression_label] = result


    def run_lasso(self, variable_set_label, regression_label, df, output_dir=None, has_constant=True):
        self.coeff_labels = self.variable_sets[variable_set_label][1:] # NOTE dropping depvar
        depvar_label = self.variable_sets[variable_set_label][0]

        # Load X and y. For posterity
        df_copy = df.copy()

        X = df[self.coeff_labels]
        y = df.iloc[:, 0]

        # Split into train and test
        train, test = sklearn.model_selection.train_test_split(df, test_size=0.2)
        X_train = train[self.coeff_labels]
        X_test = test[self.coeff_labels]
        y_train = train.iloc[:, 0]
        y_test = test.iloc[:, 0]

        ## LassoLars Information Criterion optimization method
        # This could be worth running to show that we did further validation to show that our method for choosing the optimal alpha in the CV method resulted in something similar to an aic method.
        run_lassolarsic = False
        if run_lassolarsic:

            model_bic = LassoLarsIC(criterion='bic')
            t1 = time.time()
            model_bic.fit(X, y)
            t_bic = time.time() - t1
            alpha_bic_ = model_bic.alpha_

            model_aic = LassoLarsIC(criterion='aic', max_iter=45)
            model_aic.fit(X, y)
            alpha_aic_ = model_aic.alpha_

            def plot_ic_criterion(model, name, color):
                alpha_ = model.alpha_
                alphas_ = model.alphas_
                criterion_ = model.criterion_
                plt.plot(-np.log10(alphas_), criterion_, '--', color=color,
                         linewidth=3, label='%s criterion' % name)
                plt.axvline(-np.log10(alpha_), color=color, linewidth=3,
                            label='alpha: %s estimate' % name)
                plt.xlabel('-log(alpha)')
                plt.ylabel('criterion')


            plt.figure()
            plot_ic_criterion(model_aic, 'AIC', 'b')
            plot_ic_criterion(model_bic, 'BIC', 'r')
            plt.legend()
            plt.title('Information-criterion for model selection (training time %.3fs)' % t_bic)


        ## LassoLars Cross Validation method
        # Compute paths
        t1 = time.time()
        model_larscv = LassoLarsCV(cv=5).fit(X, y)
        t_lasso_lars_cv = time.time() - t1

        # Display results
        m_log_alphas = -np.log10(model_larscv.cv_alphas_)

        plt.figure()
        endplot = int(len(m_log_alphas) * .25)
        plt.plot(m_log_alphas[endplot:], model_larscv.mse_path_[endplot:], ':')
        plt.plot(m_log_alphas[endplot:], model_larscv.mse_path_.mean(axis=-1)[endplot:], 'k',
                 label='Average across the folds', linewidth=2)
        plt.axvline(-np.log10(model_larscv.alpha_), linestyle='--', color='k',
                    label='alpha CV')
        plt.legend()

        plt.xlabel('-log(alpha)')
        plt.ylabel('Mean square error')
        plt.title('Cross validation of LASSO-LARS to find optimal alpha')
        plt.axis('tight')
        plt.savefig(os.path.join(output_dir, 'LassoLarsCV-alpha.png'), dpi=350)
        plt.show()

        coefs = model_larscv.coef_path_[:,:]

        xx = np.sum(np.abs(coefs.T), axis=1)
        xx /= xx[-1]


        list_plot = np.asarray(list(sorted(coefs, key=sum)))


        plt.plot(xx, coefs.T)
        # for i in [0, 3, 33, 39, 40, 41, 42, 43, 44, 47, 49]:
        #     plt.plot(xx, coefs[i, :], label=X.columns[i].replace('lulc_esa_2000_dummy', ''))
        ymin, ymax = plt.ylim()
        plt.vlines(xx, ymin, ymax, linestyle='dashed', linewidth=0.2)
        plt.xlabel('Coefficient iteration path: |coef| / max|coef|')
        plt.ylabel('Coefficients')
        plt.title('LASSO Path for selected coefficients')
        # plt.axis('tight')
        # plt.legend( fontsize='8')
        # plt.tight_layout(h_pad=60)
        # plt.legend(bbox_to_anchor=(1.01, .99), fontsize='7', loc=2, borderaxespad=0.)
        plt.savefig(os.path.join(output_dir, 'LassoLarsCV-coef.png'), dpi=350)
        plt.show()

        self.coeff_values = model_larscv.coef_
        try:
            intercept = model_larscv.intercept_
        except:
            intercept = None
        print('intercept', intercept)
        result = OrderedDict()
        if intercept is None:
            result['coefficients_intermediate'] = OrderedDict(zip(list(X.columns), list(self.coeff_values)))
        else:
            result['coefficients_intermediate'] = OrderedDict(zip(['intercept'] + list(X.columns), [intercept] + list(self.coeff_values)))
        result['name'] = regression_label + '_larscv'
        self.results[result['name']] = result



        ## OLS reinterpretation using Lasso Lars selected variables
        self.selected_variable_labels = [str(k) for k, v in result['coefficients_intermediate'].items() if v != 0.0 and k != 'intercept']


        X = df_copy[self.coeff_labels]
        y = df_copy.iloc[:, 0]

        # NOTE: This absolutely has to have hasconst if you want to interpret the r2
        model_lmsm = sm.OLS(y_train, X_train[self.selected_variable_labels], hasconst=has_constant).fit() # NOTE dropping intercept via list slice

        self.coeff_values = model_lmsm.params
        hb.write_to_file(str(model_lmsm.summary()), os.path.join(output_dir, variable_set_label + '_selected_summary.txt'))
        model_lmsm.params.to_csv(os.path.join(output_dir, variable_set_label + '_selected_params.csv'))


        # NOTE THAT THIS regression generates multiple results. The last one, here, is given the name regression name as it is the final output.
        result = OrderedDict()
        if intercept is None:
            result['coefficients'] = OrderedDict(zip(list(model_lmsm.params.index), list(self.coeff_values)))
        else:
            result['coefficients'] = OrderedDict(zip(['intercept'] + list(model_lmsm.params.index), [intercept] + list(self.coeff_values)))

        result['depvar_label'] = depvar_label
        result['variable_set_label'] = variable_set_label
        result['regression_label'] = regression_label

        # result['coefficients'] = OrderedDict(zip(list(model_lmsm.params.index), list(model_lmsm.params.values)))
        result['name'] = regression_label
        self.results[result['name']] = result

        plt.show()

    def run_skl_lm(self, variable_set_label, regression_label, df, output_dir=None):
        L.info('Starting to fit regression.')

        self.coeff_labels = self.variable_sets[variable_set_label][1:]  # NOTE dropping depvar
        depvar_label = self.variable_sets[variable_set_label][0]

        lm_skl = sklearn.linear_model.LinearRegression(normalize=True, fit_intercept=True)
        lm_skl.fit(df[self.coeff_labels], df.iloc[:, 0])


        self.coeff_values = lm_skl.coef_

        output_df = pd.DataFrame({'linear_regression': self.coeff_values}, index=self.coeff_labels)
        output_df.to_csv(os.path.join(output_dir, variable_set_label + '_skl_params.csv'))
        L.info('Creating predictions from regression.')

        self.predictions = lm_skl.predict(df[self.coeff_labels])

        result = OrderedDict()
        result['coefficients'] = OrderedDict(zip(list(self.coeff_labels), list(self.coeff_values)))
        result['variable_set_label'] = variable_set_label
        result['regression_label'] = regression_label
        self.results[regression_label] = result

    def predict_output(self, regression_label, output_dir):

        # Get dependent variable for this regression
        result = self.results[regression_label]
        depvar_label = result['depvar_label']

        variable_set_label = result['variable_set_label']
        regression_label = result['regression_label']
        # all_valid_array_path = result['all_valid_array_path']
        variable_set = self.variable_sets[variable_set_label]

        depvar_source = self.sources[depvar_label]

        depvar_array = hb.as_array(depvar_source.path)


        projected_array = np.full(depvar_array.shape, 0., dtype=np.float64)
        all_valid_array = np.where(depvar_array != -9999., 1, 0).astype(np.int8)
        # all_valid_array = np.full(depvar_array.shape, 1., dtype=np.int8)

        # Unload all source data so that we can load in the proper resolution
        for source_label, source in self.sources.items():
            source.data = None

        for label, output_value in result['coefficients'].items():
            coeff = np.float64(output_value)

            L.info('Creating projected map from ' + str(label) + ' with coefficient ' + str(coeff))
            if label != 'intercept':
                source = self.variables[label].source
            else:
                L.info('intercept', output_value)

            # TODOO Potential memory optimization here: iterate throug sources first, THEN variables, unloading as needed.
            if label == 'intercept':
                # TODO why zero not one?
                array = np.zeros_like(projected_array, dtype=np.float64)
            elif '_dummy' in label:
                class_id_from_label = int(label.split('_dummy')[-1])
                esa_class_id = [k for k, v in hb.esacci_extended_short_class_descriptions.items() if k == class_id_from_label][0]

                if source.data is None:
                    source.data = hb.as_array(source.path).astype(np.float64)
                    all_valid_array[source.data == -9999.] = 0
                array = np.where(source.data == esa_class_id, 1, 0)

            elif '_square' in label:
                if source.data is None:
                    source.data = hb.as_array(source.path).astype(np.float64)
                    all_valid_array[source.data == -9999.] = 0
                array = source.data ** 2
            elif '_cube' in label:
                if source.data is None:
                    source.data = hb.as_array(source.path).astype(np.float64)
                    all_valid_array[source.data == -9999.] = 0
                array = source.data ** 3
            elif '_quad' in label:
                if source.data is None:
                    source.data = hb.as_array(source.path).astype(np.float64)
                    all_valid_array[source.data == -9999.] = 0
                array = source.data ** 4
            elif '_quint' in label:
                if source.data is None:
                    source.data = hb.as_array(source.path).astype(np.float64)
                    all_valid_array[source.data == -9999.] = 0
                array = source.data ** 5
            elif '_ln' in label:
                if source.data is None:
                    source.data = hb.as_array(source.path).astype(np.float64)
                    all_valid_array[source.data == -9999.] = 0
                array = np.log(source.data)
            elif '_log10' in label:
                if source.data is None:
                    source.data = hb.as_array(source.path).astype(np.float64)
                    all_valid_array[source.data == -9999.] = 0
                array = np.log10(source.data)
            else:  # Then its a standard, untransformed variable

                if source.data is None:
                    source.data = hb.as_array(source.path).astype(np.float64)

                    all_valid_array[source.data == -9999.] = 0
                array = source.data
            print('num valid', np.sum(all_valid_array))
            # Only calculate projection for where there is a full pixelstack of observation data
            # array = np.where(all_valid_array == 1, array, 0)

            projected_array += array * coeff
            array = None
            source.data = None
            L.info('sum added: ' + str(np.sum(array)) + ', projected mean: ' + str(np.mean(projected_array)))


        hb.save_array_as_geotiff(all_valid_array, hb.temp(), depvar_source.path)
        projected_array *= all_valid_array
        projected_path = os.path.join(output_dir, regression_label, 'agb_' + regression_label + '.tif')
        hb.save_array_as_geotiff(projected_array, projected_path, depvar_source.path, data_type=6, ndv=-9999.)

        residuals_array = (projected_array - depvar_array) * all_valid_array
        residuals_path = os.path.join(output_dir, regression_label, 'residuals_' + regression_label + '.tif')
        hb.save_array_as_geotiff(residuals_array, residuals_path, depvar_source.path, data_type=6, ndv=-9999.)

        all_valid_prediction_path = os.path.join(output_dir, regression_label, 'all_valid_' + regression_label + '.tif')
        hb.save_array_as_geotiff(all_valid_array, all_valid_prediction_path, depvar_source.path, data_type=6, ndv=-9999.)

# The following regression objects define a heirarcy of inputs at different stages of preprocessing and different sets for later use.

class RegressionInput(object):
    """Only used to assign inputs. This is the element the user modifies on input."""
    def __init__(self, label, path, rf, tags=None):
        self.label = label
        self.path = path
        self.data = None
        self.rf = rf

        if tags is None:
            self.tags = ['linear']
        else:
            self.tags = tags

    def __str__(self):
        return '<RegressionInput, ' + str(self.label) + ', ' + str(self.path) + '>'

    def __repr__(self):
        return '<RegressionInput, ' + str(self.label) + ', ' + str(self.path) + '>'


class RegressionAlignedInput(object):
    """Only used to assign inputs. This is the element the user modifies on input."""

    def __init__(self, label, path, rf, tags=None):
        self.label = label
        self.path = path
        self.data = None
        self.rf = rf
        self.tags = tags

    def __str__(self):
        return '<RegressionAlignedInput, ' + str(self.label) + ', ' + str(self.path) + '>'

    def __repr__(self):
        return '<RegressionAlignedInput, ' + str(self.label) + ', ' + str(self.path) + '>'


class RegressionSource(object):
    def __init__(self, label, path, rf, tags=None):
        self.label = label
        self.path = path
        self.data = None
        self.rf = rf
        self.tags = tags

        # Check that the path exists
        if not os.path.exists(self.path):
            L.critical('RegressionSource', self.path, 'does not exist')

        self.ndv = hb.get_raster_info_hb(path)['ndv']

        if self.ndv == None:
            raise NameError('No NDV set in ' + str(path))

    def __str__(self):
        return '<RegressionSource, ' + str(self.label) + ', ' + str(self.path) + '>'

    def __repr__(self):
        return '<RegressionSource, ' + str(self.label) + ', ' + str(self.path) + '>'

class RegressionVariable(object):
    def __init__(self, label, source_label, rf, tags=None):
        self.label = label
        self.source_label = source_label
        self.rf = rf
        self.source = self.rf.sources[source_label]
        self.path = self.source.path

        self.tags = tags
        # self.variable_type = variable_type
        self.ndv = self.source.ndv

    def __str__(self):
        return '<RegressionVariable, ' + str(self.label) + ', ' + str(self.path) + '>'

    def __repr__(self):
        return '<RegressionVariable, ' + str(self.label) + ', ' + str(self.path) + '>'

def load_rf_from_path(input_path):
    with open(input_path, 'rb') as fp:
        rf = pickle.load(fp)
    return rf


def execute_os_command(command):
    # TODOOO This may be useful throughout numdal
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # Poll process for new output until finished
    while True:
        nextline = process.stdout.readline().decode('ascii')
        if nextline == '' and process.poll() is not None and len(nextline) > 10:
            break
        sys.stdout.write(nextline)
        sys.stdout.flush()

    output = process.communicate()[0]
    exitCode = process.returncode

    if (exitCode == 0):
        return output
    else:
        raise Exception(command, exitCode, output)

def execute_r_string(r_string, output_uri=None, script_save_uri=None, keep_files=True):
    if not output_uri:
        # Learning point: the following line failed because os.path.join put a \ on , which r misinterpreted.
        #output_uri = os.path.join(hb.config.TEMP_FOLDER, hb.ruri('generated_r_output.txt'))
        output_uri = hb.config.TEMPORARY_DIR + '/' + hb.ruri('generated_r_output.txt')
        if not keep_files:
            hb.uris_to_delete_at_exit.append(output_uri)
    else:
        if '\\\\' in output_uri:
            output_uri = output_uri.replace('\\\\', '/')
        elif '\\' in output_uri:
            output_uri = output_uri.replace('\\', '/')
        else:
            pass # output_uri  was okay
    if not script_save_uri:
        script_save_uri = os.path.join(hb.config.TEMPORARY_DIR, hb.ruri('generated_r_script.R'))
        if not keep_files:
            hb.uris_to_delete_at_exit.append(script_save_uri)

    r_string = r_string.replace('\\', '/')

    print (r_string)
    f = open(script_save_uri, "w")

    f.write('sink(\"' + output_uri + '\")\n')
    f.write(r_string)
    f.close()

    returned = execute_r_script(script_save_uri, output_uri)

    return returned

def execute_r_script(script_uri, output_uri):
    cmd = 'C:\\Program Files\\R\\R-3.3.1\\bin\\Rscript.exe --vanilla --verbose ' + script_uri
    returned = subprocess.check_output(cmd, universal_newlines=True)
    if os.path.exists(output_uri):
        f = open(output_uri, 'r')
        to_return = ''
        for l in f:
            to_return += l +'\n'
        return to_return
    else:
        hb.L.warning('Executed r script but no output was found.')


def convert_af_to_1d_df(af):
    array = af.data.flatten()
    df = pd.DataFrame(array)
    return df


def concatenate_dfs_horizontally(df_list, column_headers=None):
    """
    Append horizontally, based on index.
    """

    df = pd.concat(df_list, axis=1)

    if column_headers:
        df.columns = column_headers
    return df


def convert_af_to_df(input_af, output_column_name=None):
    if not output_column_name:
        output_column_name = 'f_af_' + hb.random_alphanumeric_string(3)

    data = input_af.data.flatten()

    df = pd.DataFrame(data=data,  # values
                      index=np.arange(0, len(data)),  # 1st column as index
                      columns=[output_column_name])  # 1st row as the column names
    return df

def convert_df_to_af_via_index(input_df, column, match_af, output_uri):
    match_df = hb.convert_af_to_1d_df(match_af)
    if match_af.size != len(input_df.index):
        full_df = pd.DataFrame(np.zeros(match_af.size), index=match_df.index)
    else:
        full_df = input_df

    listed_index = np.array(list(input_df.index))

    full_df[0][listed_index] = input_df['0']
    # full_df[0][input_df.index] = input_df[column]

    array = full_df.values.reshape(match_af.shape)
    hb.ArrayFrame(array, match_af, output_uri=output_uri)
    af = hb.ArrayFrame(output_uri)

    return af

