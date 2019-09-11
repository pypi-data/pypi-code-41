class DataFrameColumnIdentifier:
    def __init__(self):
        """
        An object that allows you to find the columns' name of a Pandas Dataframe, based on a matrix that matches the columns' values inside the DataFrame.

        Creating a new instance
        -----------------------
        dfci = DataFrameColumnIdentifier()

        Methods
        -------
        select_columns_by_values : Returns the names of the Pandas DataFrame columns which are selected based on a matrix of values.

        select_columns_KBest : Returns the names of the Pandas DataFrame columns which are selected based on the KBest.get_support method's output.

        transform : Returns a new Pandas DataFrame with only the columns which were selected on the select_columns_* method.

        Attributes
        ----------
        selected_columns_ : Name of the given Pandas DataFrame columns, selected based on the given values, after the select_columns_* method execution.
        """
        self.selected_columns_ = []

    def transform(self, X):
        """
        Returns a new Pandas DataFrame with only the columns which were selected on the select_columns_* method.

        transform(X)

        Parameters
        ----------
        X : Pandas DataFrame 
            The DataFrame to be transformed (the Pandas DataFrame must have the columns that should be found).
        """
        return X[self.selected_columns_]

    def select_columns_by_values(self, X, X_columns_values, n_validation_rows=1000, verbose=0):
        """
        Returns the names of the Pandas DataFrame columns which are selected based on a matrix of values.

        select_columns_by_values(X, X_columns_values, n_validation_rows=100, verbose=1)

        Parameters
        ----------
        X : Pandas DataFrame
            A DataFrame with the columns that must be found (the DataFrame must have the columns' values either).

        X_columns_values : numpy matrix 
            The values of the columns to be found.

        n_validation_rows : int, optional (default=1000)
            The number of rows that must be equal in the columns comparison. If the informed number is greater than the number of rows in X, the number of rows in X will be used.

        verbose :  int, optional (default=0)
            It controls the verbosity when looking for the columns.
        """
        self.selected_columns_ = []
        validation_rows = range(n_validation_rows) if n_validation_rows <= len(
            X) else range(len(X))
        X_columns_values_columns = range(X_columns_values.shape[1])
        X_columns = range(X.shape[1])

        for X_columns_values_column_index in X_columns_values_columns:
            for X_column_index in X_columns:
                if X.columns[X_column_index] not in self.selected_columns_:
                    equal_values = 0
                    for row_index in validation_rows:
                        if str(X_columns_values[row_index, X_columns_values_column_index]) == str(X.iloc[row_index, X_column_index]):
                            equal_values += 1
                    if equal_values == len(validation_rows):
                        self.selected_columns_.append(
                            X.columns[X_column_index])
                        if verbose == 1:
                            print('{} - Feature selected: {}'.format(len(self.selected_columns_),
                                                                     X.columns[X_column_index]))
                        break
        return self.selected_columns_

    def select_columns_KBest(self, X, kbest_get_support_output, verbose=0):
        """
        Returns the names of the Pandas DataFrame columns which are selected based on the KBest.get_support method's output.

        select_columns_KBest(X, kbest_get_support_output, verbose=0)

        Parameters
        ----------
        X : Pandas DataFrame
            The same DataFrame used in the KBest.fit_transform method.

        kbest_get_support_output : boolean array 
            The KBest.get_support method's output.

        verbose :  int, optional (default=0)
            It controls the verbosity when looking for the columns.
        """
        self.selected_columns_ = []
        kbest_get_support_output_columns = range(len(kbest_get_support_output))

        for column_index in kbest_get_support_output_columns:
            if kbest_get_support_output[column_index] == True:
                self.selected_columns_.append(X.columns[column_index])
                if verbose == 1:
                    print(
                        '{} - Feature selected: {}'.format(len(self.selected_columns_), X.columns[column_index]))
        return self.selected_columns_
