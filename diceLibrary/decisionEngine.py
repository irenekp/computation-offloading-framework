import pandas as pd
from diceLibrary.cascadeDatabase import cascadeDatabase
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

class DecisionEngine:
    dB=None
    data=None
    def __init__(self):
        self.dB=cascadeDatabase()
        self.data=self.dB.getCascadeData()

    def prepareInput(self):
        self.data.at[0,'functionName']='func2'
        self.data.at[1,'functionName']='func2'
        one_hot = pd.get_dummies(self.data['functionName'])
        funcNames=list(set(self.data['functionName']))
        self.data=self.data.join(one_hot)
        self.data=self.data.drop(['functionName'],axis=1)
        feature_cols = ['dataSize', 'runTime', 'batteryTime', 'latency','upload','download','ping','userCPU','systemCPU','idleCPU']
        feature_cols.extend(funcNames)
        X = self.data[feature_cols]
        Y=self.data.offloadStatus
        X_train,X_test,y_train,y_test=train_test_split(X,Y,test_size=0.25,random_state=0)
        return X_train,X_test,y_train,y_test

    def logisticRegression(self):
        X_train,X_test,y_train,y_test=self.prepareInput()
        logreg = LogisticRegression()
        # fit the model with data
        logreg.fit(X_train,y_train)
        y_pred=logreg.predict(X_test)
        print('end')

if __name__=="__main__":
    dc=DecisionEngine()
    dc.logisticRegression()