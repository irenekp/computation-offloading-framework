#framework: dice
from diceLibrary.settings import ProfilerEnum, DecisionEngineEnum
class DiceConfig:
    _profiler: list
    _decisionEngine: list
    _analytics: bool
    _logger: bool

    def setProfiler(self,settings: list):
        if not len(settings):
            #DICEY
            pass
        else:
            self._profiler=settings
            for setting in settings:
                if not ProfilerEnum.has_value(setting):
                    #DICEY
                    pass
    def getProfiler(self):
        return self._profiler

    def setDecisionEngine(self,settings: list):
        if not len(settings):
            #DICEY
            pass
        else:
            self._decisionEngine=settings
            for setting in settings:
                if not DecisionEngineEnum.has_value(setting):
                    #DICEY
                    pass

    def getDecisionEngine(self):
        return self._decisionEngine

    def enableAnalytics(self,setting: bool):
        #Enable analytics
        print('analytics'+str(setting))
        self._analytics=setting

    def getAnalyticSetting(self):
        return self._analytics

    def enableLogger(self, setting: bool):
        #Enable logger
        print('logger'+str(setting))
        self._logger=setting

    def getLoggerSetting(self):
        return self._logger

if __name__=='__main__':
    x=DiceConfig()
    x.setProfiler([ProfilerEnum.ENERGY, ProfilerEnum.NETWORK, ProfilerEnum.RUNTIME])
    x.setDecisionEngine([DecisionEngineEnum.CASCADE])
    x.enableAnalytics(True)
    x.enableLogger(True)
    #dice=Dice(x)