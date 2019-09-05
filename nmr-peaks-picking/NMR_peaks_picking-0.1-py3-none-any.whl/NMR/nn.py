import numpy as np
import nmrglue as ng
from scipy import interpolate
from keras.models import Sequential
from keras.layers import Flatten, Dense, Dropout
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import cross_val_score, train_test_split, GridSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.pipeline import Pipeline
from keras.optimizers import SGD
from keras.constraints import maxnorm
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trydjango.settings")
django.setup()
from NMR.models import Spectrum


def neural_network(spectrum):
    feature = []
    label = []
    dic, data = ng.bruker.read_pdata(spectrum.file)
    for peak in spectrum.peak_set.all():
        if int(peak.id) % 2 != 0:

            y0 = peak.y0  # peak.y - yPad
            y1 = peak.y1  # peak.y + yPad
            x0 = peak.x0  # peak.x - xPad
            x1 = peak.x1  # peak.x + xPad

            d = data[y0:y1, x0:x1]
            d = d / data[peak.y, peak.x]
            y, x = np.linspace(0, 1, d.shape[0]), np.linspace(0, 1, d.shape[1])
            func = interpolate.interp2d(x, y, d, kind='linear')
            xnew = np.linspace(0, 1, 64)
            ynew = np.linspace(0, 1, 64)
            znew = func(xnew, ynew)
            feature.append(znew.ravel())
            if peak.isPeak:
                label.append("True")
            else:
                label.append("False")

    feature = np.array(feature)
    scaler = StandardScaler()
    feature = scaler.fit_transform(feature)
    encoder = LabelEncoder()
    encoder.fit(label)
    label = encoder.transform(label)

    X_train, X_test, Y_train, Y_test = train_test_split(feature, label, test_size=0.2, random_state=0)

    # baseline model
    def create_model():
        # create model
        model = Sequential()
        model.add(Dense(200, input_dim=4096, kernel_initializer='glorot_normal', activation='tanh',
                        kernel_constraint=maxnorm(5)))
        model.add(Dense(1, kernel_initializer='glorot_normal', activation='sigmoid'))
        optimizer = SGD(lr=0.1, momentum=0.4)
        # Compile model
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        return model

    estimator = (KerasClassifier(build_fn=create_model, batch_size=40, epochs=10, verbose=0))
    kfold = StratifiedKFold(n_splits=10, shuffle=True)
    results = cross_val_score(estimator, feature, label, cv=kfold)
    print("Results: %.2f%% (%.2f%%)" % (results.mean() * 100, results.std() * 100))


if __name__ == "__main__":
    spectrum = Spectrum.objects.get(name="test")
    neural_network(spectrum)

