"""
Date : 2019-09-05
Author: Sagar Paudel
Description : This is a utility module which elimiates features using backward
              elimination technique.
"""
from graphviz import Source
from IPython.display import display
from IPython.display import SVG
import matplotlib.pylab as pylab
import matplotlib.pyplot as plt
import os
import pandas as pd
# from plotly import graph_objects as go
import pydotplus
import seaborn as sns
from sklearn.tree import export_graphviz
from wordcloud import STOPWORDS
from wordcloud import WordCloud

plt.style.use('ggplot')


class Plot(object):
    def __init__(self, data, show=True, save=True, rcParams=None, path=None):
        self.data = data
        self.save = save
        self.show = show
        self.path = path

        try:
            if self.path is None:
                self.path = "visualization/"

            if not os.path.isdir(self.path):
                os.mkdir(self.path)

            if rcParams is None:
                # rcParams Configurations
                rcParams = {'legend.fontsize': 'x-large',
                            'figure.figsize': (14, 8),
                            'axes.labelsize': 'x-large',
                            'axes.titlesize': 'x-large',
                            'xtick.labelsize': 'x-large',
                            'ytick.labelsize': 'x-large'}

            pylab.rcParams.update(rcParams)
        except Exception as e:
            raise Exception(e)

    def countplot(self, x=None, y=None, hue=None, title=None,
                  xlabel=None, ylabel=None, orient=None):

        try:
            if xlabel is None:
                if x is not None:
                    xlabel = x
                else:
                    xlabel = y
            if ylabel is None:
                ylabel = "Count"

            if title is None:
                title = "{}  VS {}".format(xlabel.upper(), ylabel.upper())
            else:
                title = title.upper()

            fig = plt.figure()
            ax = sns.countplot(x=x, y=y, hue=hue, data=self.data, orient=orient)
            plt.title(title)
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)

            if self.save:
                plt.savefig(self.path + "{}_countplot".format(title))

            if self.show:
                plt.show()
            else:
                plt.close(fig)
        except Exception as e:
            raise Exception(e)

    def distinctcountplot(self, include=None, exclude=None,  title=None,
                          xlabel=None, ylabel=None):

        try:
            if xlabel is None:
                xlabel = "Features"
            if ylabel is None:
                ylabel = "Distinct Count"

            if title is None:
                title = "{}  VS {}".format(xlabel.upper(), ylabel.upper())
            else:
                title = title.upper()

            if include is not None:
                temp = self.data[include].nunique().reset_index()
            elif exclude is not None:
                temp = self.data.drop(columns=exclude, axis=1).nunique().reset_index()
            else:
                temp = self.data.nunique().reset_index()

            temp.columns = ["columns", "distinct_count"]

            fig = plt.figure()
            ax = sns.barplot(x="columns", y="distinct_count", data=temp)
            plt.title(title)
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)

            if self.save:
                plt.savefig(self.path + "{}_distinctcountplot".format(title))

            if self.show:
                plt.show()
            else:
                plt.close(fig)
        except Exception as e:
            raise Exception(e)

    def barplot(self, x=None, y=None, hue=None, title=None,
                xlabel=None, ylabel=None, orient=None):
        try:

            if xlabel is None:
                xlabel = x
            if ylabel is None:
                ylabel = y

            if title is None:
                title = "{}  VS {}".format(xlabel.upper(), ylabel.upper())
            else:
                title = title.upper()

            fig = plt.figure()
            ax = sns.barplot(x=x, y=y, hue=hue, data=self.data)
            plt.title(title)
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)

            if self.save:
                plt.savefig(self.path + "{}_barplot".format(title))

            if self.show:
                plt.show()
            else:
                plt.close(fig)
        except Exception as e:
            raise Exception(e)

    def heatmap(self, x=None, y=None, val=None, title=None,
                xlabel=None, ylabel=None, format="int"):
        try:
            if xlabel is None:
                xlabel = x
            if ylabel is None:
                ylabel = y

            if title is None:
                title = "{}  VS {} having {}".format(xlabel.upper(),
                                                     ylabel.upper(), val.upper())
            else:
                title = title.upper()

            if format == "int":
                format = "d"
            elif format == "float":
                format = ".2f"
            else:
                format = "d"

            temp = self.data.pivot(y, x, val)
            fig = plt.figure()
            ax = sns.heatmap(temp, annot=True, fmt=format)
            plt.title(title)
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)

            if self.save:
                plt.savefig(self.path + "{}_heatmap".format(title))

            if self.show:
                plt.show()
            else:
                plt.close(fig)

        except Exception as e:
            raise Exception(e)

    def correlationplot(self, title=None, xlabel=None, ylabel=None):
        try:
            if title is None:
                title = "Correlation Plot".upper()
            else:
                title = title.upper()

            temp = self.data.corr()
            fig = plt.figure()
            ax = sns.heatmap(temp, annot=True, fmt=".2f")
            plt.title(title)
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)

            if self.save:
                plt.savefig(self.path + "{}_correlationplot".format(title))

            if self.show:
                plt.show()
            else:
                plt.close(fig)

        except Exception as e:
            raise Exception(e)

    def piechart(self, label_col=None, val_col=None,
                 include=None, exclude=None,  title=None,
                 metric="count", donut=False):
        try:
            if title is None:
                title = "Piechart"

            if label_col is not None and val_col is not None:
                if metric == "count":
                    temp = self.data.groupby(label_col).agg({val_col: "count"}).reset_index()
                elif metric == "sum":
                    temp = self.data.groupby(label_col).agg({val_col: "sum"}).reset_index()
                elif metric == "avg":
                    temp = self.data.groupby(label_col).agg({val_col: "mean"}).reset_index()
                elif metric == "distinct_count":
                    temp = self.data.groupby(label_col).agg({val_col: "nunique"}).reset_index()

            else:
                if include is not None:
                    temp = self.data[include]
                elif exclude is not None:
                    temp = self.data.drop(columns=exclude, axis=1)
                else:
                    temp = self.data

                if metric == "count":
                    temp = temp.count().reset_index()
                elif metric == "distinct_count":
                    temp = temp.nunique().reset_index()
                elif metric == "sum":
                    temp = temp.sum().reset_index()
                elif metric == "avg":
                    temp = temp.mean().reset_index()

            temp.columns = ["labels", metric]
            labels = temp["labels"].tolist()
            sizes = temp[metric].tolist()

            fig = plt.figure()
            if not donut:
                explode = [0] * len(sizes)
                explode[0] = 0.1
                plt.title(title)
                plt.pie(sizes, explode=explode, labels=labels,
                        autopct='%1.1f%%', shadow=True, startangle=90)
                plt.axis('equal')
            else:
                plt.title(title)
                # Create a circle for the center of the plot
                my_circle = plt.Circle((0, 0), 0.7, color='white')
                # Give color names
                plt.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True)
                p = plt.gcf()
                p.gca().add_artist(my_circle)

            if self.save:
                plt.savefig(self.path + title)

            if self.show:
                plt.show()
            else:
                plt.close(fig)

        except Exception as e:
            raise Exception(e)

    def boxplot(self, x=None, y=None, hue=None, title=None, xlabel=None, ylabel=None):
        try:
            if xlabel is None:
                xlabel = x
            if ylabel is None:
                ylabel = y

            if title is None:
                title = "{}  VS {}".format(xlabel.upper(), ylabel.upper())
            else:
                title = title.upper()

            fig = plt.figure()
            ax = sns.boxplot(x=x, y=y, hue=hue, data=self.data)
            plt.title(title)
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)

            if self.save:
                plt.savefig(self.path + "{}_boxplot".format(title))

            if self.show:
                plt.show()
            else:
                plt.close(fig)

        except Exception as e:
            raise Exception(e)

    def violinplot(self, x=None, y=None, hue=None, title=None,
                   xlabel=None, ylabel=None):
        try:
            if xlabel is None:
                xlabel = x
            if ylabel is None:
                ylabel = y

            if title is None:
                title = "{}  VS {}".format(xlabel.upper(), ylabel.upper())
            else:
                title = title.upper()

            fig = plt.figure()
            ax = sns.violinplot(x=x, y=y, hue=hue, data=self.data,
                                palette="Set2")
            plt.title(title)
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)

            if self.save:
                plt.savefig(self.path + "{}_violinplot".format(title))

            if self.show:
                plt.show()
            else:
                plt.close(fig)

        except Exception as e:
            raise Exception(e)

    def lineplot(self, x=None, y=None, hue=None, style=None, markers=True,
                 dashes=False, title=None, xlabel=None, ylabel=None):
        try:
            if xlabel is None:
                xlabel = x
            if ylabel is None:
                ylabel = y

            if title is None:
                title = "{}  VS {}".format(xlabel.upper(), ylabel.upper())
            else:
                title = title.upper()

            fig = plt.figure()
            ax = sns.lineplot(x=x, y=y, hue=hue, markers=markers, style=style,
                              dashes=dashes, data=self.data)
            plt.title(title)
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)

            if self.save:
                plt.savefig(self.path + "{}_lineplot".format(title))

            if self.show:
                plt.show()
            else:
                plt.close(fig)

        except Exception as e:
            raise Exception(e)

    def scatterplot(self, x=None, y=None, hue=None, title=None,
                    xlabel=None, ylabel=None):
        try:
            if xlabel is None:
                xlabel = x
            if ylabel is None:
                ylabel = y

            if title is None:
                title = "{}  VS {}".format(xlabel.upper(), ylabel.upper())
            else:
                title = title.upper()

            fig = plt.figure()
            ax = sns.scatterplot(x=x, y=y, hue=hue, data=self.data)
            plt.title(title)
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)

            if self.save:
                plt.savefig(self.path + "{}_scatterplot".format(title))

            if self.show:
                plt.show()
            else:
                plt.close(fig)

        except Exception as e:
            raise Exception(e)

    def distplot(self, x=None, rug=False, hist=True, kde=True,
                 title=None, xlabel=None, ylabel=None):
        try:
            if xlabel is None:
                xlabel = x

            if ylabel is None:
                ylabel = "Density"

            if title is None:
                title = "{} distribution plot".format(xlabel).upper()
            else:
                title = title.upper()

            fig = plt.figure()
            ax = sns.distplot(self.data[x], rug=rug, hist=hist, kde=kde)
            plt.title(title)
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)

            if self.save:
                plt.savefig(self.path + "{}_distplot".format(title))

            if self.show:
                plt.show()
            else:
                plt.close(fig)
        except Exception as e:
            raise Exception(e)

    def wordcloud(self, x=None, title=None):
        try:
            if title is None:
                title = "{} word cloud.".format(x).upper()

            stopwords = set(STOPWORDS)
            data = ",".join(self.data[x])

            wc = WordCloud(background_color='white',
                           stopwords=stopwords,
                           max_words=200,
                           max_font_size=40,
                           scale=3,
                           random_state=1).generate(str(data))
            fig = plt.figure()
            plt.axis('off')
            plt.title(title)
            plt.imshow(wc)

            if self.save:
                plt.savefig(self.path + title)

            if self.show:
                plt.show()
            else:
                plt.close(fig)

        except Exception as e:

            raise Exception(e)


class CMPlot(object):
    def __init__(self, mapping=None, plot=True, report=True,
                 save=True, path=None):

        self.__mapping = mapping
        self.__plot = plot
        self.__report = report
        self.__save = save
        self.__path = path

        if self.__path is None:
            self.__path = "visualization/"

        if not os.path.isdir(self.__path):
            os.mkdir(self.__path)

        if self.__mapping is None:
            print("You have to pass mapping dictionary!!")
            print("For example : {1:'yes', 0:'no'}")

    def fit_transform(self, y_true=None, y_pred=None):

        try:
            if y_true is None or y_pred is None:
                raise Exception("Please provide y_true and y_pred!!")

            if self.__mapping is None:
                raise Exception("Please provide mapping dictionary!!")

            df = pd.DataFrame({"y_true": y_true, "y_pred": y_pred})

            self.__mapping = {int(k): v for k, v in self.__mapping.items()}
            self.cm = pd.DataFrame(index=self.__mapping.values(),
                                   columns=self.__mapping.values())

            for val1, col in self.__mapping.items():
                self.cm[col] = [df[(df["y_pred"] == val1) &
                                   (df["y_true"] == val2)].shape[0]
                                for val2 in self.__mapping.keys()]

            diagonal_sum = sum([self.cm.iloc[i, i]
                                for i in range(self.cm.shape[0])])
            total = self.cm.sum().sum()
            self.accuracy = round(diagonal_sum/total, 3)*100
            self.error_rate = 100 - self.accuracy

            if self.__plot or self.__save:
                self.__plot_heatmap()

            if self.__report:
                self. __get_report()

        except Exception as e:
            raise Exception(e)

    def __plot_heatmap(self):
        try:
            plt.style.use('ggplot')
            fig = plt.figure(figsize=(10, 8))
            ax = sns.heatmap(self.cm, annot=True, fmt='d',
                             cbar_kws={'orientation': 'vertical'})
            plt.title("CONFUSION MATRIX | ACCURACY : {0}%".format(self.accuracy))
            plt.ylabel("Actual Value")
            plt.xlabel("Predicted Value")

            if self.__save:
                plt.savefig(self.__path + "confusion_matrix")

            if self.__plot:
                plt.show()
            else:
                plt.close(fig)

        except Exception as e:
            raise Exception(e)

    def __get_report(self):
        try:
            if self.cm.shape[0] == 2:
                tp = self.cm.iloc[0, 0]
                fn = self.cm.iloc[0, 1]
                fp = self.cm.iloc[1, 0]
                tn = self.cm.iloc[1, 1]

                self.sensitivity = self.recall = self.TPR = round(tp/(tp+fn), 3)

                self.specificity = self.TNR = round(tn/(tn+fp), 3)

                self.precision = round(tp/(tp+fp), 3)

                self.FPR = round(fp/(tn+fp), 3)

                self.FNR = round(fn/(tp+fn), 3)

                self.f1_score = round(2*(self.recall * self.precision) / (self.recall + self.precision),3)

                print("\n######################### SUMMARY REPORT #########################")
                print("Accuracy\t\t\t\t: {0}".format(self.accuracy))
                print("Sensitivity|Recall|TPR\t\t\t: {0}".format(self.sensitivity))
                print("Specificity|TNR\t\t\t\t: {0}".format(self.specificity))
                print("Precision|Positive Predictive Value\t: {0}".format(self.precision))
                print("FPR\t\t\t\t\t: {0}".format(self.FPR))
                print("FNR\t\t\t\t\t: {0}".format(self.FNR))
                print("F1 Score\t\t\t\t: {0}".format(self.f1_score))
                print("################# DEVELOPED BY : Sagar Paudel ####################")
            else:
                print("\nReport for multi-classification is not supported!!")
        except Exception as e:
            raise Exception(e)


class DecisionTreePlot(object):
    def __init__(self, save=True, show=True, path=None):
        self.save = save
        self.show = show
        self.path = path
        try:
            if self.path is None:
                self.path = "visualization/"

            if not os.path.isdir(self.path):
                os.mkdir(self.path)
        except Exception as e:
            raise Exception(e)

    def plot(self, estimator, feature_names=None, class_names=None):
        try:
            dot_data = export_graphviz(
                estimator, out_file=None, feature_names=feature_names,
                class_names=class_names, filled=True)

            if self.show:
                display(SVG(Source(dot_data).pipe(format='svg')))

            if self.save:
                graph = pydotplus.graph_from_dot_data(dot_data)
                graph.write_png(self.path + "decision_tree.png")

        except Exception as e:
            raise Exception(e)


if __name__ == "__main__":
    # Count Plot
    titanic = sns.load_dataset("titanic")
    po = Plot(titanic, show=False)
    po.countplot(x="class")

    # BarPlot
    tips = sns.load_dataset("tips")
    po = Plot(tips, show=False)
    po.barplot(x="day", y="total_bill", hue="sex")

    # Distinct Count Plot
    po.distinctcountplot(include=["sex", "day", "size"])

    # Pie Chart
    tips = sns.load_dataset("tips")
    po = Plot(tips, show=True)
    po.piechart(include=["sex", "day", "size", "time"])
    po.piechart(label_col="sex", val_col="size")

    # Donut Chart
    tips = sns.load_dataset("tips")
    po = Plot(tips, show=True)
    po.piechart(include=["sex", "day", "size", "time"], donut=True)
    po.piechart(label_col="sex", val_col="size", donut=True)

    # Heatmap
    flights = sns.load_dataset("flights")
    po = Plot(flights)
    po.heatmap(x="year", y="month", val="passengers", format="int")

    # Correlation Plot
    flights = sns.load_dataset("flights")
    po = Plot(flights)
    po.correlationplot()

    # Box Plot
    tips = sns.load_dataset("tips")
    po = Plot(tips)
    po.boxplot(x="day", y="total_bill", hue="smoker")

    # Line Plot
    fmri = sns.load_dataset("fmri")
    po = Plot(fmri)
    po.lineplot(x="timepoint", y="signal", hue="event", style="event")

    # Scatter Plot
    tips = sns.load_dataset("tips")
    po = Plot(tips)
    po.scatterplot(x="total_bill", y="tip", hue="time")

    # Distribution plot
    tips = sns.load_dataset("tips")
    po = Plot(tips)
    po.distplot(x="total_bill")

    # Violin Plot
    tips = sns.load_dataset("tips")
    po = Plot(tips)
    po.violinplot(x="day", y="total_bill", hue="smoker")

    # Words cloud
    words = ["Sagar", "Sagar", "Sagar", "Paudel"]
    df = pd.DataFrame({"Names": words})
    po = Plot(df)
    po.wordcloud(x="Names")

    # CONFUSION MATRIX PLOT
    obj = CMPlot(mapping={1: "YES", 0: "NO", 2: "UNIDENTIFIED"},
                 report=True, plot=False)
    obj.fit_transform(y_true=pd.Series([1, 1, 1, 2, 0, 1, 0, 1]),
                      y_pred=pd.Series([0, 1, 0, 1, 2, 0, 0, 0]))

    obj = CMPlot(mapping={1: "YES", 0: "NO"}, report=True, plot=False)
    obj.fit_transform(y_true=pd.Series([1, 1, 1, 0, 0, 1, 0, 1]),
                      y_pred=pd.Series([0, 1, 0, 1, 0, 0, 0, 0]))

    # Descision Tree Plot
    from sklearn.datasets import load_wine
    from sklearn.tree import DecisionTreeClassifier
    data = load_wine()
    X = data.data
    y = data.target
    # class labels
    labels = data.feature_names
    class_names = ["0", "1", "2"]
    # print dataset description
    estimator = DecisionTreeClassifier()
    estimator.fit(X, y)
    dtp = DecisionTreePlot(show=True, save=True)
    dtp.plot(estimator, feature_names=labels, class_names=class_names)
