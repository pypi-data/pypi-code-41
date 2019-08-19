# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""A module that contains forecasting modules."""

from abc import abstractmethod
from typing import List, Tuple, Any, Optional, Dict

import pandas as pd
import pmdarima as pm

from automl.client.core.common import (
    forecasting_utils,
    time_series_data_frame,
    constants,
    model_wrappers,
    exceptions)


class _MultiGrainForecastBase:
    """
    Multi-grain forecast base class.

    Enables multi-grain fit and predict on learners that normally can only operate on a single timeseries.
    """

    def __init__(self, timeseries_param_dict):
        self.timeseries_param_dict = timeseries_param_dict
        self.time_column_name = self.timeseries_param_dict[constants.TimeSeries.TIME_COLUMN_NAME]
        self.grain_column_names = self.timeseries_param_dict.get(
            constants.TimeSeries.GRAIN_COLUMN_NAMES, None)
        self.grain_column_names = [constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN] if \
            self.grain_column_names is None or len(self.grain_column_names) == 0 else self.grain_column_names

        # model state
        self._grain_levels = []  # type: List[Tuple[str]]
        self._models = {}  # type: Dict[Tuple[str], Any]
        self._last_observation_dates = {}  # type: Dict[Tuple[str], pd.Timestamp]
        self._first_observation_dates = {}  # type: Dict[Tuple[str], pd.Timestamp]
        self._freq = None  # type: Optional[pd.DateOffset]
        self._is_fit = False

    def fit(self, X, y, **kwargs):
        tsdf = self._construct_tsdf(X, y)

        tsdf_bygrain = tsdf.groupby_grain()
        self._grain_levels = list(tsdf_bygrain.groups)

        # Initialize the models and state variables
        self._models = {lvl: None for lvl in self._grain_levels}
        self._last_observation_dates = {
            lvl: None for lvl in self._grain_levels}
        self._first_observation_dates = {
            lvl: None for lvl in self._grain_levels}

        for lvl, series_frame in tsdf_bygrain:
            self._fit_single_grain(lvl, series_frame, tsdf.time_colname)

        self._freq = tsdf.infer_freq()
        self._is_fit = True

    def predict(self, X):
        if not self._is_fit:
            raise exceptions.UntrainedModelException()

        tsdf = self._construct_tsdf(X)

        max_horizons = self._get_forecast_horizons(tsdf)
        # Make a dataframe of forecasts
        fcast_df = self._get_forecast(tsdf, max_horizons)

        # Get rows containing in-sample data if any
        in_sample_data = pd.DataFrame()
        for g, X_group in tsdf.groupby_grain():
            if g in self._grain_levels:
                in_sample_data = pd.concat([in_sample_data,
                                            X_group.loc[X_group.time_index <= self._last_observation_dates[g]]])
        # Get fitted results for in-sample data
        if in_sample_data.shape[0] > 0:
            in_sample_fitted = self._fit_in_sample(in_sample_data)
            in_sample_fitted = in_sample_fitted.loc[:, fcast_df.columns]
            fcast_df = pd.concat([in_sample_fitted, fcast_df])

        # We're going to join the forecasts to the input - but first:
        # Convert X to a plain data frame and drop the prediction
        #  columns if they already exist
        point_name = constants.TimeSeriesInternal.DUMMY_PREDICT_COLUMN
        X_df = pd.DataFrame(tsdf, copy=False).drop(
            axis=1,
            labels=[point_name],
            errors='ignore')

        # Left join the forecasts into the input;
        #  the join is on the index levels
        pred_df = X_df.merge(fcast_df, how='left',
                             left_index=True, right_index=True)

        return pred_df[constants.TimeSeriesInternal.DUMMY_PREDICT_COLUMN].values

    def _construct_tsdf(self, X, y=None):
        X = pd.DataFrame(X)
        if self.grain_column_names == [constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN]:
            X[constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN] = constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN

        tsdf_kwargs = {'grain_colnames': self.grain_column_names}
        if y is not None:
            X[constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN] = y
            tsdf_kwargs['ts_value_colname'] = constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN

        tsdf = time_series_data_frame.TimeSeriesDataFrame(
            X,
            self.time_column_name,
            **tsdf_kwargs)

        return tsdf

    def _fit_in_sample(self, X):
        """
        Return the fitted values from a the RecursiveForecaster model.

        :param X:
            A TimeSeriesDataFrame defining the data for which fitted values
            are desired.  Inputting the same data used to fit the model will
            return all fitted data.
        :type X: TimeSeriesDataFrame

        :Returns:
            a ForecastDataFrame containing the fitted values in `pred_point`.
        """
        point_name = constants.TimeSeriesInternal.DUMMY_PREDICT_COLUMN
        origin_name = constants.TimeSeriesInternal.ORIGIN_TIME_COLUMN_NAME

        fitted_df = pd.DataFrame()
        for g, X_grain in X.groupby_grain():
            origin_time = self._last_observation_dates[g]
            time_values = pd.date_range(self._first_observation_dates[g],
                                        origin_time,
                                        freq=self._freq)
            fitted = self._fit_in_sample_single_grain_impl(self._models[g], g)
            fitted = pd.Series(fitted, index=time_values)
            assign_dict = {origin_name: origin_time,
                           point_name: fitted[X_grain.time_index].values}
            X_grain = X_grain.assign(**assign_dict)

            fitted_df = pd.concat([fitted_df, X_grain])

        fitted_df = fitted_df.loc[X.index, :]

        return fitted_df

    def _get_forecast_horizons(self, X):
        """
        Find maximum horizons to forecast in the prediction frame X.

        Returns a dictionary, grain -> max horizon.
        Horizons are calculated relative to the latest training
        dates for each grain in X.
        If X has a grain that isn't present in the training data,
        this method returns a zero for that grain.
        """
        # Internal function for getting horizon for a single grain
        def horizon_by_grain(gr, Xgr):
            try:
                horizon = len(pd.date_range(start=self._last_observation_dates[gr],
                                            end=Xgr.time_index.max(),
                                            freq=self._freq))
            except KeyError:
                horizon = 0

            return horizon
        # ------------------------------------------

        fcast_horizon = {gr: horizon_by_grain(gr, Xgr)
                         for gr, Xgr in X.groupby_grain()}

        return fcast_horizon

    def _get_forecast(self, X, max_horizon):
        """
        Generate forecasts up to max_horizon for each grain in X.

        The max_horizon parameter can be a single integer or
        a dictionary mapping each grain in X to an integer.

        Note that this method generates max_horizon forecasts
        regardless of the content of X. The input, X, is used
        only to determine the grains to forecasts and the column
        names to create in the output.

        Returns a pandas DataFrame. The index of this data frame
        will have the same levels as the input, X.
        The ouput will have the following:
        time, grain(s), origin time, point forecast.
        """
        # Get column names from X
        point_name = constants.TimeSeriesInternal.DUMMY_PREDICT_COLUMN
        origin_time_colname = constants.TimeSeriesInternal.ORIGIN_TIME_COLUMN_NAME

        grain_iter = X.groupby_grain().groups.keys()

        # Make max_horizon forecasts for each grain
        fcast_df = pd.concat([
            self._get_forecast_single_grain(
                gr,
                max_horizon[gr],
                X.time_colname,
                X.grain_colnames,
                origin_time_colname,
                point_name)
            for gr in grain_iter])

        return fcast_df.set_index(X.index.names)

    def _get_forecast_single_grain(self, grain_level, max_horizon,
                                   time_colname,
                                   grain_colnames,
                                   origin_time_colname,
                                   pred_point_colname):
        """
        Generate forecasts up to max_horizon for a single grain.

        Returns a plain pandas Dataframe with the following columns:
        time, grain(s), origin time, point forecast,
        distribution forecast (optional).
        """
        if grain_level not in self._grain_levels \
                or not self._models[grain_level] \
                or max_horizon <= 0:

            raise exceptions.DataException(
                model_wrappers.ForecastingPipelineWrapper.FATAL_NO_GRAIN_IN_TRAIN)
        # ---------------------------------------------------------------

        # Origin date/time is the latest training date, by definition
        origin_date = self._last_observation_dates[grain_level]

        # Retrieve the trained model and make a point forecast
        trained_model = self._models[grain_level]
        point_fcast = self._get_forecast_single_grain_impl(
            trained_model, max_horizon, grain_level)

        # Construct the time axis that aligns with the forecasts
        fcast_start = origin_date + self._freq
        fcast_dates = pd.date_range(start=fcast_start,
                                    periods=max_horizon,
                                    freq=self._freq)

        # Create the data frame from a dictionary
        fcast_dict = {time_colname: fcast_dates,
                      origin_time_colname: origin_date,
                      pred_point_colname: point_fcast}

        if grain_colnames is not None:
            fcast_dict.update(forecasting_utils.grain_level_to_dict(grain_colnames,
                                                                    grain_level))

        return pd.DataFrame(fcast_dict)

    def _fit_single_grain(self, lvl, series_frame, time_colname):
        """
        Train a single series and will be invoked by parallel train job.

        lvl, series_frame - indicate the grain and the actual series data.
        """
        series_frame.sort_index()
        series_values = series_frame.ts_value.values
        self._models[lvl] = self._fit_single_grain_impl(series_values, lvl)

        # Gather the last observation date if time_colname is set
        self._last_observation_dates[lvl] = series_frame.time_index.max()
        self._first_observation_dates[lvl] = series_frame.time_index.min()

        return True

    @abstractmethod
    def _fit_in_sample_single_grain_impl(self, model, grain_level):
        """
        Return the fitted in-sample values from a model.

        :param model:
            is an object representation of a model. It is the
            object returned by the _fit_single_grain_impl method.

        :param grain_level:
            is an object that identifies the series by its
            grain group in a TimeSeriesDataFrame. In practice, it is an element
            of X.groupby_grain().groups.keys(). Implementers can use
            the grain_level to store time series specific state needed for
            training or forecasting. See ets.py for examples.

        :Returns:
            a 1-D numpy array of fitted values for the training data. The data are
            assumed to be in chronological order
        """
        raise NotImplementedError()

    @abstractmethod
    def _get_forecast_single_grain_impl(self, model, max_horizon, grain_level):
        """
        Return the forecasted value for a single grain.

        :param model:
            trained model.
        :param max_horizon:
            int that represents the max horizon.
        :param grain_level:
            tuple that identifies the timeseries the model belongs to.
        :Returns:
            a 1-D numpy array of fitted values for the training data. The data are
            assumed to be in chronological order
        """
        raise NotImplementedError

    @abstractmethod
    def _fit_single_grain_impl(self, series_values, grain_level):
        """
        Return a fitted model for a single timeseries.

        :param series_values:
            an array that represents the timeseries.
        :param grain_level:
            tuple that identifies the timeseries the model belongs to.
        :Returns:
            a model object that can be used to make predictions.
        """
        raise NotImplementedError


class AutoArima(_MultiGrainForecastBase):
    """AutoArima multigrain forecasting model."""

    def __init__(self, **kwargs):
        """Create an autoarima multi-grain forecasting model."""
        timeseries_param_dict = kwargs[constants.TimeSeriesInternal.TIMESERIES_PARAM_DICT]
        super().__init__(timeseries_param_dict)

    def _fit_in_sample_single_grain_impl(self, model, grain_level):
        pred = model.predict_in_sample()
        return pred

    def _get_forecast_single_grain_impl(self, model, max_horizon, grain_level):
        pred = model.predict(n_periods=int(max_horizon))
        return pred

    def _fit_single_grain_impl(self, series_values, grain_level):
        series_values = series_values.astype(float)
        model = pm.auto_arima(series_values, error_action="ignore")
        return model
