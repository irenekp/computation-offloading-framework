from diceLibrary.profiler import Profiler
from diceLibrary.logger import Logger
from diceLibrary.settings import DecisionEngineConfig, AnalyticsConfig
from diceLibrary.cascadeDatabase import cascadeDatabase
from diceLibrary.analytics import Analytics
from diceLibrary.decisionEngine import DecisionEngine
from diceLibrary.trainer import Trainer
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

    def train(self, main, inputs: list):
        self.trainer.train(main, inputs)

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

                dispatcher=kwargs.get('dispatcher')
                metaData=dispatcher.getMetaData()
                values=Dice.createInputMetaData(metaData,*args2,**kwargs2)
                offload=True if dice.decisionEngine.decide()==True else False
                if(dice.decisionEngine.decide() == 1): #decisionEnginedecision
                    dice.dispatch(dispatcher,values)
                else:
                    func(*args2, **kwargs2)
                dice.profiler.closeProfile()
                runT,batteryS,batteryT,latency,ping,upload,download,user,sys,idle = dice.profiler.getProfilerSummary()
                if dice.cascadeDB:
                    id=dice.cascadeDB.addCascadeEntry(func.__name__,values,metaData,offload,2000,runT,batteryS,batteryT,\
                                                      latency,ping,upload,download,user,sys,idle, dice.decisionEngine.getTrainMode())
                    dice.log.info('Run time analytics for function '+func.__name__+' stored in CASCADE DB with runId:'+id)
                    if dice.analyticsStatus and dice.singleRun:
                        dice.analytics.addToAnalytics(id)
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