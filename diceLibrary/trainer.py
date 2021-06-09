from datetime import datetime
from diceLibrary.cascadeDatabase import cascadeDatabase
from diceLibrary.settings import ProfilerConfig
from sklearn import preprocessing
import logging
class Trainer:
    log=None
    decisionEngine=None
    def __init__(self, decisionEngine):
        self.log=logging.getLogger()
        self.decisionEngine=decisionEngine

    def decide(self,local,offloaded):
        return 1

    def cascadeTrainer(self):
        dB=cascadeDatabase()
        df=dB.getCascadeData()
        df=df[df['training']==1]
        df['CPU']=df['userCPU']+df['systemCPU']+df['idleCPU']
        cols=['runTime','batteryStartTime','latency','CPU']
        for col in cols:
            df[col]=(df[col]-df[col].min())/(df[col].max()-df[col].min())
        funcs=set(list(df['functionName']))
        for func in funcs:
            funcDf=df[df['functionName']==func]
            local=funcDf[funcDf['offloadStatus']==0]
            for idx,row in local.iterrows():
                offloaded=df[(df['offloadStatus']==1) & (df['inputTypes']==row['inputTypes']) & (df['inputValues']==row['inputValues'])\
                             & (df['dataSize']==row['dataSize'])]
                decision=self.decide(row,offloaded)
                dB.addTrainingEntry(row['functionName'],row['inputTypes'],row['inputValues'],decision,row['dataSize'],row['batteryStartTime'],\
                                    row['latency'])

        print(df)

    def train(self,func, inputs: list):
        self.decisionEngine.setTrainMode(True)
        if len(inputs)<1:
            self.log.error("The number of inputs is insufficient")
            raise Exception("Insufficient input to trainer")
        self.decisionEngine.setOffload(False)
        start=datetime.now()
        for i in inputs:
            func(*i)
        end=datetime.now()
        self.log.info("Local Training Complete. Training took: "+str((start-end).seconds)+" seconds.")
        self.decisionEngine.setOffload(True)
        start=datetime.now()
        for i in inputs:
            func(*i)
        end=datetime.now()
        self.decisionEngine.setTrainMode(False)
        self.log.info("Remote Training Complete. Training took: "+str((start-end).seconds)+" seconds.")

if __name__=='__main__':
    t=Trainer(1)
    precedence=[ProfilerConfig.RUNTIME, ProfilerConfig.ENERGY, ProfilerConfig.NETWORK]
    t.cascadeTrainer()
    print('end')