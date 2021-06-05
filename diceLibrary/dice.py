from diceLibrary.profiler import Profiler
from diceLibrary.logger import Logger
from diceLibrary.settings import DecisionEngineConfig, AnalyticsConfig
from diceLibrary.cascadeDatabase import cascadeDatabase
from diceLibrary.analytics import Analytics
class Dice:
    config=None
    profiler=None
    cascadeDB=None
    analytics=None
    log=None
    analyticsStatus=False
    singleRun=False
    def __init__(self, config):
        self.config=config
        self.log=Logger(config.getLoggerConfig())
        self.profiler=Profiler(config.getProfilerConfig(), self.log)
        if config.getDecisionEngineConfig():
            if DecisionEngineConfig.CASCADE in config.getDecisionEngineConfig():
                self.cascadeDB=cascadeDatabase()
        self.analyticsStatus=config.isAnalyticsEnabled()
        if self.analyticsStatus:
            self.singleRun=AnalyticsConfig.CURRENTRUN in config.getAnalyticsSetting()
            self.analytics=Analytics(self.config.getAnalyticsSetting(),self.config.getProfilerConfig())

    @staticmethod
    def offloadable(*args, **kwargs):
        def intermediateOffloadable(func):
            def runOffloadable(*args2, **kwargs2):
                dice=kwargs.get('dice',None)
                if dice:
                    dice.log.info('Beginning profiling process')
                    dice.profiler.startProfile()
                    func(*args2, **kwargs2)
                    dice.profiler.closeProfile()
                    runT,batteryT,latency,ping,upload,download,user,sys, \
                    idle,interrupt,dpc=dice.profiler.getProfilerSummary()
                    if dice.cascadeDB:
                        id=dice.cascadeDB.addCascadeEntry(func.__name__,0,2000,runT,batteryT,latency,ping,upload,download,user,sys, \
                                                       idle,interrupt,dpc)
                        dice.log.info('Run time analytics for function '+func.__name__+' stored in CASCADE DB with runId:'+id)
                        if dice.analyticsStatus and dice.singleRun:
                            dice.analytics.addToAnalytics(id)
                        else:
                            dice.log.info('No graphs to be generated for: '+func.__name__)
                    else:
                        dice.log.info('No information saved as cascade decision engine was not selected')
                else:
                    dice.log.error('Dice Instance Not Passed')
                    raise Exception('Dice Instance Not Passed')
            return runOffloadable
        return intermediateOffloadable

    def analyze(self):
        if self.analyticsStatus:
            data=self.cascadeDB.getCascadeData()
            self.analytics.analyze(data)

if __name__=='__main__':
    pass