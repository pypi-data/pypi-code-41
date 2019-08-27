import matplotlib.pyplot as plt
from sklearn.metrics import r2_score


def plot_actual_vs_prediction(X_train, y_train, X_test, y_test, model):
    """
    Actual vs Prediction plot for regression evaluation with R2-squared and identity line.


    == Example usage ==
    from jcopml.plot import plot_actual_vs_prediction
    plot_actual_vs_prediction(X_train, y_train, X_test, y_test, model)


    == Arguments ==
    X_train, X_test: pandas DataFrame
        training and testing input features

    y_train, y_test: pandas Series
        training and testing labels

    model: scikit-learn pipeline or estimator
        trained scikit-learn pipeline or estimator


    == Return ==
    None
    """
    plt.figure(figsize=(11, 5))

    plt.subplot(121)
    plt.scatter(model.predict(X_train), y_train, c='r', s=10)
    xlim, ylim = plt.xlim(), plt.ylim()
    plt.plot(xlim, ylim, 'k--', zorder=-1)
    plt.xlabel("Prediction", fontsize=14)
    plt.ylabel("Actual", fontsize=14)
    plt.title(f"R2_train: {r2_score(y_train, model.predict(X_train)):.3f}", fontsize=14)

    plt.subplot(122)
    plt.scatter(model.predict(X_test), y_test, c='r', s=10)
    xlim, ylim = plt.xlim(), plt.ylim()
    plt.plot(xlim, ylim, 'k--', zorder=-1)
    plt.xlabel("Prediction", fontsize=14)
    plt.ylabel("Actual", fontsize=14)
    plt.title(f"R2_test: {r2_score(y_test, model.predict(X_test)):.3f}", fontsize=14);
