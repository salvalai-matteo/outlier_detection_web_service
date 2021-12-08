import numpy as np

from ml_microservice.anomaly_detection import preprocessing
from ml_microservice.anomaly_detection import metrics

def test_naive_model():
    window_size = 3
    train = np.array([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20])
    test = np.array([20,21,22,23,24,25,100,27,28,29,30,100])
    
    preproc = preprocessing.Preprocessor(train=train, test=test, input_width=window_size)

    naive = metrics.NaivePredictor()
    naive.compile(loss="mse")
    #naive.fit(*preproc.train)
    X, y = preproc.extract_windows(test)
    y_naive = naive.predict(X)
    print(y_naive)
    assert len(y_naive.shape) == 2 and y_naive.shape[0] == preproc.test[0].shape[0] and y_naive.shape[1] == 1
    assert np.sum(y_naive - X[...,-1]) == 0
    y_naive0 = metrics.naive_prediction(X)
    assert all(y_naive - y_naive0 == 0)

def test_naive_metric():
    window_size = 3
    train = np.array([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20])
    test = np.array([20,21,22,23,24,25,100,27,28,29,30,100])
    
    preproc = preprocessing.Preprocessor(train=train, test=test, input_width=window_size)

    naive = metrics.NaivePredictor()
    naive.compile(loss="mse")
    #naive.fit(*preproc.train)
    X_test, y_test = preproc.test
    y_naive = naive.predict(X_test)
    metric = metrics.naive_model_metric(X_test, y_test, y_naive)
    assert metric == 1
    alternative = metrics.naive_y_metric(y_test, y_naive, y_naive)
    assert alternative == 1

def test_naive_prediction():
    window_size = 3
    train = np.array([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20])
    test = np.array([20,21,22,23,24,25,100,27,28,29,30,100])
    
    preproc = preprocessing.Preprocessor(train=train, test=test, input_width=window_size)

    naive = metrics.NaivePredictor()
    naive.compile(loss="mse")
    X_test, y_test = preproc.test
    y_naive = naive.predict(X_test)
    print(y_naive)
    y_naive0 = metrics.naive_prediction(X_test)
    print(y_naive0)
    assert len(y_naive0) == len(y_naive)
    same = True
    for y, y0 in zip(y_naive, y_naive0):
        if y - y0 > .01:
            same = False
            break
    assert same
