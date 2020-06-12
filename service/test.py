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
def load_test_set():
    #Loading a hdf5 file is much much faster
    in_file = os.path.join(data_directory(), "",  "data_user.csv")
    return pd.read_csv(in_file)

def test_model():
    test = load_test_set()
    target = 'condition'
    hrv_features = list(test)
    hrv_features = [x for x in hrv_features if x not in [target]]
    X_test = test[hrv_features]
    y_test = test[target]
    pipeline = joblib.load('model_stress.pkl')
    y_prediction = pipeline.predict(X_test)
    print(sklearn.metrics.classification_report(y_test, y_prediction))
    
if __name__ == '__main__':
    test_model()
    
   


   
