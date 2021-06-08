import pandas as pd
from diceLibrary.cascadeDatabase import cascadeDatabase
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier


class DecisionEngine:
    dB=None
    data=None
    funcNames = None
    def __init__(self):
        self.dB=cascadeDatabase()
        self.data=self.dB.getCascadeData()

    def prepareInput(self):
        self.data.at[0,'functionName']='func2'
        self.data.at[1,'functionName']='func2'
        one_hot = pd.get_dummies(self.data['functionName'])
        self.data=self.data.join(one_hot)
        self.funcNames=list(set(self.data['functionName']))
        self.data=self.data.drop(['functionName', 'runId'],axis=1)
        return self.data

    def getTestTrain(self, dataFrame):
        feature_cols = ['dataSize', 'runTime', 'batteryTime', 'latency', 'upload', 'download', 'ping', 'userCPU',
                        'systemCPU', 'idleCPU']
        feature_cols.extend(self.funcNames)
        X = dataFrame[feature_cols]
        Y = dataFrame.offloadStatus
        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.25, random_state=0)
        return X_train, X_test, y_train, y_test

    def logisticRegression(self):
        df_ohe = self.prepareInput()
        X_train,X_test,y_train,y_test=self.getTestTrain(df_ohe)
        logreg = LogisticRegression()
        # fit the model with data
        logreg.fit(X_train,y_train)
        y_pred=logreg.predict(X_test)
        print('end')

    def kNearestNeighbours(self):
        data = self.prepareInput()
        #data_scaled = StandardScaler().fit_transform(data)
        X_train,X_test,y_train,y_test=self.getTestTrain(data)
        k_range = range(1,3)
        scores_list = []
        for k in k_range:
            knn = KNeighborsClassifier(n_neighbors=k)
            knn.fit(X_train, y_train)
            y_pred = knn.predict(X_test)
            scores_list.append(metrics.accuracy_score(y_test, y_pred))

    def svm(self):
        data = self.prepareInput()
        X_train,X_test,y_train,y_test=self.getTestTrain(data)
        clf = svm.SVC(kernel='linear')
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)

    def decisionTree(self):
        data = self.prepareInput()
        X_train,X_test,y_train,y_test=self.getTestTrain(data)
        clf = DecisionTreeClassifier()
        clf = clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)

    def randomForest(self):
        data = self.prepareInput()
        X_train,X_test,y_train,y_test=self.getTestTrain(data)
        clf = RandomForestClassifier(n_estimators=100)
        clf.fit(X_train,y_train)
        y_pred = clf.predict(X_test)
        print(y_pred)


if __name__=="__main__":
    dc=DecisionEngine()
    #dc.logisticRegression()
    dc.randomForest()
    print("done")