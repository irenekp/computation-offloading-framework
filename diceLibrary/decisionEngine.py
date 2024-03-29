import pandas as pd
from pandas import Series
from sklearn.preprocessing import Normalizer

from diceLibrary.cascadeDatabase import cascadeDatabase
from diceLibrary.settings import InputType, findClosest
from sklearn import metrics
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from pickle import load, dump
from sklearn.metrics import accuracy_score
import logging
from diceLibrary.settings import DecisionEngineConfig
from statistics import mode
import sys
from scipy.spatial import distance
import numpy as np

class cascade:
    de=None
    cascadeData=None
    corrMap=dict()
    def __init__(self, de):
        self.de=de
        self.cascadeData=de.prepareInput()

    def getCols(self):
        cols=list(self.cascadeData.columns)
        cols.remove('offload')
        cols.remove('inputTypes')
        cols.remove('inputValues')
        return cols

    def oldCascade(self, df, funcName, ipVals):
        x=self.cascadeData[self.cascadeData[funcName]==1]
        x=x[x['inputTypes']==df['inputTypes'][0]]
        offload=x[x['offload']==1]
        local=x[x['offload']==0]
        i=ipVals[0]
        arr=list(offload[i])
        closest=findClosest(arr, len(arr), df.loc[0,ipVals][0])
        rt=list(offload[offload[i]==closest]['runTime'])
        sumOffloadRt=sum(rt)/len(rt)
        arr=list(local[i])
        closest=findClosest(arr, len(arr), df.loc[0,ipVals][0])
        rt=list(local[local[i]==closest]['runTime'])
        sumLocalRt=sum(rt)/len(rt)
        if sumLocalRt>sumOffloadRt:
            return [1]
        else:
            return [0]

    def getDistance(self, row1, row2, funcName, ipVals):
        distance=0
        result=0
        vals = row2.drop([funcName, 'inputTypes'], axis=1)
        vals.fillna(0, inplace=True)
        vals = vals.astype(float)
        vals = vals.div(vals.sum(axis=1), axis=0)

        vals_db=Series.to_frame(row1).T
        vals_db = vals_db[['upload', 'download', 'batteryStartTime', 'dataSize']]
        for col in ipVals:
            vals_db[col] = row1[col]
        vals_db.fillna(0, inplace=True)
        vals_db = vals_db.astype(float)
        vals_db = vals_db.div(vals_db.sum(axis=1), axis=0)

        if row1[funcName]==1 and row1['inputTypes']==str(row2['inputTypes'][0]):
            for col in ipVals:
                #Euclidean distance taken for each row
                distance += np.linalg.norm(float(vals[col]) - float(vals_db[col]))
            if row1['batteryStartTime'] != 0 and row2['batteryStartTime'][0] != 0:
                distance+= np.linalg.norm(float(vals['batteryStartTime']) - float(vals_db['batteryStartTime']))
            if row1['upload'] != 0 and row2['upload'][0] != 0:
                distance+=np.linalg.norm(float(vals['upload']) - float(vals_db['upload']))
            if row1['download'] != 0 and row2['download'][0] != 0:
                distance+=np.linalg.norm(float(vals['download']) - float(vals_db['download']))
            if row1['dataSize'] != 0 and row2['dataSize'][0] != 0:
                distance+= np.linalg.norm(float(vals['dataSize']) - float(vals_db['dataSize']))
        else:
            return sys.maxsize,row1['offload']
        return distance, row1['offload']

    def predict(self, df, funcName, ipVals, old=False):
        if not old:
            if funcName not in self.corrMap:
                fDf=self.cascadeData[self.cascadeData[funcName]==1]
                var=dict()
                for col in ipVals:
                    var[col]=fDf[col].corr(fDf['runTime'])
                self.corrMap[funcName]=var
            distance=0
            mindist=sys.maxsize
            minres=0

            for idx, row in self.cascadeData.iterrows():
                dist, res=self.getDistance(row,df, funcName, ipVals)
                if dist<mindist:
                    mindist=dist
                    minres=res
            return [minres]
        else:
            return self.oldCascade(df, funcName, ipVals)

class DecisionEngine:
    dB=None
    data=None
    funcNames = None
    trainMode=False
    offload=False
    log=None
    decEng = None
    preparedInput=None
    def __init__(self, decEng):
        self.dB=cascadeDatabase()
        self.data=self.dB.getCascadeData(train=True)
        self.preparedInput=None
        self.log=logging.getLogger()
        self.decEng=decEng

    def valsToConsider(self, ls):
        #indexes of input values that are of VALUE type NOT FILE TYPE
        ret=list()
        for idx,i in enumerate(ls):
            if i==InputType.VALUE.value:
                ret.append(idx)
        return ret


    def prepareInput(self):
        if self.preparedInput is not None:
            return self.preparedInput
        one_hot = pd.get_dummies(self.data['functionName'])
        self.data=self.data.join(one_hot)
        self.funcNames=list(set(self.data['functionName']))
        self.data=self.data.drop(['functionName'],axis=1)
        finalDf=self.data.copy()
        for f in self.funcNames:
            funcDf=self.data[self.data[f]==1]
            inputTypes=set(funcDf['inputTypes'])
            inputTypes= next(iter(inputTypes))
            inputTypes=self.dB.toList(inputTypes)
            inputTypes=[int(x) for x in inputTypes]
            valsToConsider=self.valsToConsider(inputTypes)
            finalDf = finalDf.reindex(finalDf.columns.tolist() + [f+str(i) for i in valsToConsider], axis=1)
        for f in self.funcNames:
            funcDf=self.data[self.data[f]==1]
            inputTypes=set(funcDf['inputTypes'])
            inputTypes= next(iter(inputTypes))
            inputTypes=self.dB.toList(inputTypes)
            inputTypes=[int(x) for x in inputTypes]
            valsToConsider=self.valsToConsider(inputTypes)
            for idx,row in funcDf.iterrows():
                inputValues=self.dB.toList(row['inputValues'])
                for i,val in enumerate(inputValues):
                    if i in valsToConsider:
                        try:
                            value=int(val)
                        except:
                            value=len(val)
                        finalDf.loc[finalDf['id'] ==row['id'], f+str(i)]=value
        finalDf=finalDf.drop(['id'],axis=1)
        self.data=finalDf.copy()
        self.preparedInput=self.data
        return self.data

    def getTestTrain(self, dataFrame):
        feature_cols = dataFrame.columns.values.tolist()
        feature_cols.remove('offload')
        feature_cols.remove('inputTypes')
        feature_cols.remove('inputValues')
        feature_cols.remove('runTime')
        dataFrame.fillna(dataFrame.mean(), inplace=True)
        dataFrame.fillna(0, inplace=True)
        X = dataFrame[feature_cols]
        Y = dataFrame.offload
        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.25, random_state=0)
        return X_train, X_test, y_train, y_test, feature_cols

    def getXY(self, dataFrame):
        #no test train
        feature_cols = dataFrame.columns.values.tolist()
        feature_cols.remove('offload')
        feature_cols.remove('inputTypes')
        feature_cols.remove('inputValues')
        feature_cols.remove('runTime')
        dataFrame.fillna(dataFrame.mean(), inplace=True)
        dataFrame.fillna(0, inplace=True)
        X = dataFrame[feature_cols]
        Y = dataFrame.offload
        return X,Y, feature_cols

    def writeList(self, ls, path):
        textfile = open(path, "w")
        for element in ls:
            textfile.write(element + "\n")
        textfile.close()

    def readList(self, path):
        # open file in read mode
        with open(path, 'r') as file_handle:
            # read file content into list
            lines = file_handle.readlines()
        # print list content
        print(lines)
        lines=[line.strip() for line in lines]
        return lines

    def logisticRegression(self, test=False):
        try:
           logreg = load(open('Trails/logreg.pkl', 'rb'))
           colNames=self.readList('Trails/logreg.txt')
        except:
            df_ohe = self.prepareInput()
            logreg = LogisticRegression()
            if test:
                X_train,X_test,y_train,y_test,colNames=self.getTestTrain(df_ohe)
                # fit the model with data
                logreg.fit(X_train,y_train)
                dump(logreg, open('Trails/logreg.pkl', 'wb'))
                self.writeList(colNames, 'Trails/logreg.txt')
                y_pred=logreg.predict(X_test)
                acc=accuracy_score(y_test, y_pred)
                self.log.info('Logistic Regression Model Trained with Accuracy: '+str(acc))
            else:
                X,y,colNames=self.getXY(df_ohe)
                logreg.fit(X,y)
                dump(logreg, open('Trails/logreg.pkl', 'wb'))
                self.writeList(colNames, 'Trails/logreg.txt')
        return logreg, colNames

    def knn(self):
        try:
            knn = load(open('Trails/knn.pkl', 'rb'))
            colNames=self.readList('Trails/knn.txt')
        except:
            data = self.prepareInput()
            #data_scaled = StandardScaler().fit_transform(data)
            X_train,X_test,y_train,y_test, colNames=self.getTestTrain(data)
            k_range = range(1,3)
            scores_list = []
            for k in k_range:
                knn = KNeighborsClassifier(n_neighbors=k)
                knn.fit(X_train, y_train)
                y_pred = knn.predict(X_test)
                scores_list.append(metrics.accuracy_score(y_test, y_pred))
            dump(knn, open('Trails/knn.pkl', 'wb'))
            self.writeList(colNames, 'Trails/knn.txt')
        return knn, colNames

    def svm(self, test=False):
        try:
            svmM = load(open('Trails/svm.pkl', 'rb'))
            colNames=self.readList('Trails/svm.txt')
        except:
            df_ohe = self.prepareInput()
            svmM = svm.SVC(kernel='linear')
            if test:
                X_train,X_test,y_train,y_test,colNames=self.getTestTrain(df_ohe)
                # fit the model with data
                svmM.fit(X_train,y_train)
                dump(svmM, open('Trails/svm.pkl', 'wb'))
                self.writeList(colNames, 'Trails/svm.txt')
                y_pred=svmM.predict(X_test)
                acc=accuracy_score(y_test, y_pred)
                self.log.info('Support Vector Machine Model Trained with Accuracy: '+str(acc))
            else:
                X,y,colNames=self.getXY(df_ohe)
                svmM.fit(X,y)
                dump(svmM, open('Trails/svm.pkl', 'wb'))
                self.writeList(colNames, 'Trails/svm.txt')
        return svmM, colNames

    def decisionTree(self, test=False):
        try:
            dtm = load(open('Trails/dtm.pkl', 'rb'))
            colNames=self.readList('Trails/dtm.txt')
        except:
            df_ohe = self.prepareInput()
            dtm = DecisionTreeClassifier()
            if test:
                X_train,X_test,y_train,y_test,colNames=self.getTestTrain(df_ohe)
                # fit the model with data
                dtm.fit(X_train,y_train)
                dump(dtm, open('Trails/dtm.pkl', 'wb'))
                self.writeList(colNames, 'Trails/dtm.txt')
                y_pred=dtm.predict(X_test)
                acc=accuracy_score(y_test, y_pred)
                self.log.info('Decision Tree Model Trained with Accuracy: '+str(acc))
            else:
                X,y,colNames=self.getXY(df_ohe)
                dtm.fit(X,y)
                dump(dtm, open('Trails/dtm.pkl', 'wb'))
                self.writeList(colNames, 'Trails/dtm.txt')
        return dtm, colNames

    def randomForest(self, test=False):
        try:
            rfm = load(open('Trails/rfm.pkl', 'rb'))
            colNames=self.readList('Trails/rfm.txt')
        except:
            df_ohe = self.prepareInput()
            rfm = RandomForestClassifier()
            if test:
                X_train,X_test,y_train,y_test,colNames=self.getTestTrain(df_ohe)
                # fit the model with data
                rfm.fit(X_train,y_train)
                dump(rfm, open('Trails/rfm.pkl', 'wb'))
                self.writeList(colNames, 'Trails/rfm.txt')
                y_pred=rfm.predict(X_test)
                acc=accuracy_score(y_test, y_pred)
                self.log.info('Random Forest Model Trained with Accuracy: '+str(acc))
            else:
                X,y,colNames=self.getXY(df_ohe)
                rfm.fit(X,y)
                dump(rfm, open('Trails/rfm.pkl', 'wb'))
                self.writeList(colNames, 'Trails/rfm.txt')
        return rfm, colNames

    def setOffload(self, ip: bool):
        self.offload=ip

    def setTrainMode(self, ip: bool):
        self.trainMode=ip

    def getTrainMode(self):
        return self.trainMode

    def decide(self, ipTypes, ipValues, dataSize, batteryStartTime, upload, download, funcName):
        if self.trainMode:
            return self.offload
        else:
            algs=list()
            cNs=list()
            result=list()
            if DecisionEngineConfig.LOGREG in self.decEng:
                alg, colNames = self.logisticRegression()
                algs.append(alg)
                cNs.append(colNames)
            if DecisionEngineConfig.SVM in self.decEng:
                alg, colNames = self.svm()
                algs.append(alg)
                cNs.append(colNames)
            if DecisionEngineConfig.KNN in self.decEng:
                alg, colNames = self.knn()
                algs.append(alg)
                cNs.append(colNames)
            if DecisionEngineConfig.DECTREE in self.decEng:
                alg, colNames = self.decisionTree()
                algs.append(alg)
                cNs.append(colNames)
            if DecisionEngineConfig.RANDFRST in self.decEng:
                alg, colNames = self.randomForest()
                algs.append(alg)
                cNs.append(colNames)
            if DecisionEngineConfig.CASCADE in self.decEng:
                alg=cascade(self)
                colNames=alg.getCols()
                algs.append(alg)
                cNs.append(colNames)
            for idx, alg in enumerate(algs):
                result.append(self.predict(alg, ipTypes, ipValues, dataSize, batteryStartTime, upload, download, funcName,
                                    cNs[idx]))
            logRes='offload' if mode(result)==1 else 'local'
            self.log.info('The decision was made to: '+ logRes)
            return mode(result)

    def predict(self, alg, ipTypes, ipValues, dataSize, batteryStartTime, upload, download, funcName, colNames):
        inputTypes=self.dB.toList(ipTypes)
        inputTypes=[int(x) for x in inputTypes]
        valsToConsider=self.valsToConsider(inputTypes)
        inputValues=self.dB.toList(ipValues)
        df={'dataSize':dataSize,'batteryStartTime':batteryStartTime,'upload':upload,'download':download, funcName:1}
        ipVals=list()
        for idx,val in enumerate(inputValues):
            if idx in valsToConsider:
                try:
                    value=int(val)
                except:
                    value=len(val)
                df[funcName+str(idx)]=value
                ipVals.append(funcName+str(idx))
        for i in colNames:
            if i not in df.keys():
                df[i]=None
        keysToBeDeleted=list()
        for key in df.keys():
            if key not in colNames:
                keysToBeDeleted.append(key)
        for key in keysToBeDeleted:
            df.pop(key)
        if (isinstance(alg, cascade)):
            df['inputTypes']=ipTypes
            df=pd.DataFrame(df, index=[0])
            result=alg.predict(df, funcName, ipVals, False) #TRUE FOR OLD, FALSE FOR NEW -- RABBIT.
        else:
            df=pd.DataFrame(df, index=[0])
            df.fillna(0, inplace=True)
            result=alg.predict(df)
        logOp='offloading' if result[0]==1 else 'local'
        self.log.info(str(type(alg))+' predicted to execute by:'+logOp)
        return result[0]

if __name__=="__main__":
    dc=DecisionEngine([DecisionEngineConfig.CASCADE])
    ipTypes='1'
    ipValues='5'
    dataSize=2000
    batteryStartTime=4200
    upload=103
    download=103
    funcName='nQueens'
    result=dc.decide(ipTypes, ipValues, dataSize, batteryStartTime, upload, download, funcName)
    print('res:',str(result))