import pandas as pd
from diceLibrary.cascadeDatabase import cascadeDatabase
from diceLibrary.settings import InputType
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from pickle import load, dump

class DecisionEngine:
    dB=None
    data=None
    funcNames = None
    trainMode=False
    offload=False

    def __init__(self):
        self.dB=cascadeDatabase()
        self.data=self.dB.getCascadeData(train=True)

    def valsToConsider(self, ls):
        #indexes of input values that are of VALUE type NOT FILE TYPE
        ret=list()
        for idx,i in enumerate(ls):
            if i==InputType.VALUE.value:
                ret.append(idx)
        return ret

    def prepareInput(self):
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
        return self.data

    def getTestTrain(self, dataFrame):
        feature_cols = dataFrame.columns.values.tolist()
        feature_cols.remove('offload')
        feature_cols.remove('inputTypes')
        feature_cols.remove('inputValues')
        X = dataFrame[feature_cols]
        Y = dataFrame.offload
        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.25, random_state=0)
        return X_train, X_test, y_train, y_test, feature_cols

    def logisticRegression(self):
        df_ohe = self.prepareInput()
        X_train,X_test,y_train,y_test, colNames=self.getTestTrain(df_ohe)
        try:
           logreg = load(open('logreg.pkl', 'rb'))
        except:
            logreg = LogisticRegression()
            # fit the model with data
            logreg.fit(X_train,y_train)
            dump(logreg, open('logreg.pkl', 'wb'))
        y_pred = logreg.predict(X_test)
        return logreg, colNames

    def kNearestNeighbours(self):
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
        return knn, colNames

    def svm(self):
        data = self.prepareInput()
        X_train,X_test,y_train,y_test, colNames=self.getTestTrain(data)
        clf = svm.SVC(kernel='linear')
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        return clf

    def decisionTree(self):
        data = self.prepareInput()
        X_train,X_test,y_train,y_test, colNames=self.getTestTrain(data)
        clf = DecisionTreeClassifier()
        clf = clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        return clf

    def randomForest(self):
        data = self.prepareInput()
        X_train,X_test,y_train,y_test, colNames=self.getTestTrain(data)
        clf = RandomForestClassifier(n_estimators=100)
        clf.fit(X_train,y_train)
        y_pred = clf.predict(X_test)
        return clf

    def setOffload(self, ip: bool):
        self.offload=ip

    def setTrainMode(self, ip: bool):
        self.trainMode=ip

    def getTrainMode(self):
        return self.trainMode

    def decide(self):
        if self.trainMode:
            return self.offload
        else:
            dc = DecisionEngine()
            alg, colNames = dc.logisticRegression()
            ipTypes = '1'
            ipValues = '5'
            dataSize = 2000
            batteryStartTime = 4200
            upload = 103
            download = 103
            funcName = 'myFunc'
            result = dc.predict(alg, ipTypes, ipValues, dataSize, batteryStartTime, upload, download, funcName,
                                colNames)
            return result

    def predict(self, alg, ipTypes, ipValues, dataSize, batteryStartTime, upload, download, funcName, colNames):
        inputTypes=self.dB.toList(ipTypes)
        inputTypes=[int(x) for x in inputTypes]
        valsToConsider=self.valsToConsider(inputTypes)
        df={'dataSize':dataSize,'batteryStartTime':batteryStartTime,'upload':upload,'download':download, funcName:1}
        inputValues=self.dB.toList(ipValues)
        for idx,val in enumerate(inputValues):
            if idx in valsToConsider:
                try:
                    value=int(val)
                except:
                    value=len(val)
                df[funcName+str(idx)]=value
        for i in colNames:
            if i not in df.keys():
                df[i]=None
        df=pd.DataFrame(df, index=[0])
        result=alg.predict(df)
        return result[0]

if __name__=="__main__":
    dc=DecisionEngine()
    alg, colNames=dc.logisticRegression()
    ipTypes='1'
    ipValues='5'
    dataSize=2000
    batteryStartTime=4200
    upload=103
    download=103
    funcName='myFunc'
    result=dc.predict(alg, ipTypes, ipValues, dataSize, batteryStartTime, upload, download, funcName, colNames)
    print('res:',str(result))