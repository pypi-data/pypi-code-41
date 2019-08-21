import numpy
import pandas
import sklearn
from primalytics.tools import sign


class Encoder:
    def __init__(self, fit_variables: list, verbose: bool = False):
        self._fit_variables = fit_variables
        self._new_variables = {}
        self._verbose = verbose

        self._fitted = False

        self._is_df = False
        self._is_series = False
        self._is_dict = False
        self._is_array = False

    def reset(self):
        self._fitted = False
        self._new_variables = {}
        self._is_df = False
        self._is_series = False
        self._is_dict = False
        self._is_array = False

    def base_transform(self, data, array_indices, get_transformed):
        if not self._fitted:
            raise FitError('Encoder not fitted')

        self._is_df = isinstance(data, pandas.DataFrame)
        self._is_series = isinstance(data, pandas.Series)
        self._is_dict = isinstance(data, dict)
        self._is_array = isinstance(data, numpy.ndarray)

        if self._is_df:
            skip_data = data[data.columns.difference(self._fit_variables)]
            original_columns = list(data.columns)
            transformed_data = pandas.DataFrame(index=data.index)
        elif self._is_series:
            skip_data = data[data.index.difference(self._fit_variables)]
            original_columns = list(data.index)
            transformed_data = pandas.Series(name=data.name)
        elif self._is_dict:
            skip_data = None
            original_columns = list(data.keys())
            transformed_data = data.copy()
        elif self._is_array:
            skip_data = None
            original_columns = None
            transformed_data = numpy.array([])
            if array_indices is None:
                raise MissingIndicesError(
                    'Missing indices for array transformation'
                )
        else:
            raise TypeError('Type not valid for transformation')

        final_columns = []
        if self._is_series or self._is_df or self._is_dict:
            for variable in original_columns:
                if variable in self._fit_variables:
                    if self._verbose:
                        print('Transforming', variable)

                    transformed_col_or_val, new_columns = get_transformed(
                        col_or_val=data[variable],
                        variable=variable
                    )
                    final_columns += new_columns

                    if self._is_series:
                        transformed_data = transformed_data\
                            .append(transformed_col_or_val)
                    elif self._is_df:
                        transformed_data = transformed_data\
                            .join(transformed_col_or_val)
                    elif self._is_dict:
                        transformed_data.pop(variable)
                        transformed_data.update(transformed_col_or_val)
                else:
                    final_columns.append(variable)

        elif self._is_array:
            index = -1
            for i in range(len(data)):
                if i in array_indices:
                    if self._verbose:
                        print('Transforming', i)

                    index += 1
                    variable = self._fit_variables[index]
                    transformed_col_or_val, new_columns = get_transformed(
                        col_or_val=data[i], variable=variable
                    )
                    transformed_data = numpy.append(
                        transformed_data, transformed_col_or_val
                    )
                else:
                    transformed_data = numpy.append(transformed_data, data[i])

        if self._is_series:
            result = skip_data.append(transformed_data)[final_columns]
        elif self._is_df:
            result = skip_data.join(transformed_data)[final_columns]
        elif self._is_dict:
            result = transformed_data
        else:
            result = transformed_data

        return result

    def fit(self, df: pandas.DataFrame, return_new_variables: bool = False):
        pass


class HashEncoder(Encoder):
    def __init__(self, fit_variables: list, n_min_features: int = 2,
                 n_attempt_tot_max: int = 20, verbose: bool = False):

        super().__init__(fit_variables, verbose)

        self._hashing_dict = {}
        self._n_min_features = n_min_features
        self._n_attempt_tot_max = min(n_attempt_tot_max, 20)

    def fit(self, df: pandas.DataFrame, return_new_variables: bool = False):
        self.reset()
        self._hashing_dict = {}

        for variable in self._fit_variables:
            if self._verbose:
                print('Fitting', variable)
            self.__get_hashing(df, variable)

        self._fitted = True
        if return_new_variables:
            return self._new_variables

    def transform(self, data, array_indices=None):
        return super().base_transform(
            data=data,
            array_indices=array_indices,
            get_transformed=self.__get_transformed
        )

    def fit_transform(self, df, return_hashing_cols: bool = False,
                      array_indices=None):
        self.fit(df=df, return_new_variables=return_hashing_cols)
        return self.transform(data=df, array_indices=array_indices)

    def __get_transformed(self, col_or_val, variable: str):
        new_columns = self._new_variables[variable]

        if self._is_series:
            transformed_col_or_val = pandas.Series(
                self._hashing_dict[variable][col_or_val], index=new_columns
            )
        elif self._is_df:
            transformed_col_or_val = pandas.DataFrame(
                data=list(col_or_val.apply(
                    lambda x: self._hashing_dict[variable][x])
                ),
                index=col_or_val.index, columns=new_columns)
        elif self._is_dict:
            try:
                hashing_values = self._hashing_dict[variable][col_or_val]
            except KeyError:
                raise HashingError(
                    'Value \'{}\' not found in hashing dict for '
                    'variable \'{}\'.'.format(col_or_val, variable))

            transformed_col_or_val = {
                new_columns[i]: float(v) for i, v in enumerate(hashing_values)}
        else:
            transformed_col_or_val = numpy.array(
                self._hashing_dict[variable][col_or_val])

        return transformed_col_or_val, new_columns

    def __get_hashing(self, df: pandas.DataFrame, variable: str):
        n_features = self._n_min_features

        n_attempts_tot = 0
        missed_values = 2

        uniques = sorted(df.loc[:, variable].unique())
        n_uniques = len(uniques)

        hashed = [hash(x) for x in uniques]
        hashed = ['{}{:019}'.format(sign(x), abs(x)) for x in hashed]
        hashed_matrix = [[]]

        while (missed_values > 0) and n_attempts_tot < self._n_attempt_tot_max:
            hashed_matrix = [x[0: n_features] for x in hashed]
            n_taken = len(set(hashed_matrix))
            missed_values = n_uniques - n_taken

            hashed_matrix = [list(map(int, y)) for y in hashed_matrix]

            n_attempts_tot += 1
            n_features += 1

        if missed_values > 0:
            raise HashingError(
                'Hashing failed on variable: {}. '
                'Missed values{}.'.format(variable, missed_values))

        else:
            tmp_hashing_dict = dict(zip(uniques, hashed_matrix))
            self._hashing_dict.update({variable: tmp_hashing_dict})
            self._new_variables.update({
                variable: ['{}_H{:03}'.format(variable, i)
                           for i in range(len(hashed_matrix[0]))]
            })


class CircularEncoder(Encoder):
    def __init__(self, fit_variables: list, verbose: bool = False):
        super().__init__(fit_variables=fit_variables, verbose=verbose)
        self._variables = fit_variables
        self._parameters = {}

    def fit(self, df: pandas.DataFrame, **parameters):
        """
        :param df: pandas.DataFrame
        :param parameters: dictionary with shape
            {
                'variable' : {
                    'min' : <value>,
                    'max' : <value>,
                    'skip_values' : [<value1>, <value2>, ...] (optional)
                ...
            }
        :return:
        """
        self.reset()
        self._parameters = {}

        for variable in self._variables:
            var_parameters = parameters.get(variable, {})

            min_value = var_parameters.get('min', df[variable].min())
            max_value = var_parameters.get('max', df[variable].max())
            skip_values = var_parameters.get('skip_values', [])

            self._parameters.update({
                variable: {
                    'min': min_value,
                    'den': max_value - min_value + 1,
                    'skip_values': skip_values
                }
            })

            self._new_variables.update({
                variable: ['{}_{}'.format(variable, s) for s in ['C', 'S']]
            })

        self._fitted = True

    def transform(self, data, array_indices=None):
        return super().base_transform(
            data=data,
            array_indices=array_indices,
            get_transformed=self.__get_transformed)

    def fit_transform(self, df, array_indices=None, **parameters):
        self.fit(df=df, **parameters)
        return self.transform(data=df, array_indices=array_indices)

    def __get_transformed(self, col_or_val, variable: str):
        new_columns = self._new_variables[variable]
        if self._is_df:
            data = list(col_or_val.apply(
                lambda x: self.__get_mapped(x, variable)))
            transformed_col_or_val = pandas.DataFrame(
                data=data,
                index=col_or_val.index,
                columns=new_columns)
        else:
            mapped_values = self.__get_mapped(col_or_val, variable)

            if self._is_series:
                transformed_col_or_val = pandas.Series(
                    data=mapped_values, index=new_columns)
            elif self._is_dict:
                transformed_col_or_val = {
                    new_columns[i]: float(v)
                    for i, v in enumerate(mapped_values)}
            else:
                transformed_col_or_val = numpy.array(mapped_values)

        return transformed_col_or_val, new_columns

    def __get_mapped(self, x, variable):
        if x in self._parameters[variable]['skip_values']:
            result = [0.0, 0.0]
        else:
            theta = 2 * numpy.pi * (x - self._parameters[variable]['min']) / \
                    (self._parameters[variable]['den'])
            result = [numpy.cos(theta), numpy.sin(theta)]

        return result


class OneHotEncoder(Encoder):
    def __init__(self, fit_variables, verbose: bool = False, **kwargs):
        """
        :param fit_variables: names of the variables to use
        :param verbose: print log while processing
        :param kwargs: kwargs to pass to sklearn.preprocessing.OneHotEncoder
        """
        super().__init__(fit_variables=fit_variables, verbose=verbose)
        self._variables = fit_variables

        ohe_args = {'categories': 'auto', 'sparse': False}
        ohe_args.update(kwargs)

        self.__one_hot_encoders = {
            variable: sklearn.preprocessing.OneHotEncoder(**ohe_args)
            for variable in self._variables}

    def fit(self, df: pandas.DataFrame, return_new_variables: bool = False):
        self.reset()
        for variable, encoder in self.__one_hot_encoders.items():
            encoder.fit(df[[variable]])

        self._new_variables = {
            variable: ['{}_OHE{:03}'.format(variable, i)
                       for i, _ in enumerate(df[variable].unique())]
            for variable in self._variables}

        self._fitted = True
        if return_new_variables:
            return self._new_variables

    def transform(self, data, array_indices=None):
        return super().base_transform(
            data=data,
            array_indices=array_indices,
            get_transformed=self.__get_transformed
        )

    def fit_transform(self, df, array_indices=None):
        self.fit(df=df)
        return self.transform(data=df, array_indices=array_indices)

    def __get_transformed(self, col_or_val, variable: str):
        new_columns = self._new_variables[variable]

        if self._is_df:
            input_col_or_val = col_or_val.values.reshape(-1, 1)
            data = self.__one_hot_encoders[variable].transform(input_col_or_val)
            transformed_col_or_val = pandas.DataFrame(
                data=data,
                index=col_or_val.index,
                columns=new_columns
            )
        else:
            data = self.__one_hot_encoders[variable].transform([[col_or_val]])
            data = data[0]

            if self._is_series:
                transformed_col_or_val = pandas.Series(
                    data=data, index=new_columns)
            elif self._is_dict:
                transformed_col_or_val = {
                    new_columns[i]: float(v) for i, v in enumerate(data)}
            else:
                transformed_col_or_val = data

        return transformed_col_or_val, new_columns


class KBinsDiscretizer(Encoder):
    def __init__(self, fit_variables, verbose: bool = False, **kwargs):
        """
        :param fit_variables: names of the variables to use
        :param verbose: print log while processing
        :param kwargs: kwargs to pass to sklearn.preprocessing.OneHotEncoder
        """
        super().__init__(fit_variables=fit_variables, verbose=verbose)
        self._variables = fit_variables

        self._k_bins_discretizers = {
            variable: sklearn.preprocessing.KBinsDiscretizer(**kwargs)
            for variable in self._variables
        }

    def fit(self, df: pandas.DataFrame, return_new_variables: bool = False):
        self.reset()

        for variable, encoder in self._k_bins_discretizers.items():
            encoder.fit(df[[variable]])
            new_variables = [
                '{}_KBD{:03}'.format(variable, i)
                for i in range(encoder.n_bins_[0])]

            self._new_variables.update({variable: new_variables})

        self._fitted = True
        if return_new_variables:
            return self._new_variables

    def transform(self, data, array_indices=None):
        return super().base_transform(
            data=data,
            array_indices=array_indices,
            get_transformed=self.__get_transformed
        )

    def fit_transform(self, df, array_indices=None):
        self.fit(df=df)
        return self.transform(data=df, array_indices=array_indices)

    def __get_transformed(self, col_or_val, variable: str):
        new_columns = self._new_variables[variable]
        print(new_columns)
        if self._is_df:
            input_col_or_val = col_or_val.values.reshape(-1, 1)
            data = self._k_bins_discretizers[variable].transform(
                data=input_col_or_val)
            transformed_col_or_val = pandas.DataFrame(
                data=data,
                index=col_or_val.index,
                columns=new_columns
            )
        else:
            data = self._k_bins_discretizers[variable].transform([[col_or_val]])
            data = data[0]

            if self._is_series:
                transformed_col_or_val = pandas.Series(
                    data=data, index=new_columns)
            elif self._is_dict:
                transformed_col_or_val = {
                    new_columns[i]: float(v) for i, v in enumerate(data)}
            else:
                transformed_col_or_val = data

        return transformed_col_or_val, new_columns

#
# class KBinsPowers(KBinsDiscretizer):
# 	def __init__(self, variables, verbose: bool = False, **kwargs):
# 		"""
# 		:param variables:
# 		:param verbose:
# 		:param kwargs:
# 		{
# 			'power' : <int>
# 			'variables': [ <variables list> ]
# 		}
# 		{
# 			'power' : <int>
# 			'variables': None
# 		}
# 		{
# 			'powers' :{
# 				variable : (None, [powers])
# 			}
# 		}
# 		{
# 			'powers' :{
# 				variable : ([ <bin indeces> ], [powers])
# 			}
# 		}
# 		"""
# 		super().__init__(variables=variables, verbose=verbose, **kwargs)
#
# 	def fit(self, df: pandas.DataFrame, **kwargs):
# 		super().fit(df, **kwargs)
# 		self._fitted = False
#
# 		power = kwargs.get('power')
# 		if power is not None:
# 			variables = kwargs.get('variables')
# 			if variables is None:
# 				variables = self._variables
#
# 			for variable in variables:
# 				dx = self.__get_dx(s=df[variable], variable=variable)
#
# 		elif 'powers' in kwargs.keys():
# 			for variable, powers in kwargs['powers'].items():
# 				encoder = self._k_bins_discretizers[variable]
#
# 	# encoder.fit(df[[variable]])
# 	# self.__new_columns.update({variable: ['{}_KBD{:03}'.
# 	format(variable, i) for i in range(encoder.n_bins_[0])]})
# 	def __get_dx(self, s: pandas.Series, variable: str):
# 		x0 = self._k_bins_discretizers[variable].bin_edges_
# 		dx = self._k_bins_discretizers[variable].transform(s)
# 		return dx


class LabelEncoder(Encoder):
    def __init__(self, fit_variables, verbose=False):
        super().__init__(fit_variables=fit_variables, verbose=verbose)
        self.__label_encoders = {
            variable: sklearn.preprocessing.LabelEncoder()
            for variable in self._fit_variables}

    def fit(self, df: pandas.DataFrame, return_new_variables: bool = False):
        self.reset()

        for variable, encoder in self.__label_encoders.items():
            encoder.fit(df[[variable]])

        self._fitted = True
        if return_new_variables:
            return self._new_variables

    def transform(self, data, array_indices=None):
        return super().base_transform(
            data=data,
            array_indices=array_indices,
            get_transformed=self.__get_transformed)

    def fit_transform(self, df, array_indices=None):
        self.fit(df=df)
        return self.transform(data=df, array_indices=array_indices)

    def __get_transformed(self, col_or_val, variable: str):
        if self._is_df:
            transformed_col_or_val = pandas.DataFrame(
                self.__label_encoders[variable].transform(col_or_val.values)
                    .reshape(-1, 1), index=col_or_val.index, columns=[variable])
        else:
            data = self.__label_encoders[variable].transform([col_or_val])[0]
            if self._is_series:
                transformed_col_or_val = pandas.Series(
                    data=data, index=[variable])
            elif self._is_dict:
                transformed_col_or_val = {variable: data}
            else:
                transformed_col_or_val = data

        return transformed_col_or_val, variable


class SequentialEncoder:
    def __init__(self, encoders: dict):
        """
        :param encoders: dict with shape:
            {
                'encoder_name': <encoder_intance>,
                ...
            }
        """
        self.__encoders = encoders

    def fit(self, df: pandas.DataFrame, **kwargs):
        """
        :param df: pandas.DataFrame to fit
        :param kwargs: parameters to pass to fit functions of each encoder:
            {
                'encoder_name_1' :
                    {
                        'variable_1': value_1,
                        'variable_2': value_2
                    },
                ...
            }
        """

        for name, encoder in self.__encoders.items():
            params = kwargs.get(name, {})
            encoder.fit(df, **params)

    def transform(self, data, array_indices: dict = None):
        """
        :param data: data to tranform
        :param array_indices: dict containing indices to use in case data is a
            numpy.array: {
                'encoder_name_1: [i_1, i_2, ...], 'encoder_name_2: [...]}
        :return:
        """
        if array_indices is not None:
            array_indices.update({
                name: {}
                for name in self.__encoders.keys()
                if name not in array_indices.keys()})
        else:
            array_indices = {name: {} for name in self.__encoders.keys()}

        transformed_data = data.copy()
        for name, encoder in self.__encoders.items():
            transformed_data = encoder.transform(
                data=transformed_data, array_indices=array_indices[name])

        return transformed_data

    def fit_transform(self, df: pandas.DataFrame,
                      array_indices: dict = None, **kwargs):
        """
        :param df: pandas.DataFrame to fit
        :param array_indices: dict containing indices to use in case data is a
            numpy.array:{
                'encoder_name_1: [i_1, i_2, ...], 'encoder_name_2: [...]}
        :param kwargs: parameters to pass to fit functions of each encoder:
            {
                'encoder_name_1' :
                    {
                        'variable_1': value_1,
                        'variable_2': value_2
                    },
                ...
            }
        :return:
        """
        self.fit(df=df, **kwargs)
        return self.transform(data=df, array_indices=array_indices)


# EXCEPTIONS -------------------------------------------------------------------
class FitError(Exception):
    """:raises Error when class Hasher is not fitted"""


class HashingError(Exception):
    """:raises Error when hashing is invalid"""


class MissingIndicesError(Exception):
    """:raises Error when indices are missing"""
