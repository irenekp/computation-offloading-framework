from diceLibrary.profiler import Profiler
from diceLibrary.logger import Logger
from diceLibrary.settings import DecisionEngineConfig, AnalyticsConfig, InputType
from diceLibrary.cascadeDatabase import cascadeDatabase
from diceLibrary.analytics import Analytics
from diceLibrary.decisionEngine import DecisionEngine
from diceLibrary.trainer import Trainer
from diceLibrary.dispatcher import Dispatcher
import diceLibrary.app as analyticsApp
import os
import time

class Dice:
    config=None
    profiler=None
    cascadeDB=None
    analytics=None
    decisionEngine=None
    log=None
    analyticsStatus=False
    singleRun=False
    dispatcher = None
    trainer=None

    def __init__(self, config):
        self.config=config
        self.log=Logger(config.getLoggerConfig())
        self.profiler=Profiler(config.getProfilerConfig(), self.log)
        if config.getDecisionEngineConfig():
            self.cascadeDB=cascadeDatabase()
            self.decisionEngine=DecisionEngine(config.getDecisionEngineConfig())
        self.analyticsStatus=config.isAnalyticsEnabled()
        if self.analyticsStatus:
            self.singleRun=AnalyticsConfig.CURRENTRUN in config.getAnalyticSetting()
            self.analytics=Analytics(self.config.getAnalyticSetting())
        self.trainer=Trainer(self.decisionEngine)

    def analyze(self):
        profilerConfig = self.profiler.getUpdatedProfile()
        self.analytics.parseUpdatedConfig(profilerConfig)
        if self.analyticsStatus:
            data=self.cascadeDB.getCascadeData()
            self.analytics.analyze(data)
        analyticsApp.main()


    def train(self, main, inputs: list):
        self.trainer.train(main, inputs)
        self.trainer.cascadeTrainer()

    @staticmethod
    def createInputMetaData(metaData,*args,**kwargs):
        json={}
        idx=0
        for var in metaData.keys():
            val=kwargs.get(var,None)
            if val!=None:
                json[var]=str(val)
            else:
                json[var]=str(args[idx])
                idx=idx+1
        return json

    @staticmethod
    def getInputTypeAndValue(metaData, values):
        types = ''
        for key, val in metaData.items():
            if len(types) == 0:
                types = str(val.value)
            else:
                types = types + ', ' + str(val.value)

        ipvals = ''
        for key, val in values.items():
            if len(ipvals) == 0:
                ipvals = str(val)
            else:
                ipvals = ipvals + ', ' + str(val)

        return types, ipvals

    @staticmethod
    def getFileSize(filepath):
        return (os.path.getsize(filepath)/1000)

    def dispatch(self, dispatcher,json):
        self.dispatcher=dispatcher
        self.dispatcher.addInput(json)
        self.dispatcher.offload()


def offloadable(*args, **kwargs):
    def intermediateOffloadable(func):
        def runOffloadable(*args2, **kwargs2):
            dice=kwargs.get('dice',None)
            if dice:
                dice.log.info('Beginning profiling process')
                dice.profiler.startProfile()
                batteryS, upload, download = dice.profiler.getTrainingSummary()
                dispatcher=kwargs.get('dispatcher')
                metaData=dispatcher.getMetaData()
                values=Dice.createInputMetaData(metaData,*args2,**kwargs2)
                ipTypes, ipValues = Dice.getInputTypeAndValue(metaData, values)
                dataSize = 0
                for key, value in metaData.items():
                    if value == InputType.FILE:
                        dataSize = dataSize + Dice.getFileSize(dispatcher.getIpFilePath())
                #if not dice.profiler.checkInternet():
                    #offload = False
                offload=True if dice.decisionEngine.decide(ipTypes=ipTypes, ipValues=ipValues, dataSize=dataSize, batteryStartTime=batteryS, upload=upload, download=download,funcName=func.__name__)==True else False

                if(offload): #decisionEnginedecision
                    dice.dispatch(dispatcher,values)
                else:
                    func(*args2, **kwargs2)
                dice.profiler.closeProfile()
                runT,batteryS,batteryT,latency,ping,upload,download,user,sys,idle = dice.profiler.getProfilerSummary()
                if dice.cascadeDB:
                    id=dice.cascadeDB.addCascadeEntry(func.__name__,values,metaData,offload,dataSize,runT,batteryS,batteryT,\
                                                      latency,ping,upload,download,user,sys,idle, dice.decisionEngine.getTrainMode())
                    dice.log.info('Run time analytics for function '+func.__name__+' stored in CASCADE DB with runId:'+id)
                    if dice.analyticsStatus and dice.singleRun:
                        dice.analytics.addToAnalytics(id)
                        #dice.analyze()
                        dice.log.info("Graphs will be available at analytics page: http://localhost:8080/analyticsPage")
                    else:
                        dice.log.info('No graphs to be generated for: '+func.__name__)
                else:
                    dice.log.info('No information saved as cascade decision engine was not selected')
            else:
                #dice.log.error('Dice Instance Not Passed')
                raise Exception('Dice Instance Not Passed')
        return runOffloadable
    return intermediateOffloadable

if __name__=='__main__':
    pass