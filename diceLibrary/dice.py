from diceLibrary.profiler import Profiler
from diceLibrary.logger import Logger
from diceLibrary.settings import DecisionEngineConfig, AnalyticsConfig
from diceLibrary.cascadeDatabase import cascadeDatabase
from diceLibrary.analytics import Analytics
from diceLibrary.dispatcher import Dispatcher

class Dice:
    config=None
    profiler=None
    cascadeDB=None
    analytics=None
    log=None
    analyticsStatus=False
    singleRun=False
    dispatcher = None
    def __init__(self, config):
        self.config=config
        self.log=Logger(config.getLoggerConfig())
        self.profiler=Profiler(config.getProfilerConfig(), self.log)
        if config.getDecisionEngineConfig():
            if DecisionEngineConfig.CASCADE in config.getDecisionEngineConfig():
                self.cascadeDB=cascadeDatabase()
        self.analyticsStatus=config.isAnalyticsEnabled()
        if self.analyticsStatus:
            self.singleRun=AnalyticsConfig.CURRENTRUN in config.getAnalyticSetting()
            self.analytics=Analytics(self.config.getAnalyticSetting())
        self.dispatcher = Dispatcher("http://ec2-18-219-235-10.us-east-2.compute.amazonaws.com:8080/getNQueens", _inputArgs={"n":"9"})
        

    @staticmethod
    def offloadable(*args, **kwargs):
        def intermediateOffloadable(func):
            def runOffloadable(*args2, **kwargs2):
                dice=kwargs.get('dice',None)
                if dice:
                    dice.log.info('Beginning profiling process')
                    dice.profiler.startProfile()
                    func(*args2, **kwargs2)
                    #dice.dispatcher.offload_Val_Val()
                    dice.profiler.closeProfile()
                    runT,batteryT,latency,ping,upload,download,user,sys,idle =dice.profiler.getProfilerSummary()
                    if dice.cascadeDB:
                        id=dice.cascadeDB.addCascadeEntry(func.__name__,0,2000,runT,batteryT,latency,ping,upload,download,user,sys,idle)
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

    def analyze(self):
        profilerConfig = self.profiler.getUpdatedProfile()
        self.analytics.parseUpdatedConfig(profilerConfig)
        if self.analyticsStatus:
            data=self.cascadeDB.getCascadeData()
            self.analytics.analyze(data)

if __name__=='__main__':
    pass