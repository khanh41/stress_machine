import pandas as pd
import numpy as np
import os
import sklearn.pipeline
import time
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectKBest
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import MinMaxScaler,StandardScaler
from sklearn.svm import SVC
from sklearn.externals import joblib

def root_directory():
    current_path = os.path.abspath(__file__)
    return os.path.abspath(os.path.join(current_path, os.pardir))
def data_directory():
    return os.path.join(root_directory(), "data")

def load_train_set():
    #Loading a hdf5 file is much much faster
    in_file = os.path.join(data_directory(), "final",  "train.csv")
    return pd.read_csv(in_file)
def load_test_set():
    #Loading a hdf5 file is much much faster
    in_file = os.path.join(data_directory(), "final",  "test.csv")
    return pd.read_csv(in_file)

def train_model():
    select = SelectKBest(k=10)
    train =load_train_set()
    test = load_test_set()
    target = 'condition'
    hrv_features = list(train)
    hrv_features = [x for x in hrv_features if x not in [target]]
  
    classifiers = [
                    #MultinomialNB(),
                    #SVC(C=20, kernel='rbf'),
                    RandomForestClassifier()
                 ]
    for clf in classifiers:
        count_time = time.time()
        X_train= train[hrv_features]
        y_train= train[target]
        X_test = test[hrv_features]
        y_test = test[target]
    
        name = str(clf).split('(')[0]
        """if 'multinomialnb'==name.lower():
            scaler = MinMaxScaler()
            scaler.fit(X_train)
            X_train = scaler.transform(X_train)
            X_test = scaler.transform(X_test)
        else:
            scaler = StandardScaler()
            scaler.fit(X_train)
            X_train = scaler.transform(X_train)
            X_test = scaler.transform(X_test)"""
        print(name)
        """steps = [('feature_selection', select),
             ('model', clf)]"""
        steps = [('scaler',StandardScaler()),
                 ('feature_selection', select),
             ('model', clf)]
        pipeline = sklearn.pipeline.Pipeline(steps)
        pipeline.fit(X_train, y_train)
        y_prediction = pipeline.predict(X_test)
        print("----------------------------{0}---------------------------".format(name))
        print(sklearn.metrics.classification_report(y_test, y_prediction))
        count_time = time.time() - count_time
        print("time: ",count_time)
        print()
        print()
        joblib.dump(pipeline, 'model_stress.pkl')
        print("done")
     
if __name__ == '__main__':
    train_model()
    
   


   
