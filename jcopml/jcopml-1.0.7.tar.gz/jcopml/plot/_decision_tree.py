from sklearn.externals.six import StringIO
from IPython.display import Image
from sklearn.tree import export_graphviz
import pydotplus


def plot_decision_tree(dtree, feature_name=None, filled=False, rounded=True, save_img_path=None):
    """
    Decision Tree Visualization


    == Example usage ==
    from jcopml.plot import plot_decision_tree
    model = RandomForestRegressor().fit(X_train, y_train)
    tree = model.estimators_[0]
    plot_decision_tree(tree, feature_name=X_train.columns, filled=True, rounded=True)


    == Arguments ==
    dtree: tree object
        scikit-learn's trained tree object

    feature_name: list or None
        list of feature names shown in the decision visualization. 'x' will be used if feature_name is None

    filled: bool
        fill the visualization with colors

    rounded: bool
        visualize decision tree with rounded rectangle

    save_img_name: str or None
        save the figure to the specified path str


    == Return ==
    IPython Image
    """
    dot_data = StringIO()
    if feature_name is not None:
        export_graphviz(dtree, out_file=dot_data, filled=filled, rounded=rounded, special_characters=True,
                        feature_names=feature_name)
    else:
        export_graphviz(dtree, out_file=dot_data, filled=filled, rounded=rounded, special_characters=True,
                        feature_names="x")

    graph = pydotplus.graph_from_dot_data(dot_data.getvalue())

    if save_img_path is not None:
        assert type(save_img_path) == str
        graph.write_png(save_img_path)

    return Image(graph.create_png())
