#!/usr/bin/env python
# coding: utf-8


from collections import OrderedDict
import json
import os
import time as time
import pandas as pd
import numpy as np
import datetime
import logging
import sys
# To save intermediate results in binary format
import pickle
# To use multiprocessing on functions with more than 1 parameter
# Create folders + path access
import os
os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
from GRAAF.utils import *

import matplotlib.pyplot as plt

from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC, LinearSVC
os.environ['KMP_DUPLICATE_LIB_OK']='True'
from sklearn.calibration import CalibratedClassifierCV
from xgboost import XGBClassifier
from numpy import loadtxt
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, precision_recall_curve, roc_auc_score, roc_curve, f1_score
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import RandomOverSampler, SMOTE, ADASYN
#import scikitplot as skplt

from scikitplot.metrics import plot_lift_curve, plot_cumulative_gain, plot_roc, plot_precision_recall



class XGB:

    def __init__(self, training_embeddings, test_embeddings, output_path = "", sampling_ratio=0, sampling_algorithm="", SCALING="", WORKERS=3, scale_pos_weight=1):

        st = time.time()
        
        X_train, y_train = preprocessing(training_embeddings, sampling_ratio=sampling_ratio, SCALING=SCALING, sampling_algorithm=sampling_algorithm)
        X_test, y_test = preprocessing(test_embeddings, SCALING=SCALING)

        model = XGBClassifier(n_jobs=WORKERS, scale_pos_weight=scale_pos_weight)
        model.fit(X_train, y_train)
        self.model = model

        # Create class containing all scoring methods
        self.scores = Test(self.model, X_test, y_test)
    
        #Signal completion
        ed = time.time()
        print("Finished: ", os.getpid())
        print("Runtime of process ", os.getpid(), " was ", (ed-st))


class Test:

    def __init__(self, model, X_test, y_test):

        self.pred_prob = model.predict_proba(X_test)[:, 1]
        self.y_pred = model.predict(X_test)
        self.y_test = y_test

    def get_auc_score(self):
        try:
            self.auc = roc_auc_score(self.y_test, self.pred_prob)
        except:
            self.auc = "undefined"
        return self.auc

    def get_f1_score(self):
        try:
            self.f1 = f1_score(self.y_test, self.y_pred)
        except:
            self.f1 = "undefined"
        return self.f1

    def get_lift_score(self, percentage=0.1):

        ###LIFT SCORE###
        cols = ['ACTUAL', 'PROB_POSITIVE', 'PREDICTED']
        data = [self.y_test, self.pred_prob, self.y_pred]
        df = pd.DataFrame(dict(zip(cols, data)))

        # Observations where y=1
        total_positive_n = df['ACTUAL'].sum()
        # Total Observations
        total_n = df.index.size
        natural_positive_prob = total_positive_n / float(total_n)

        # Sort values and take top x%
        df_sorted = df.sort_values('PROB_POSITIVE', ascending=False).iloc[:int(np.round(percentage * total_n))]
        lift_positive = ((df_sorted['PREDICTED'] & df_sorted['ACTUAL']).sum()) / (total_positive_n)
        percentage = ((df_sorted['ACTUAL'].count()) / float(total_n))
        self.lift_index_positive = lift_positive / percentage  # (lift_positive/natural_positive_prob) #*100

        return self.lift_index_positive

    def get_confusion_matrix(self):

        try:
            self.conf_matrix = confusion_matrix(self.y_test, self.y_pred)
        except:
            self.conf_matrix = "undefined"
        return self.conf_matrix

    def get_sensitivity(self):
        try:
            tn, fp, fn, tp = self.get_confusion_matrix().ravel()
            self. sensitivity = tp / (tp + fn)
        except:
            self.sensitivity = "undefined"
        return self.sensitivity

    def get_specificity(self):
        try:
            tn, fp, fn, tp = self.get_confusion_matrix().ravel()
            self.specificity = tn / (tn + fp)
        except:
            self.specificity = "undefined"
        return self.specificity

    def get_roc_curve(self, title="ROC Curve"):

        try:
            fpr, tpr, thresholds = roc_curve(self.y_test, self.pred_prob)
            plot_roc_curve(fpr, tpr, title)
        except:
            "issues"

    def get_precision_recall_curve(self):

        precisions, recalls, thresholds = precision_recall_curve(y_test, pred_prob)
        plot_precision_recall_vs_threshold(precisions, recalls, thresholds)

    def get_sensitivity_specificity_vs_threshold(self):

        fpr, tpr, thresholds = roc_curve(self.y_test, self.pred_prob)
        plot_sensitivity_specificity_vs_threshold(tpr, fpr, thresholds)

    def set_threshold(self, threshold=0.5):
        self.y_pred = self.pred_prob > threshold

    def set_optimal_threshold(self, model, X_val, y_val):
        """
        Set optimal threshold based on a validation dataset
        """
        pred_prob = model.predict_proba(X_val)[:, 1]
        self.optimal_threshold = search(pred_prob, y_val)
        self.set_threshold(self.optimal_threshold)
        return(self.optimal_threshold)



def plot_sensitivity_specificity_vs_threshold(tpr, fpr, thresholds):
    """
    Modified from:
    Hands-On Machine learning with Scikit-Learn
    and TensorFlow; p.89
    """
    plt.figure(figsize=(8, 8))
    plt.title("Precision and Recall Scores as a function of the decision threshold")
    plt.plot(thresholds, tpr, "b--", label="sensitivity")
    plt.plot(thresholds, 1-(fpr), "g-", label="specificity")
    plt.xlim([0.0, 1.0])
    plt.ylabel("Score")
    plt.xlabel("Decision Threshold")
    plt.legend(loc='best')
    plt.show()

def plot_precision_recall_vs_threshold(precisions, recalls, thresholds):
    """
    Modified from:
    Hands-On Machine learning with Scikit-Learn
    and TensorFlow; p.89
    """
    plt.figure(figsize=(8, 8))
    plt.title("Precision and Recall Scores as a function of the decision threshold")
    plt.plot(thresholds, precisions[:-1], "b--", label="Precision")
    plt.plot(thresholds, recalls[:-1], "g-", label="Recall")
    plt.xlim([0.0, 1.0])
    plt.ylabel("Score")
    plt.xlabel("Decision Threshold")
    plt.legend(loc='best')
    plt.show()

def testing(model, X_test, y_test):

    pred_prob = model.predict_proba(X_test)[:,1]
    y_pred = model.predict(X_test)
    auc_lr = roc_auc_score(y_test, pred_prob)
    f1_lr = f1_score(y_test, y_pred)
    fpr, tpr, thresholds = roc_curve(y_test, pred_prob)
    p, r, pr_thresholds = precision_recall_curve(y_test, pred_prob)

    conf_matrix = confusion_matrix(y_test, y_pred)
    #optimal_idx = np.argmax(np.abs(tpr - fpr))
    #optimal_threshold = thresholds[optimal_idx]
    #print("optimal threshold: ", optimal_threshold)
    #preds = np.where(pred_prob > THRESHOLD, 1, 0)

    #f1_bis = f1_score(y_test, preds)
    #print("F1: ", f1_bis)

    ###LIFT SCORE###
    cols = ['ACTUAL','PROB_POSITIVE','PREDICTED']
    data = [y_test,pred_prob,y_pred]
    df = pd.DataFrame(dict(zip(cols,data)))
    #print(df.tail(5))

    #Observations where y=1
    total_positive_n = df['ACTUAL'].sum()
    #print("Total fraud cases: ", total_positive_n)
    #Total Observations
    total_n = df.index.size
    natural_positive_prob = total_positive_n/float(total_n)

    #Sort values and take top 10%
    df_sorted = df.sort_values('PROB_POSITIVE', ascending=False).iloc[:int(np.round(0.1*total_n))]
    #print("total number in sample: ", df_sorted['PREDICTED'].count())
    #print("total correctly predicted: ", (df_sorted['PREDICTED'] & df_sorted['ACTUAL']).sum() )
    lift_positive = ((df_sorted['PREDICTED'] & df_sorted['ACTUAL']).sum())/(total_positive_n)
    percentage = ((df_sorted['ACTUAL'].count())/float(total_n))
    #print("pecentage: ", percentage)
    #print("percentage of total fraud in 10% : ", lift_positive)
    lift_index_positive = lift_positive/percentage   #(lift_positive/natural_positive_prob) #*100
    #if(lift_index_positive > 10):
        #print(lift_index_positive)

    ### Visualization ###
    f, (ax1, ax2, ax3, ax4) = plt.subplots(4,1, figsize=(5,20))
    y_pred_graphs = model.predict_proba(X_test)
    plot_lift_curve(y_test, y_pred_graphs, title='Lift Curve', ax=ax1)
    plot_cumulative_gain(y_test, y_pred_graphs, ax=ax2)
    plot_roc(y_test, y_pred_graphs, plot_micro=False, plot_macro=False, classes_to_plot=[True], ax=ax3)
    plot_precision_recall(y_test, y_pred_graphs, ax=ax4)
    ### --- ###

    return (auc_lr, f1_lr, lift_index_positive, fpr, tpr, thresholds, f, conf_matrix, p, r, pr_thresholds)

def preprocessing(df, sampling_ratio=0, SCALING="", sampling_algorithm=""):


    try:
        df = df.drop(["scores_ST","scores_MT","scores_LT"], axis=1)
    except:
        pass

    X_train = df.drop(["transaction", "client", "merchant", "category","country","amount","timestamp","fraud"], axis=1).values

    if SCALING == 'min_max_scaler':
        min_max_scaler = preprocessing.MinMaxScaler()
        X_train = min_max_scaler.fit_transform(X_train)
    elif SCALING == 'standard_scaler':
        standard_scaler = StandardScaler()
        X_train = standard_scaler.fit_transform(X_train)

    y_train = df.fraud

    if sampling_ratio:
        if sampling_algorithm == "RandomOverSampler":

            ros = RandomOverSampler(sampling_strategy=(1/sampling_ratio), random_state=0)
            X_train, y_train = ros.fit_resample(X_train, y_train)
        elif sampling_algorithm == "SMOTE":

            smote = SMOTE(sampling_strategy=(1/sampling_ratio))
            X_train, y_train = smote.fit_resample(X_train, y_train)
        elif sampling_algorithm == "ADASYN":

            adasyn = ADASYN(sampling_strategy=(1/sampling_ratio))
            X_train, y_train = adasyn.fit_resample(X_train, y_train)

        elif sampling_algorithm == "undersampling":
            non_fraud_indices = df[df.fraud == False].index
            sample_size = int(np.round(np.sum(df.fraud == True) * sampling_ratio))
            random_indices = np.random.choice(non_fraud_indices, sample_size, replace=False)
            non_fraud_sample = df.loc[random_indices]
            fraud_sample = df[df.fraud == True]

            df = pd.concat([non_fraud_sample, fraud_sample])
            df = df.sample(frac=1)

            X_train = df.drop(
                ["transaction", "client", "merchant", "category", "country", "amount", "timestamp", "fraud"],
                axis=1).values
            y_train = df.fraud



    return (X_train, y_train)

def logger(filename, aucs, f1s, lifts):
    logs = OrderedDict()
    logs["auc"] = aucs

    logs["f1"] = f1s
    logs["lift@10%"] = lifts
    #logs["number_of_fraud_cases_train"] = fraudcasestrain
    #logs["number_of_fraud_cases test"] = fraudcasestest

    print("saving file")
    with open(filename+'.json', 'w') as out:
        json.dump(logs, out)
        out.close()


def search(pred_prob, y_test, depth=6):
    """
    :param pred_prob: predicted probabilities
    :param y_test: test set labels
    :param depth: precision of optimal threshold (number of decimals)
    :return: optimal threshold maximizing the sum of specificity and sensitivity
    """
    
    fpr, tpr, thresholds = roc_curve(y_test, pred_prob)
    sensitivities = tpr
    specificities = (1-fpr)
    
    #find threshold with smallest difference:
    best_index = np.argmin(np.abs(sensitivities-specificities))
    optimal_threshold = thresholds[best_index]
    best_sum = sensitivities[best_index]+specificities[best_index]
    
    best_positive_index = best_index
    while (sensitivities[best_positive_index+1] >= sensitivities[best_positive_index])&(specificities[best_positive_index+1] >= specificities[best_positive_index]):
        best_positive_index = best_positive_index+1
        
        if sensitivities[best_positive_index]+specificities[best_positive_index] > best_sum:
            optimal_threshold = thresholds[best_positive_index]
            best_sum = sensitivities[best_positive_index]+specificities[best_positive_index]
    
    best_negative_index = best_index
    while (sensitivities[best_negative_index-1] >= sensitivities[best_negative_index])&(specificities[best_negative_index-1] >= specificities[best_negative_index]):
        best_negative_index = best_negative_index-1
        if sensitivities[best_negative_index]+specificities[best_negative_index] > best_sum:
            optimal_threshold = thresholds[best_negative_index]
            best_sum = sensitivities[best_negative_index]+specificities[best_negative_index]
    
    
    #last_best = 0
    #new_best = 1
    #current_high = 0
    #lower = 0
    #upper = 1
    #for j in range(1, depth):
        #step = 1 / (10 ** j)
        #for threshold in np.arange(lower, upper, step=step):
            #y_pred = pred_prob > threshold
           # tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
            #specificity = tn / (tn + fp)
            #sensitivity = tp / (tp + fn)

            #if specificity + sensitivity > current_high:
                #current_high = specificity * sensitivity
                #last_best = new_best
                #new_best = threshold

        #lower = new_best - step
        #upper = new_best + step

    return optimal_threshold

def plot_roc_curve(fpr, tpr, title="ROC Curve"):
    plt.figure()
    plt.plot(fpr, tpr, color='darkorange', label='ROC curve' )
    plt.plot([0, 1], [0, 1], color='navy', linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(title)
    plt.legend(loc="lower right")
    plt.show()

