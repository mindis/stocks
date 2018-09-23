import requests
import pandas as pd
import quandl
import math
import random
import os
import numpy as np
from sklearn import preprocessing, cross_validation, svm
from sklearn.linear_model import LinearRegression

def getStockData():
    stock = request.args.get('stock', default=None, type=None)
    quandl.ApiConfig.api_key = "qWcicxSctVxrP9PhyneG"
    allData = quandl.get('WIKI/'+stock)
    dataLength = 251
    allDataLength = len(allData)
    firstDataElem = math.floor(random.random()*(allDataLength-dataLength))
    mlData = allData[0:firstDataElem+dataLength]

    def FormatForModel(dataArray):
        dataArray = dataArray[['Adj. Open', 'Adj. High', 'Adj. Low', 'Adj. Close', 'Adj. Volume']]
        dataArray['HL_PCT'] = (dataArray['Adj. High'] - dataArray['Adj. Close']) / dataArray['Adj. Close'] * 100.0
        dataArray['PCT_change'] = (dataArray['Adj. Close'] - dataArray['Adj. Open']) / dataArray['Adj. Open'] * 100.0
        dataArray = dataArray[['Adj. Close', 'HL_PCT', 'PCT_change','Adj. Volume']]
        dataArray.fillna(-99999, inplace=True)
        return dataArray

    mlData = FormatForModel(mlData)

    forecast_col = 'Adj. Close'
    forecast_out = int(math.ceil(0.12*dataLength))

    mlData['label'] = mlData[forecast_col].shift(-forecast_out)
    mlData.dropna(inplace=True)

    X = np.array(mlData.drop(['label'],1))
    X = preprocessing.scale(X)
    X_data = X[-dataLength:]
    X = X[:-dataLength]
    data = mlData[-dataLength:]
    mlData = mlData[:-dataLength]
    y = np.array(mlData['label'])

    X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.3)

    clf = LinearRegression()
    clf.fit(X_train, y_train)
    accuracy = clf.score(X_test, y_test)

    prediction = clf.predict(X_data)
    data = data[['Adj. Close']]
    data = data.rename(columns={'Adj. Close':'EOD'})
    data['prediction'] = prediction[:]
    data = data.to_json(orient='table')
    return jsonify(data)