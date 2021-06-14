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
        if local['runTime'] is not None:
            rt=abs(local['runTime']-float(offloaded['runTime'].mean()))
        else:
            rt=0
        if local['batteryTime'] is not None:
            bt=abs(local['batteryTime']-float(offloaded['batteryTime'].mean()))
        else:
            bt=0
        if local['CPU'] is not None:
            ct=abs(local['CPU']-float(offloaded['CPU'].mean()))
        else:
            ct=0
        offloadVotes=0
        localVotes=0
        if local['runTime'] is not None:
            if local['runTime']>float(offloaded['runTime'].mean()):
                offloadVotes+=rt
            else:
                localVotes+=rt
        if local['batteryTime'] is not None:
            if local['batteryTime']>float(offloaded['batteryTime'].mean()):
                offloadVotes+=bt
            else:
                localVotes+=bt
        if local['CPU'] is not None:
            if local['CPU']>float(offloaded['CPU'].mean()):
                offloadVotes+=ct
            else:
                localVotes+=ct
        if localVotes>offloadVotes:
            return 0
        else:
            return 1

    def cascadeTrainer(self):
        dB=cascadeDatabase()
        df=dB.getCascadeData()
        df=df[df['training']==1]
        df['CPU']=df['userCPU']+df['systemCPU']+df['idleCPU']
        funcs=set(list(df['functionName']))
        for func in funcs:
            funcDf=df[df['functionName']==func]
            local=funcDf[funcDf['offloadStatus']==0]
            for idx,row in local.iterrows():
                offloaded=df[(df['offloadStatus']==1) & (df['inputTypes']==row['inputTypes']) & (df['inputValues']==row['inputValues'])\
                             & (df['dataSize']==row['dataSize'])]
                decision=self.decide(row,offloaded)
                dB.addTrainingEntry(row['functionName'],row['inputTypes'],row['inputValues'],decision,row['dataSize'],row['batteryStartTime'],\
                                    row['upload'], row['download'], row['runTime'])

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
    t.cascadeTrainer()
    print('end')