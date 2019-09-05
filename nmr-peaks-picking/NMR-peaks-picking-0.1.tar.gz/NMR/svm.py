import pickle
from zipfile import ZipFile
import numpy as np
import nmrglue as ng
import matplotlib.pyplot as plt
from sklearn import svm, preprocessing
from scipy import interpolate
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report,accuracy_score, confusion_matrix, recall_score
from sklearn.model_selection import cross_val_score
from trydjango.settings import MEDIA_ROOT
from skimage.feature import hog
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trydjango.settings")
django.setup()
from NMR.models import Spectrum
from NMR.process import read_zip


# support vector machine
def SVM(spectra):
    # create train abd test data container
    hog_features = []
    labels = []
    csv_feature = []
    # feature extraction
    for spectrum in spectra:
        dic, data, path = read_zip(spectrum.spectrum_file)
        for peak in spectrum.peak_set.all():
            # consider only fixed area peaks
            if int(peak.id) % 2 != 0:

                y0 = peak.y0
                y1 = peak.y1
                x0 = peak.x0
                x1 = peak.x1

                # slice data
                d = data[y0:y1, x0:x1]
                # normalise data
                d = d / data[peak.y, peak.x]

                # apple bilinear interpolation to 96*96
                x, y = np.linspace(0, 1, d.shape[1]), np.linspace(0, 1, d.shape[0])
                func = interpolate.interp2d(x, y, d, kind='linear')
                xnew = np.linspace(0, 1, 96)
                ynew = np.linspace(0, 1, 96)
                znew = func(xnew, ynew)
                # extract hog feature
                fd = hog(znew, orientations=9, pixels_per_cell=(8, 8),
                            cells_per_block=(2, 2), block_norm="L2", feature_vector=True)
                hog_features.append(fd)
                if peak.isPeak:
                    labels.append("True")
                    csv_feature.append(znew.ravel())
                else:
                    labels.append("False")
                    csv_feature.append(znew.ravel())

    #np.savetxt('output.csv', csv_feature, delimiter=',', fmt='%f')
    #np.savetxt('label.csv', labels, delimiter=',', fmt="%s")

    # processing data
    labels = np.array(labels).reshape(len(labels), 1)
    hog_features = np.array(hog_features)
    # build svc model
    clf = svm.SVC(C=10, kernel='rbf', class_weight='balanced', gamma=0.01, probability=True)
    # split into training and testing dataset
    x_train, x_test, y_train, y_test = train_test_split(hog_features, labels, test_size=0.3, random_state=0)
    """
    # grid search the best parameters set
    tuned_parameters = [{'kernel': ['rbf'], 'gamma': [1e-2, 1e-3, 1e-4, 1e-5],
                         'C': [0.001, 0.10, 0.1, 10, 25, 50, 100, 1000]},
                        {'kernel': ['sigmoid'], 'gamma': [1e-2, 1e-3, 1e-4, 1e-5],
                         'C': [0.001, 0.10, 0.1, 10, 25, 50, 100, 1000]},
                        {'kernel': ['linear'], 'C': [0.001, 0.10, 0.1, 10, 25, 50, 100, 1000]}
                        ]
    scores = ['accuracy', 'precision', 'recall', 'f1']
    for score in scores:
        print("# Tuning hyper-parameters for %s" % score)
        print()

        clf = GridSearchCV(svm.SVC(C=1), tuned_parameters, cv=3,
                           scoring='%s' % score)
        clf.fit(x_train, y_train.ravel())

        print("Best parameters set found on development set:")
        print()
        print(clf.best_params_)
        print()
        print("Grid scores on development set:")
        print()
        means = clf.cv_results_['mean_test_score']
        stds = clf.cv_results_['std_test_score']
        for mean, std, params in zip(means, stds, clf.cv_results_['params']):
            print("%0.3f (+/-%0.03f) for %r"
                  % (mean, std * 2, params))
    """
    # taing and predict
    clf.fit(x_train, y_train.ravel())
    train_pred = clf.predict(x_train)
    test_pred = clf.predict(x_test)
    # retrieve confidence for prediction
    class_probabilities = clf.predict_proba(hog_features)
    class_probabilities = class_probabilities[:, 1]
    predict = clf.predict(hog_features)
    # true negative, false positive, false negative, true positive
    tn, fp, fn, tp = confusion_matrix(labels, predict).ravel()
    count = 0
    # store the prediction into database
    for spectrum in spectra:
        for peak in spectrum.peak_set.all():
            if int(peak.id) % 2 != 0:
                peak.predict = predict[count]
                peak.probability = int(class_probabilities[count]*100)
                peak.save()
                o_peak = peak.get_the_other()
                o_peak.probability = int(class_probabilities[count] * 100)
                o_peak.save()
                count += 1
    # store the trained model for prediction
    file = "train_model.m"
    MODEL_ROOT = os.path.join(MEDIA_ROOT, 'model')
    path = os.path.join(MODEL_ROOT, file)
    try:
        os.remove(path)
    except OSError:
        pass
    with open(path, 'wb') as f:
        pickle.dump(clf, f)

    return np.round(accuracy_score(y_train, train_pred), 4), np.round(accuracy_score(y_test, test_pred), 4), tn, fp, fn, tp


# use pre-trained model to predict
def pred(spectrum, path):
    hog_features = []
    labels = []
    # read in spectrum data
    with ZipFile(spectrum.spectrum_file) as zipfile:
        list = zipfile.namelist()
        p = os.path.join(MEDIA_ROOT, "spectrum")
        p = os.path.join(p, list[0])
        dic, data = ng.bruker.read_pdata(p)
    # if peak data available, produce confusion matrix(evaluate True)
    evaluate = False
    if spectrum.count_peak() > 0:
        evaluate = True

    # feature extraction
    for peak in spectrum.peak_set.all():
        if int(peak.id) % 2 != 0:

            y0 = peak.y0
            y1 = peak.y1
            x0 = peak.x0
            x1 = peak.x1

            d = data[y0:y1, x0:x1]
            d = d / data[peak.y, peak.x]
            y, x = np.linspace(0, 1, d.shape[0]), np.linspace(0, 1, d.shape[1])
            func = interpolate.interp2d(x, y, d, kind='linear')
            xnew = np.linspace(0, 1, 96)
            ynew = np.linspace(0, 1, 96)
            znew = func(xnew, ynew)
            fd = hog(znew, orientations=9, pixels_per_cell=(8, 8),
                    cells_per_block=(2, 2), block_norm="L2", feature_vector=True)
            hog_features.append(fd)
            if peak.isPeak and evaluate:
                labels.append("True")

            elif not peak.isPeak and evaluate:
                labels.append("False")

    hog_features = np.array(hog_features)
    labels = np.array(labels).reshape(len(labels), 1)
    # read the trained model and predict
    with open(path, 'rb') as f:
        model = f.read()
        clf = pickle.loads(model)
        predict = clf.predict(hog_features)
        class_probabilities = clf.predict_proba(hog_features)
        class_probabilities = class_probabilities[:, 1]
        count = 0
        # store the prediction in database
        for peak in spectrum.peak_set.all():
            if int(peak.id) % 2 != 0:
                peak.predict = predict[count]
                peak.probability = int(class_probabilities[count]*100)
                peak.save()
                o_peak = peak.get_the_other()
                o_peak.probability = int(class_probabilities[count] * 100)
                o_peak.save()
                count += 1
    # return confusion matrix
    if evaluate:
        tn, fp, fn, tp = confusion_matrix(labels, predict).ravel()
        acc = np.round(accuracy_score(labels, predict), 4)
        return acc, tn, fp, fn, tp
    else:
        return -1, -1, -1, -1, -1


if __name__ == "__main__":
    # search for the best fixed size
    xPad = [14, 15, 16, 17, 18, 19, 20, 21]
    yPad = [1, 2, 3, 4, 5, 6, 7]
    train = []
    test = []
    for i in xPad:
        for j in yPad:
            a1, a2, a, b, c, d = SVM(Spectrum.objects.all(), i, j)
            train.append(a1)
            test.append(a2)
    fig = plt.figure(figsize=(18, 12))
    plt.plot([i for i in range(len(train))], train,  '--', label="training accuracy")
    plt.plot([i for i in range(len(test))], test,  '--', label="testing accuracy")
    for x, y in zip([i for i in range(len(test))], test):
        plt.text(x, y, str(np.round(y, 3)), color="red", fontsize=12)
    plt.grid()
    plt.xlabel("Peak size")
    plt.ylabel("Accuracy")
    plt.xticks(rotation=90)
    plt.xticks(range(len(test)), [str(i*2)+'*'+str(j*2) for i in xPad for j in yPad])
    fig.savefig('size.png')