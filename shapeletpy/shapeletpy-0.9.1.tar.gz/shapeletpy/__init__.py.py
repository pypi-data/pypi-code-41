from . import ShapeletClassifier
__all__ = ['ShapeletClassifier']
__version__ ='0.9.1'


INPUT_DIR = "./Datasets/"

# Function to plot bar graph
def plot_graph(Dictionary, mytitle, ytitle="Accuracy", prune=False):
    ys = sorted(Dictionary.values(), reverse=True)
    labels = sorted(Dictionary, key=Dictionary.get, reverse=True)
    xs = np.arange(len(labels))
    # Set title
    plt.figure(figsize=(15, 7))
    plt.title(mytitle, fontsize=15)
    plt.bar(xs, ys, align='center', color=getColors(len(xs)), tick_label=ys)
    plt.xticks(
        xs,
        labels)  #Replace default x-ticks with xs, then replace xs with labels
    plt.xlabel("Classifier Type")
    plt.yticks(ys)
    plt.ylabel(ytitle)
    plt.xticks(rotation=90)
    plt.tick_params(axis='y', which='major')
    # To ensure differences are scene start y value close to first value
    plt.ylim(bottom=ys[-1] - 0.01)
    # Prune y axis to avoid overlap
    if prune:
        new_y = []
        for i, y in enumerate(ys):
            if i == 0:
                prev = y
                new_y.append(prev)
                continue
            if (prev - y > 0.005):
                new_y.append(y)
            prev = y
        plt.yticks(new_y)
    plt.show()
