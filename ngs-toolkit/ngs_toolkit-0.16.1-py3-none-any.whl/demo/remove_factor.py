from ngs_toolkit import Analysis

a = Analysis(from_pep="metadata/project_config.yaml")
a.load_data()
a.matrix_norm = a.matrix_norm.dropna()

# inspect
a.unsupervised_analysis(output_prefix="before")

# assuming 'b' is the strongest factor

# remove 'b' without regard for the other factors
m = a.remove_factor_from_matrix(
    factor='b',
    assign=False, save=False)
a.unsupervised_analysis(
    matrix=m,
    output_prefix="after_simple")

# remove 'b' accounting for the other factors
m = a.remove_factor_from_matrix(
    factor='b', covariates=['a', 'c', 'd'],
    assign=False, save=False)
a.unsupervised_analysis(
    matrix=m,
    output_prefix="after_covariates")
