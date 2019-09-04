import pandas as pd

from ngs_toolkit import Analysis
from sklearn.decomposition import NMF
from ngs_toolkit.graphics import plot_projection

a = Analysis(from_pep="metadata/project_config.yaml")
a.load_data()

m = a.annotate_samples(save=False, assign=False)

nmf = NMF()
x_new = pd.DataFrame(
    nmf.fit_transform(a.matrix_norm.T),
    index=m.columns)
color_dataframe = a.get_level_colors(index=m.columns, as_dataframe=True)

plot_projection(
    x_new,
    color_dataframe=color_dataframe,
    dims=4, output_file="nmf.svg",
    attributes_to_plot=["trisomy_12_class","sex_female"],
    plot_group_centroids=True)
